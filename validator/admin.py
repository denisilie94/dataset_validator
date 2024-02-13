import json

from tqdm import tqdm

from django.db import models
from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django_json_widget.widgets import JSONEditorWidget

from .models import Language, Dataset, DatasetLanguage, JsonObject


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.action(description='Import JSON objects from file')
def import_json_objects(modeladmin, request, queryset):
    for dataset_language in queryset:
        try:
        	# Read the JSON file
	        with dataset_language.file.open('r') as file:
	            json_objects = json.load(file)

	        if isinstance(json_objects, list):
	            if dataset_language.dataset_language_source:
	                json_objects_source = JsonObject.objects.filter(
	                    dataset_language=dataset_language.dataset_language_source
	                ).order_by('order_id')

	                if len(json_objects) != len(json_objects_source):
	                    raise ValidationError("The number of JSON objects does not correspond.")

	                for order_id, (json_object, json_object_source) in tqdm(enumerate(zip(json_objects, json_objects_source))):
	                    if order_id != json_object_source.order_id:
	                        raise ValidationError("The order_id values do not correspond.")

	                    # Create a JsonObject instance
	                    JsonObject.objects.create(
	                        dataset_language=dataset_language,
	                        json_object=json_object,
	                        json_object_source=json_object_source,
	                        order_id=order_id,
	                        is_valid=False,
	                    )
	            else:
	                for order_id, json_object in tqdm(enumerate(json_objects)):
	                    # Create a JsonObject instance
	                    JsonObject.objects.create(
	                        dataset_language=dataset_language,
	                        json_object=json_object,
	                        json_object_source=None,
	                        order_id=order_id,
	                        is_valid=True,
	                    )

	            dataset_language.imported = True
	            dataset_language.save()
	        else:
	            raise ValidationError("The file does not contain a JSON array.")

        except json.JSONDecodeError:
            modeladmin.message_user(request, f"Invalid JSON in file: {dataset_language.file.name}", level='error')
        except Exception as e:
            modeladmin.message_user(request, f"Error processing file: {dataset_language.file.name} - {e}", level='error')


@admin.action(description='Export Dataset Language to JSON file')
def export_json_objects(modeladmin, request, queryset):
    # Ensure only one dataset is selected
    if queryset.count() != 1:
        messages.error(request, "Please select only one dataset for export.")
        return

    dataset_language = queryset.first()
    exported_data = []

    # For the selected DatasetLanguage, find all related JsonObjects
    json_objects = dataset_language.json_objects.all()

    for json_object in json_objects:
        # Serialize each JsonObject into a dictionary
        json_fields = json_object.json_fields.all()
        json_data = {field.key.name: field.value for field in json_fields}
        exported_data.append(json_data)

    # Convert the dictionary to a JSON string
    json_string = json.dumps(exported_data, indent=4, ensure_ascii=False)

    # Create an HttpResponse with a JSON file
    response = HttpResponse(json_string, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{dataset_language.dataset.name}_{dataset_language.language.code}.json"'

    return response


@admin.register(DatasetLanguage)
class DatasetLanguageAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'language', 'file', 'imported')
    search_fields = ('dataset__name', 'language__name')
    list_filter = ('dataset', 'language')
    actions = [import_json_objects, export_json_objects]

	
@admin.register(JsonObject)
class JsonObjectAdmin(admin.ModelAdmin):
	list_display = ('id', 'order_id', 'dataset_language', 'is_valid')
	fields = ('id', 'order_id', 'dataset_language', 'is_valid', 'json_object', 'get_json_object_source_json_object')
	readonly_fields = ('id', 'order_id', 'dataset_language', 'get_json_object_source_json_object')
	search_fields = ('id', 'order_id')
	list_filter = ('dataset_language__dataset', 'dataset_language__language')
	formfield_overrides = {
		models.JSONField: {'widget': JSONEditorWidget},
	}

	def get_json_object_source_json_object(self, obj):
	    if obj.json_object_source:
	        # Convert the JSON object to a formatted string
	        json_pretty_str = json.dumps(obj.json_object_source.json_object, indent=2)
	        return json_pretty_str
	    return 'N/A'
	get_json_object_source_json_object.short_description = 'JSON Object Source'

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return True
