
import json
import requests
import subprocess

import urllib.error as error
from urllib.error import HTTPError

from owslib.wfs import WebFeatureService
from cjio import cityjson as cj

from shapely.geometry import Polygon as ShapelyPolygon
from shapely.ops import unary_union

import config.global_config as global_config
import models.logging_model as logging_model


CITYJSON_URL = "https://data.3dbag.nl/v20240420/tiles/{TID}/{ad_TID}.city.json"
WFS_URL = "https://data.3dbag.nl/api/BAG3D/wfs?request=getcapabilities"
WFS_LAYER = "BAG3D:Tiles"

maximum_amount_tiles = 10

def get_bag_tile_ids(bbox, show_debug: bool = False):
    """Gets tile IDS from WFS based on a specified bounding box. 

    Args:
        wfs_url (_type_): The URL for the WFS GetCapabilities service.
        wfs_layer (_type_): The WFS layer that needs to be accessed.
        bbox (_type_): The bounding box in which to look for the tiles.

    Returns:
        tile_ids ([str]): List of strings of pulled tile numbers in the format x/xxx/xxx.
    """
    wfs11 = WebFeatureService(url=WFS_URL, version='1.1.0')
	
    try:
        response = wfs11.getfeature(typename=WFS_LAYER, bbox=bbox, srsname='urn:x-ogc:def:crs:EPSG:28992', outputFormat='json')
        tiles = json.loads( response.read().decode('utf-8') )['features']
        tile_ids = [ tile['properties']['tile_id'] for tile in tiles ]
    except error.HTTPError as err:
        print(err)
        return None
    if show_debug:    
        print("\n")    
        print("|-----> TILE IDS: ")
        print(f" |---> Total amount of tiles: {len(tile_ids)}")
    
        for i, tile in enumerate(tile_ids):
            print(f"   |--> {i}: {tile} ")
        
    return tile_ids

def download_bag_tiles(tile_ids,show_debug: bool = False):
    """Downloads 3DBAG tiles from the WFS service

    Args:
        tile_ids ([str]): a list of strings in the format of x/xxx/xxx corresponding with the tile numbers that need to be downloaded.

    Returns:
        fnames ([str]): List of paths for the downloaded files.
    """
    
    fnames = []
    
    for tid in tile_ids:
        ad_tid = tid.replace("/", "-")
        url = CITYJSON_URL.format(TID=tid, ad_TID=ad_tid)
            
        fname = global_config.project_tiles_path + (ad_tid + '.city.json')
               
        try:
            with requests.get(url) as response, open(fname, "wb") as file:
                data = response.content
                file.write(data)
                fnames.append(fname)
                     
        except HTTPError as err:
            print(err)
        
    if show_debug:
        print("\n") 
        print("|-----> NR OF CITYOBJECTS: ")
        total_amount = 0
    
        for i, fname in enumerate(fnames):
            _cm = cj.load(fname)
            print(f"   |--> {i}: {len(_cm.j['CityObjects'])}")
            total_amount += len(_cm.j['CityObjects'])
        
        print(f"        |--> TOTAL NR OF CITYOBJECTS IN TILES: {total_amount}")
        print("\n")  
          
    return fnames

def merge_tiles(fnames, save_debug_file: bool=False):
    """Merges CityJSON tiles together with transformation

    Args:
        tile_ids ([str]): a list of paths as strings to the CityJSON tiles to be merged

    Returns:
        cm (CityJSON Object): A CityJSON object containing the merged tile.
    """
    
    cms = []

    cm = cj.load(fnames[0], transform=False)
    
    for i, f in enumerate(fnames):
        _cm = cj.load(f, transform=False)
        cms.append(_cm)
        
    cm.merge(cms)
    cm.load_from_j()
    if save_debug_file:
        cj.save(cm, global_config.project_generate_path + "merged_cm.city.json")
        print(f"         |----> File for debugging saved at {global_config.project_generate_path + "merged_cm.city.json"}")  
    
    print("|-------->> Merge succesfull!")
    return cm

def intersect_cm_with_aoi(cm, aoi_poly, save_path, save_debug_file: bool=False) :
    """Intersecting an CityJSON tile with the original WKT Polygon to cut out unnecessary parts. 

    Args:
        cm (CityJSON Object): CityJSON object that needs to be intersected with.
        aoi_poly (WKT Polygon): The WKT polygon that defines the area of interest.

    Returns:
        aoi_cm(CityJSON Object): an CityJSON object cut according to the input WKT polygon. 
    """
    aoi_cm = cj.CityJSON()

    buildings = cm.get_cityobjects(type="building")
    for co_id, co in buildings.items():
        for geom in co.geometry:
            if str(geom.lod) == "0":
                fp_poly = unary_union([ShapelyPolygon(ring)
                                    for surface in geom.boundaries
                                    for ring in surface])
                if fp_poly.intersects(aoi_poly):
                    aoi_cm.set_cityobjects({co_id: co})
                    # also add its children
                    if len(co.children) > 0:
                        ch = cm.get_cityobjects(id=co.children)
                        aoi_cm.set_cityobjects(ch)
    aoi_cm.add_to_j()
    aoi_cm.update_bbox()
    aoi_cm.set_epsg(7415)
        
    if save_debug_file:
        cj.save(aoi_cm, global_config.project_generate_path + "intersected_cm.city.json")
        print(f"         |----> File for debugging saved at {global_config.project_generate_path + "intersected_cm.city.json"}")
        print(f"         |----> total amount of buildings left in the intersected tile: {len(aoi_cm.j["CityObjects"])}")   
    
    print("|-------->> Intersection with area of interest succesfull!")
   
    return aoi_cm


def check_amount_tiles(tile_ids, bypass: bool=False):
    if bypass == False:
        if len(tile_ids) == 0:
            print("No tile ids were found for the specified area of interest. Please adjust your selection.")
            return False
        
        if len(tile_ids) > maximum_amount_tiles:
            print(f"You have selected more than {maximum_amount_tiles} tiles! For performance reasons this is not advised and currently not allowed! Check with the developer if you think you nneed it anyway.")
            return False
        return True
    else:
        return True
    
def extract_lod_from_cm(lod, cm, save_debug_file: bool=False):
    
    cm.extract_lod(lod)
    
    if save_debug_file:
        cj.save(cm, global_config.project_generate_path + f"lodextracted={lod}_cm.city.json", addtojEnabled=False)
        print(f"CityJSON object saved to {global_config.project_generate_path + f"lodextracted={lod}_cm.city.json"}")
        
    return cm

# Construct the command to run Blender with the script and arguments
def create_blender_file(lod):
    command = [
        global_config.blender_exe,
        '--background',
        '--python', global_config.blender_script,
        '--',  # Separator for Blender arguments and script arguments
        global_config.project_name, global_config.projects_folder, lod
    ]

    # Execute the command
    subprocess.run(command)
    