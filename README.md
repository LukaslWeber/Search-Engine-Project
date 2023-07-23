# Search-Engine
 Our Proposal for the "Modern Search Engines" Group project

## Creators:
 - Lukas Weber
 - Dana Rapp
 - Simon Frank
 - Maximilian Jaques

## Installation guide
We have used Python 3.9 for this proejct. <br>
To install required libraries, run the following command: pip install -r requirements.txt <br>
To be able to open the web page, you need to be able to run the project  as a Django project. <br>
We created the project using PyCharm so we know how to do it with that interpreter.
Once you have opened the Project with PyCharm: File (on Windows) or PyCharm (on Mac) -> Settings -> Languages & Frameworks -> Django -> Enable Django Support
Set the Django Project root to the Project folder and point the "settings" to the "settings.py" which is in the "SearchEngine" folder. Also point the "Manage script" to the "manage.py" which also lies in the main folder. In our cases, it was sufficient to set settings as "SearchEngine\settings.py" and Manage script als "manage.py".
You should then be able to create a Django run configuration with the type Django Server. 
In our case, Environment variables were: "PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=SearchEngine.settings"

## Create Index

To create the index just run `python FocusedWebCrawler.py -n`\
To restart the crawler run `python FocusedWebCrawler.py -r`, therefore already some files must be stored in the *data_files* folder.
