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

#AHN SETTINGS
AHN_URL = "https://service.pdok.nl/rws/ahn/wms/v1_0?service=WMS&version=1.3.0&request=GetMap&layers=dtm_05m&styles=default&crs=EPSG:28992&bbox=1.98603,50.695,7.81981,55.7062&width=500&height=500&format=image/png"
WMS_URL = ""
WMS_LAYER = "dtm_05m"

MAX_IMAGE_SIZE = 2000

#BLENDER
BLENDER_EXE = "C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"
BLENDER_SCRIPT = ""


#USEFULL COMMANDS

#Empty Projects folder
#Remove-Item "E:\Projects\Coding\git-automatic-bag3d-data-downloader\projects\*" -Recurse -Force


aoi = {
    'nw_coord': [141509.1966788704, 455361.4163170283],
    'se_coord': [142874.55721519803, 453132.7088395531]
}