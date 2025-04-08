from owslib.wms import WebMapService
import config.global_config as g_config
import os
import utilities as ut
from shapely import wkt


class AHNHandler:
    def __init__(self, path, wkt_polygon):
        self.wkt_polygon = wkt_polygon
        self.AHN_URL = g_config.AHN_URL
        self.path = path
        self.logger.log_message("info", "---->> AHNHandler succesfully created", True, True, True)
        self.image_size = ut.calculate_aspectratio(wkt_polygon.bounds) 
        
    def __repr__(self):
        return (f"AHNHandler Details:\n"
                f"Path: {self.path}\n"
                f"AOI: {self.wkt_polygon}\n"
                f"AHN_URL: {self.AHN_URL}\n"
        )
        
    def download_ahn(self):
        wms = WebMapService(self.AHN_URL, version='1.1.1')
        
        try:
            response = wms.getmap(
                layers=[g_config.WMS_LAYER],
                styles=[''],
                srs='EPSG:28992',
                bbox=self.wkt_polygon.bounds,
                size=self.image_size,
                format='image/png' 
            )
            image_filename = os.path.join(self.path, "AHN", 'map_tile.png')
            try:
                with open(image_filename, 'wb') as f:
                    f.write(response.read())
            except Exception as e:
                self.logger.log_message("info", f"|| An error has occured when trying to save the AHN PNG: {e}", True, True, True)
                return 
                
        except Exception as e:
            self.logger.log_message("info", f"|| An error has occured when trying to download the AHN PNG: {e}", True, True, True)
            return 
            
        
    
        

    
    


