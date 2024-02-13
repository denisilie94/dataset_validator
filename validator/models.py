from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DatasetLanguage(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset_languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='dataset_languages')
    file = models.FileField(upload_to='datasets/', validators=[FileExtensionValidator(allowed_extensions=['json'])])
    dataset_language_source = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = ('dataset', 'language')
        indexes = [
            models.Index(fields=['dataset', 'language']),
        ]

    def __str__(self):
        return f"{self.dataset.name} - {self.language.name}"


@receiver(post_delete, sender=DatasetLanguage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


def json_object_default():
	return {}


class JsonObject(models.Model):
    dataset_language = models.ForeignKey(DatasetLanguage, on_delete=models.CASCADE, related_name='json_objects')
    json_object = models.JSONField("JsonObject", default=json_object_default)
    json_object_source = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.IntegerField()
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"JSON object for {self.dataset_language}"
