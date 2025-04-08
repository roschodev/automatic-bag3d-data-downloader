
import config.global_config as g_config
import import_cityjson_blender as importblender
import subprocess
from shapely.geometry import Polygon
import os

def run_blender(projectname, path, lod):
    script_path = os.path.abspath(importblender.__file__)
    command = [
        g_config.BLENDER_EXE,
        '--background',
        '--python', script_path,
        '--',  # Separator for Blender arguments and script arguments
        projectname, path, lod
    ]

    # Execute the command
    subprocess.run(command)
    
def create_wkt_from_coordinates(aoi):
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
    
def calculate_aspectratio(bounds):
        #alter the image size based on the bounds

        bbox_width = bounds[2] - bounds[0] 
        bbox_height = bounds[3] - bounds[1]

        aspect_ratio = bbox_width / bbox_height
        
        if aspect_ratio > 1:  # Landscape
            image_width = g_config.max_image_size
            image_height = int(g_config.max_image_size / aspect_ratio)
        else:  # Portrait or square
            image_height = g_config.max_image_size
            image_width = int(g_config.max_image_size * aspect_ratio)
            
        return (image_width * g_config.resolution.multiplier, image_height * g_config.resolution.multiplier)    