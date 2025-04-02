import models.project_model as p
import models.enums_model as e
import os

def create_new_project(project_name, lod=e.Lod.HIGH, writeLogFile: bool=True):
    try:
        current_project = p.Project(project_name, lod)
        
        def generate_subfolders():
            subfolders = ["3D_BAG", "AHN", "3D_Models", "Blender"]
            for folder in subfolders:
                os.mkdir(os.path.join(current_project.path, folder))

        generate_subfolders()
        current_project.logger.log_message("info", "Project created successfully.", True, writeLogFile)
        return current_project
    
    except Exception as e:
            current_project.logger(f"An error occurred while creating the project: {e}", True, writeLogFile)


create_new_project("Amersfoort", e.Lod.HIGH, True)