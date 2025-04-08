import os
import sys
import datetime as dt
import random
import string
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models.enums_model as e
import models.logging_model as logging
import models.bag_model as bag
import models.ahn_model as ahn
import config.global_config as g_config
import utilities as ut

#CURRENT PROJECT
class Project:
    def __init__(self, project_name, lod=e.Lod.HIGH):
        #create a logger model associated with this project
        self.logger = logging.LogHandler(os.path.join(project_name + ".log.txt"))
        #Set Project Settings
        #-->Generate the unique projectname 
        self.randomcode = ''.join(random.choices(string.ascii_letters, k=6))
        self.project_name = project_name + "_" + self.randomcode
        #-->Set Date
        self.creation_date = dt.datetime.now()
        #-->Set project status (set to Not Started by default)
        self.status = e.Status.NOT_STARTED.value
        #-->Set LOD that we are working with (set to 2.2 by default)
        self.lod = lod.value
        
        #Set  output path for files
        self.path = os.path.join(g_config.PROJECTS_BASE_PATH, self.project_name)
        #Set the wkt polygon
        self.wkt_polygon = ut.create_wkt_from_coordinates(g_config.aoi)
        
      
        #Create a BAGHandler class instance associated with this project
        self.BAGHandler = bag.BAGHandler(self.path, self.logger, self.wkt_polygon, self.lod)    
        #create a AHNHandler class instance associated with this project
        self.AHNHandler = ahn.AHNHandler(self.path, self.wkt_polygon)
                     
        self.logger.log_message("info", f"|| Project succesfully created", True, True, True)
    
    def createProjectFolders(self):
        #Create and change directory to create subfolders
        os.mkdir(self.path)
        os.chdir(self.path)
        try:
            subfolders = ["3D_BAG", "AHN", "3D_Models", "Blender"]
            for folder in subfolders:
                os.mkdir(os.path.join(self.path, folder))
        except Exception as e:
            self.logger.log_message("error", f"|| Something went wrong when creating the subfolders {e}", True, True, True)
         
    def __repr__(self):
        return (
            f"Project Details:\n"
            f"Name: {self.project_name}\n"
            f"Random code: {self.randomcode}\n"
            f"Status: {self.status}\n"
            f"Path: {self.path}\n"
            f"Level of Detail (LOD): {self.lod}\n"
            f"Creation Date: {self.creation_date}\n"
        )
    
    
project = Project("Amersfoort", e.Lod.HIGH)
project.createProjectFolders()
project.BAGHandler.load_bag()
