import os
import sys
import json
import requests
import traceback
from cjio import cityjson as cj

from owslib.wfs import WebFeatureService

import urllib.error as error
from urllib.error import HTTPError

from shapely.geometry import Polygon as ShapelyPolygon
from shapely.ops import unary_union

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config.global_config as global_config

class BAGHandler:
    def __init__(self, path, logger, wkt_polygon, lod):
        self.bag = None
        self.wkt_polygon = wkt_polygon
        self.lod = lod
        self.logger = logger
        self.WFS_URL = global_config.WFS_URL
        self.WFS_LAYER = global_config.WFS_LAYER
        self.WFS_VERSION = global_config.WFS_VERSION
        self.CITYJSON_URL = global_config.CITYJSON_URL
        self.maximum_amount_tiles = global_config.maximum_amount_tiles
        self.path = os.path.join(path, "3D_BAG")
        self.logger.log_message("info", "---->> BAGHandler succesfully created", True, True, True)
                
    def __repr__(self):
        return (f"BAGHandler Details:\n"
                f"Path: {self.path}\n"
                f"Maximum amount of tiles: {self.maximum_amount_tiles}\n"
                f"WFS URL: {self.WFS_URL}\n"
                f"WFS Version: {self.WFS_VERSION}\n"
                f"WFS Layer: {self.WFS_LAYER}\n"
                f"CityJSON URL: {self.CITYJSON_URL}\n")
        
    def load_bag(self):
            tile_ids = self.get_tile_ids(self.wkt_polygon.bounds)
            bag_tiles = self.download_tiles(tile_ids)
            merged_tile = self.merge_tiles(bag_tiles)
            self.logger.log_message("info", f"|| Extracting only objects matching the LOD type: {self.lod}", True, True, True)
            merged_tile.extract_lod(self.lod)
            intersected_tile = self.intersect_cm_with_aoi(merged_tile, self.wkt_polygon)    
    
    def get_tile_ids(self, bbox):
        wfs11 = WebFeatureService(url=self.WFS_URL, version=self.WFS_VERSION)

        try:
            self.logger.log_message("info", "|| ............FETCHING TILE IDS............", True, True, True)
            response = wfs11.getfeature(typename=global_config.WFS_LAYER, bbox=bbox, srsname='urn:x-ogc:def:crs:EPSG:28992', outputFormat='json')
            tiles = json.loads( response.read().decode('utf-8') )['features']

            #check if the amount of tiles is within the limit
            if len(tiles) > self.maximum_amount_tiles:
                self.logger.log_message("error", "Maximum amount of tiles exceeded.", True, True, True, )
                return None
            elif(len(tiles) == 0):
                self.logger.log_message("error", "No Tiles in selection.", True, True, True, )
                return None

            tile_ids = []
           
            for tile in tiles:
                try:
                    tile_id = tile['properties']['tile_id']
                    tile_ids.append(tile_id)
                    self.logger.log_message("info","    ----> " + tile_id, True, True, False)
                except KeyError:
                    self.logger.log_message("warning", "Tile without tile_id found", True, True, False)
                
            self.logger.log_message("info", f"|| ............FETCHING TILE IDS SUCCESFULL ({len(tile_ids)})............\n", True, True, True)
            return tile_ids
                    
        except error.HTTPError as e:
            self.logger.log_message("info", f"|| Fetching Tile IDs failed: {e}. \n", True, True, False)
            return None
        
    def download_tiles(self, tile_ids):
        bag_tiles = []
        try:
            self.logger.log_message("info", "|| ............DOWNLOADING TILES FROM BAG SERVICE............", True, True, True)
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
                    self.logger.log_message("error", f"|| An error occured during downloading of BAG tiles: {e}.", True, True, True,)
                    return None
            
            total_cityObjects = 0 
            for i, tile in enumerate(bag_tiles):
                cityjson_tile = cj.load(tile)
                total_cityObjects += cityjson_tile.number_city_objects()
                
                self.logger.log_message("info", f"|| tile {i}: {tile}", True, True, True)
                    
            self.logger.log_message("info", f"|| ............DOWNLOADING TILES FROM BAG SERVICE SUCCESFULL (nr. of tiles: {len(bag_tiles)}, nr. of CityObjects: {total_cityObjects}:)............\n", True, True, True)
            return bag_tiles
        except Exception as e:        
            traceback_str = traceback.format_exc()
            self.logger.log_message("error", f"|| An error occurred during downloading of BAG tiles: {traceback_str}", True, True, True)
            return None
        
    def merge_tiles(self, bag_tiles):
        self.logger.log_message("info", "|| ............STARTING TILE MERGING............", True, True, True)
        
        cms = []
        try:
            cm = cj.load(bag_tiles[0], transform=False)
            
            for i, f in enumerate(bag_tiles):
                _cm = cj.load(f, transform=False)
                cms.append(_cm)
                
            cm.merge(cms)
            cm.load_from_j()
          
            cj.save(cm, self.path + "/merged_tile.city.json")
            self.logger.log_message("info", f"    ----> total number of CityObjects: {cm.number_city_objects()}", True, True, True)
            self.logger.log_message("info", "|| ............SUCCESFULLY MERGED TILES............\n", True, True, True)
            return cm
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.logger.log_message("error", f"|| An error occurred during merging of BAG tiles: {traceback_str}", True, True, True)
            return None
   
    def intersect_cm_with_aoi(self, cm, aoi_poly) :
        self.logger.log_message("info", "|| ............STARTING INTERSECTING WITH ORIGINAL AOI............", True, True, True)
        try:
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
            cj.save(aoi_cm, self.path + "/intersected_cm.city.json")
            self.logger.log_message("info", f"    ----> total number of CityObjects: {aoi_cm.number_city_objects()}", True, True, True)
            self.logger.log_message("info", "|| ............SUCCESFULLY INTERSECTED WITH ORIGINAL AOI............\n", True, True, True)
            
            obj_data = aoi_cm.export2obj()
            
            with open(self.path + "/output.obj", "w") as file:
                file.write(obj_data.getvalue())
            
            return aoi_cm
        
        except Exception as e:
            traceback_str = traceback.format_exc()
            self.logger.log_message("error", f"|| An error occurred during intersection of BAG tile with the original AOI: {traceback_str}", True, True, True)
            return None
       

        
