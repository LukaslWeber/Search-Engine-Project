# Search-Engine
 Our Proposal for the "Modern Search Engines" Group project

## Creators:
 - Lukas Weber
 - Dana Rapp
 - Simon Frank
 - Maximilian Jaques

## Installation guide
We have used Python 3.9 for this proejct. <br>
<br>
To install required libraries, run the following command: pip install -r requirements.txt. If this does not succeed for you, you can alternatively install it with PyCharm. <br>
<br>
To be able to open the TüBing web page, you need to be able to run the project as a Django project. <br>
We created the project using PyCharm so we advise you to do it with PyCharm. <br>
Once you have opened the Project with PyCharm, enable the Django support with: File (on Windows) or PyCharm (on Mac) -> Settings -> Languages & Frameworks -> Django -> Enable Django Support
<br>
Set the Django Project root to the Project folder and point the "settings" to the "settings.py" which is in the "SearchEngine" folder. Also point the "Manage script" to the "manage.py" which also lies in the main folder. In our cases, it was sufficient to set settings as "SearchEngine\settings.py" and Manage script als "manage.py". <br>
You should then be able to create a Django run configuration with the type Django Server and your Python environment. 
In our case, Environment variables were: "PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=SearchEngine.settings"
<br><br>
If no folder called "media" exists in the project, please create it. Furhtermore if no folder called "results" is in "data_files", please also create it.

## Create Index

To create the index just run `python FocusedWebCrawler.py -n`\
To restart the crawler run `python FocusedWebCrawler.py -r`, therefore already some files must be stored in the *data_files* folder.
