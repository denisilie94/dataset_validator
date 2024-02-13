# dataset_validator

This Django application is designed to validate translated datasets in JSON format.
The primary use of this application is through the admin panel. Here are the steps to set up and use the application:

## Setup

1. Clone the repository and navigate to the project directory.

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Run the following Django management commands to set up the database:

   ```
   python manage.py makemigrations
   python manage.py makemigrations translator
   python manage.py migrate
   ```

4. Create a superuser to access the admin panel:

   ```
   python manage.py createsuperuser
   ```

## Usage

1. Access the admin panel by visiting `http://localhost:8000/admin/` and log in with the superuser credentials created earlier.

2. In the admin panel, ensure that you have the following configured:

   - **Languages**: Add the languages you will be working with (e.g., English and Romanian).

3. Create a new `DatasetLanguage` in the admin panel. For example, you can create a dataset named "alpaca_data" with the source language set to English and provide the corresponding JSON file.

4. After creating the `DatasetLanguage` object, use the custom admin action "Import JSON objects from file" to import the JSON data into the database. Depending on the file's size, this process may take some time. For validating a dataset you need at least two uploaded. The original one and the translated one. In the media folder we provide 2 short examples for the aplaca_dataset.

5. Validate the datasets using the admin panel provided by Django.

6. Once the validation is completed, you can export the new dataset using the admin custom action "Export Dataset Language to JSON file" from the "Dataset Language" section in the admin panel.

Feel free to customize the application and add additional custom translators in the `task.py` file to suit your needs.
