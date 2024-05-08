import osmnx as ox
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import shapely
import geopandas as gpd
import os
import mplleaflet
import networkx as nx
from shapely.geometry import Point
import json



ox.settings.log_console=True
ox.settings.use_cache=True




### save walk network as gpickle
def get_street_network(place, network_type='walk',layer_name='roads',target_path="GisData"):
    make_dir(target_path)
    layer_name += f'_{network_type}'
    location_name = place.split(',')[0]
    print(f"start with {place}")
    G = ox.graph.graph_from_place(place, network_type=network_type,simplify=True)
    print("writing to file")
    path = f'{target_path}/{layer_name}_{location_name}.pkl'
    nx.write_gpickle(G,path)


### save osm data for given places and tags as shapfile
def get_osm_for_place(places,tags,extra=None):
    place_lst = []
    for place in places:
        print(f"start with {place}")
        tag_lst =['geometry']
        tag_lst.extend(list(tags.keys() ) )
        gdf = ox.geometries.geometries_from_place(place, tags=tags)
        if len(gdf) == 0:
            return None
        if 'nodes' in gdf.columns:
            gdf = gdf.reset_index().drop(columns=['osmid','nodes']).copy()
        else:
            gdf = gdf.reset_index().drop(columns=['osmid']).copy()
        if extra != None:
            tag_lst.extend(extra)
        gdf = gdf.rename(columns={'element_type': "geom_type"})
        gdf = gdf.set_index('geom_type')
        gdf = gdf[~ (gdf.geometry.geom_type == 'LineString')]
        place_lst.append(gdf)
    appended_data = pd.concat(place_lst)
    return appended_data[tag_lst].dropna(how='all',axis = 1)

def compose(G,G2):
    if (G and G2) != None:
        composed = nx.compose(G,G2)
    elif G != None:
        composed = G
    elif G2 != None:
        composed = G2
    else:
        print("error no graph is valid")
        composed = None
    return composed

####### helper #########


def save(layer_name,gdf,target_path="GisData"):
    dir_name = make_dir(target_path)
    print(f"saving GIS data to {dir_name}/{layer_name}.geojson")
    gdf.to_file(f"{dir_name}/{layer_name}.geojson", driver="GeoJSON")

def make_dir(dir_path='GisData'):
    try:
        os.mkdir(dir_path)
        print("Directory " , dir_path ,  " Created ")
    except FileExistsError:
        print("Directory " , dir_path ,  " already exists")
    return dir_path

def configure(config_file="config.json"):
    with open(config_file,"r") as f:
        config = json.loads(f.read())
        return config["tags"], config["cities"]

#####download street "walk" network ######
#get_street_network(citys[0])
#get_street_network(citys[1])
#G = compose(nx.read_gpickle('GisData/roads_walk_Berlin.pkl'),nx.read_gpickle('GisData/roads_walk_Havelland.pkl'))
#nx.write_gpickle(G,'GisData/merged_roads_BerHvl.pkl')

####download gis layer for tags #######
# save("greenspace_new",get_osm_for_place(citys,green_tags))
# save("poi_new",get_osm_for_place(citys,poi_tags))
# save("shop_new",get_osm_for_place(citys,shop_tags))
# save("health_new",get_osm_for_place(citys,health))
# save("publicTransport_new",get_osm_for_place(citys,publicTransport_tags,extra=["name"]))






