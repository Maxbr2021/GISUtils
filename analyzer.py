import sys
import numpy as np
import utils
import projector 
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import projector
import utils
import osmnx as ox



class Analyzer():
    def __init__(self,data_in,buffer_dist,load_buffer_dist,street_network_path,travel_time,travel_speed):
        stats =  pd.read_csv(data_in)
        self.lon_lat_home = stats.values[:,1:]
        self.stats = stats

        self.buffer_dist = buffer_dist
        self.load_buffer_dist = load_buffer_dist
        self.G,self.NODES = utils.load_graph_from_pickle(street_network_path)
        self.travel_time = travel_time
        self.travel_speed = travel_speed

    def return_ratio(self,layer,home_lon_lat,buffer_dist=500):
        buffer = utils.create_point_buffer(home_lon_lat,buffer_dist ,False,'EPSG:4326')
        data = utils.load_data_around_home(layer,home_lon_lat,buffer_dist + 100,False,'EPSG:4326')
        ratio = utils.ratio(buffer,data)
        return (buffer,data,ratio)
    
    def get_iso_plot(self,home_lon_lat):
        G_sub, stats = utils.return_sub_graph(self.G,self.NODES,home_lon_lat,is_projected=False,buffer_dist=self.buffer_dist)
        self.iso = utils.reachability_polygon(G_sub,home_lon_lat,[self.travel_time],self.travel_speed)
        return projector.project_UTM33N_to_WSG84_gdf(self.iso)
    
    def return_count(self,layer,home_lon_lat):
        data = utils.load_data_around_home(layer,home_lon_lat,self.load_buffer_dist,is_projected=False)
        if data.shape[0] > 0 :
            data_centered = utils.gdf_to_centroid(data)
            intersecting = utils.spatial_overlays(self.iso.iloc[[0]], data_centered, merge_polygon=False)
            count = intersecting.shape[0]
        else:
            intersecting = None
            count = 0
        return projector.project_UTM33N_to_WSG84_gdf(intersecting), count
    
    def set_attribut(self,id,label,value):
        self.stats.loc[self.stats.id == id,label] = value


    

    

    

