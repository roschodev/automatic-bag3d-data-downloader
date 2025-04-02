import os
import sys
import json
import requests
import traceback
import cjio

from owslib.wfs import WebFeatureService

import urllib.error as error
from urllib.error import HTTPError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import models.enums_model as e
import config.global_config as global_config
import models.project_model as project_model

class BAGHandler:
    def __init__(self, currentProject: project_model.Project):
        self.bag = None
        self.currentProject = currentProject
        self.WFS_URL = global_config.WFS_URL
        self.WFS_LAYER = global_config.WFS_LAYER
        self.WFS_VERSION = global_config.WFS_VERSION
        self.CITYJSON_URL = global_config.CITYJSON_URL
        self.maximum_amount_tiles = global_config.maximum_amount_tiles
        self.path = os.path.join(currentProject.path, "3D_BAG")
        self.currentProject.logger.log_message("info", "|| BAGHandler succesfully created.\n", True, True, True)

    def load_bag(self):
            tile_ids = self.get_tile_ids(self.currentProject.wkt_polygon.bounds)
            bag_tiles = self.download_bag_tiles(tile_ids)
           
            
    def __repr__(self):
        return (f"BAGHandler Details:\n"
                f"Path: {self.path}\n"
                f"Maximum amount of tiles: {self.maximum_amount_tiles}\n"
                f"WFS URL: {self.WFS_URL}\n"
                f"WFS Version: {self.WFS_VERSION}\n"
                f"WFS Layer: {self.WFS_LAYER}\n"
                f"CityJSON URL: {self.CITYJSON_URL}\n")
    
    def get_tile_ids(self, bbox):
        wfs11 = WebFeatureService(url=self.WFS_URL, version=self.WFS_VERSION)

        try:
            self.currentProject.logger.log_message("info", "|| ............FETCHING TILE IDS............", True, True, True)
            response = wfs11.getfeature(typename=global_config.WFS_LAYER, bbox=bbox, srsname='urn:x-ogc:def:crs:EPSG:28992', outputFormat='json')
            tiles = json.loads( response.read().decode('utf-8') )['features']

            #check if the amount of tiles is within the limit
            if len(tiles) > self.maximum_amount_tiles:
                self.currentProject.logger.log_message("error", "Maximum amount of tiles exceeded.", True, True, True, )
                return None
            elif(len(tiles) == 0):
                self.currentProject.logger.log_message("error", "No Tiles in selection.", True, True, True, )
                return None

            tile_ids = []
           
            for tile in tiles:
                try:
                    tile_id = tile['properties']['tile_id']
                    tile_ids.append(tile_id)
                    self.currentProject.logger.log_message("info","    ----> " + tile_id, True, True, False)
                except KeyError:
                    self.currentProject.logger.log_message("warning", "Tile without tile_id found", True, True, False)
                
            self.currentProject.logger.log_message("info", f"|| ............FETCHING TILE IDS SUCCESFULL {len(tile_ids)}............\n", True, True, True)
            return tile_ids
                    
        except error.HTTPError as e:
            self.currentProject.logger.log_message("info", f"|| Fetching Tile IDs failed: {e}. \n", True, True, False)
            return None
        
        
    def download_bag_tiles(self, tile_ids):
   
        bag_tiles = []
        try:
            self.currentProject.logger.log_message("info", "|| ............DOWNLOADING TILES FROM BAG SERVICE............", True, True, True)
            for tile_id in tile_ids:
                adjusted_tile_id = tile_id.replace("/", "-")
                url = global_config.CITYJSON_URL.format(TID=tile_id, ad_TID=adjusted_tile_id)
                fname = os.path.join(self.path, (adjusted_tile_id + '.city.json'))
                try:
                    with requests.get(url) as response, open(fname, "wb") as file:
                        data = response.content
                        file.write(data)
                        bag_tiles.append(fname)
                            
                except HTTPError as e:
                    self.currentProject.logger.log_message("error", f"|| An error occured during downloading of BAG tiles: {e}.", True, True, True,)
                    return None
                
                for i, tile in enumerate(bag_tiles):
                    cityjson_tile = cjio.load(tile)
                    print(f"   |--> {i}: {len(cityjson_tile.j['CityObjects'])}")
                    total_cityObjects += len(cityjson_tile.j['CityObjects'])
                
            self.currentProject.logger.log_message("info", f"|| ............DOWNLOADING TILES FROM BAG SERVICE SUCCESFULL (nr. of tiles: {len(bag_tiles)}, nr. of CityObjects{total_cityObjects}:)............\n", True, True, True)
            return bag_tiles
        except Exception as e:
           
            traceback_str = traceback.format_exc()
            

            self.currentProject.logger.log_message("error", f"|| An error occurred during downloading of BAG tiles: {traceback_str}", True, True, True)
            return None

       
    def merge_tiles():
        pass
    def intersect_with_aoi():
        pass
    def convert_to_3d_data():
        pass
    def return_to_user():
        pass


project = project_model.Project("Amersfoort", e.Lod.HIGH)
bagHandler = BAGHandler(project)
bagHandler.load_bag()