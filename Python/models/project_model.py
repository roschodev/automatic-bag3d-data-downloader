import os
import sys
import datetime as dt
import random
import string
from shapely.geometry import Polygon
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models.enums_model as e
import models.logging_model as logging_model
import config.global_config as global_config




project_tasks_general = ["Check projectname", "Check LOD", "Check if project folder exists", "Create project folder", "Create subfolders"]
project_tasks_3dbag = ["Confirm Avalaibility", "Get Tile IDS", "Download Relevant tiles", "Merge tiles", "Convert to 3D-Data", "Return to User"]
project_tasks_ahn = ["Unknown","Unknown"]

project_tasks = project_tasks_general + project_tasks_3dbag + project_tasks_ahn

#CURRENT PROJECT
class Project:
    def __init__(self, project_name, lod=e.Lod.HIGH):
        self.randomcode = ''.join(random.choices(string.ascii_letters, k=6))
        self.project_name = project_name + "_" + self.randomcode
        self.wkt_polygon = self.create_wkt_from_coordinates(global_config.aoi)
        self.creation_date = dt.datetime.now()
        self.path = os.path.join(global_config.PROJECTS_BASE_PATH, self.project_name)
        os.mkdir(self.path)
        os.chdir(self.path)
        self.status = e.Status.NOT_STARTED.value
        self.tasks = project_tasks
        self.lod = lod.value
        self.logger = logging_model.LogHandler(os.path.join(project_name + ".log.txt"))
        self.generate_subfolders()
        self.logger.log_message("info", f"|| Project succesfully created", True, True, True)
        

            
    def __repr__(self):
        return (f"Project Details:\n"
                f"Name: {self.project_name}\n"
                f"Status: {self.status}\n"
                f"Path: {self.path}\n"
                f"Level of Detail (LOD): {self.lod}\n"
                f"Creation Date: {self.creation_date}\n"
                f"Tasks left: {self.tasks}\n")

    def create_wkt_from_coordinates(self, aoi):
        def convert_to_wkt(aoi):
            nw_coord = aoi["nw_coord"]
            se_coord = aoi["se_coord"]
            polygon = Polygon([
                (nw_coord[0], nw_coord[1]), 
                (se_coord[0], nw_coord[1]),  
                (se_coord[0], se_coord[1]),  
                (nw_coord[0], se_coord[1]),  
                (nw_coord[0], nw_coord[1])   
            ])
            aoi_poly = polygon
            return aoi_poly

        wkt_polygon = convert_to_wkt(aoi)
        return wkt_polygon
    
    def generate_subfolders(self):
        try:
            subfolders = ["3D_BAG", "AHN", "3D_Models", "Blender"]
            for folder in subfolders:
                os.mkdir(os.path.join(self.path, folder))
        except Exception as e:
            self.logger.log_message("error", f"|| Something went wrong when creating the subfolders {e}", True, True, True)



