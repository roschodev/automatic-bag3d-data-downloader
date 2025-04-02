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
maximum_amount_tiles = 15


#BAG SETTINGS
CITYJSON_URL = "https://data.3dbag.nl/v20240420/tiles/{TID}/{ad_TID}.city.json"
WFS_URL = "https://data.3dbag.nl/api/BAG3D/wfs?request=getcapabilities"
WFS_VERSION = "1.1.0"
WFS_LAYER = "BAG3D:Tiles"


#USEFULL COMMANDS

#Empty Projects folder
#Remove-Item "E:\Projects\Coding\git-automatic-bag3d-data-downloader\projects\*" -Recurse -Force


