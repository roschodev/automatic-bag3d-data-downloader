import os
import datetime as dt



#GENERAL INFORMATION
APP_INFO = {
    "version": "1.0",
    "author": "Roscho.dev",
    "description": "3D BAG downloader",
    "tech-stack": "Python 3.8, requests, CityJSON, Flask, Javascript, HTML, CSS",
    }


#PATHS
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS_BASE_PATH = os.path.join(BASE_PATH, "projects")

#GLOBAL SETTINGS
show_debug = False



#USEFULL COMMANDS

#Empty Projects folder
#Remove-Item "E:\Projects\Coding\git-automatic-bag3d-data-downloader\projects\*" -Recurse -Force


