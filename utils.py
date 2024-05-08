import geopandas as gpd
import osmnx as ox
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import networkx as nx
import projector




###################### HELPER ##############################
############################################################


def build_geo_df(lat_lon,crs='epsg:4326'):
    #build geoDatafram for point of interest
    point = to_point(lat_lon)
    geo_s = gpd.GeoSeries(point,dtype='object')
    geo_df = gpd.GeoDataFrame(geometry=geo_s)
    geo_df = geo_df.set_crs(crs) #set lon lat input to wsg84 crs
    return geo_df

def to_point(lon_lat):
    return Point(lon_lat[0],lon_lat[1])


def create_point_buffer(lat_lon,dist,is_projected=True,project_buffer_to=None):
    if is_projected:
        point = build_geo_df(lat_lon,'EPSG:32633')
        buffer = gpd.GeoDataFrame(geometry=point.buffer(dist)).set_crs(point.crs)
    else:
        point = build_geo_df(lat_lon).to_crs('EPSG:32633')
        buffer = gpd.GeoDataFrame(geometry=point.buffer(dist)).set_crs(point.crs)
    if project_buffer_to != None:
        buffer = buffer.to_crs(project_buffer_to)
    return buffer

def spatial_overlays(buffer,data,how='intersection',merge_polygon=True):
    if data.crs == None or data.crs != buffer.crs:
        geo_df_proj = ox.project_gdf(data,to_crs=buffer.crs) #make sure both are in the same crs
    else:
        geo_df_proj = data
    if merge_polygon == True:
        overlay = gpd.overlay(buffer,polygon_to_gdf(geo_df_proj,geo_df_proj.crs),how=how,keep_geom_type=False)
    else:
        overlay = gpd.overlay(buffer,geo_df_proj,how=how,keep_geom_type=False) # only use if df2 are same geomety types for sure
    return overlay

def polygon_to_gdf(gdf_p,proj=None):
    polygon = gdf_p.unary_union
    s = gpd.GeoSeries(polygon)
    gdf = gpd.GeoDataFrame(geometry=s).set_crs(proj)
    return gdf

def gdf_to_centroid(gdf,crs="EPSG:32633"):
    try:
        gdf = projector.project_WSG84_to_UTM33N_gdf(gdf)
        gdf['geometry'] = gdf.centroid
        #gdf = Projector.project_UTM33N_to_WSG84_gdf(gdf)#polygon.to_crs('epsg:4326')
        gdf.reset_index(inplace=True)
        gdf['geom_type'] = 'node'
        gdf = gdf.set_index('geom_type',drop=True)
        return gdf.to_crs(crs)
    except Exception as e:
        print(f"Could not center gdf as of exception\{e}")
        return gdf.to_crs(crs)

def is_valid(G):
    if ( (len(G.edges) > 0) & (len(G.nodes) > 0) ):
        return True
    else:
        return False
        
def calc_ratio(buffer,inter):
    return round((inter.unary_union.area / buffer.unary_union.area) * 100,2) 

def make_iso_polys(G, center_node, trip_times, edge_buff=25, node_buff=50, infill=False):
    # NOTE: function from https://github.com/gboeing/osmnx-examples/blob/main/notebooks/13-isolines-isochrones.ipynb
    isochrone_polys = []
    for trip_time in sorted(trip_times, reverse=True):
        subgraph = nx.ego_graph(G, center_node, radius=trip_time, distance="time")

        node_points = [Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)]
        nodes_gdf = gpd.GeoDataFrame({"id": list(subgraph.nodes)}, geometry=node_points)
        nodes_gdf = nodes_gdf.set_index("id")

        edge_lines = []
        for n_fr, n_to in subgraph.edges():
            f = nodes_gdf.loc[n_fr].geometry
            t = nodes_gdf.loc[n_to].geometry
            edge_lookup = G.get_edge_data(n_fr, n_to)[0].get("geometry", LineString([f, t]))
            edge_lines.append(edge_lookup)

        n = nodes_gdf.buffer(node_buff).geometry
        e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
        all_gs = list(n) + list(e)
        new_iso = gpd.GeoSeries(all_gs).unary_union

        # try to fill in surrounded areas so shapes will appear solid and
        # blocks without white space inside them
        if infill:
            new_iso = Polygon(new_iso.exterior)
        isochrone_polys.append(new_iso)
    return isochrone_polys



###################### HELPER ##############################
############################################################


###################### WRAPPER ##############################
############################################################
def ratio(buffer,data,how="intersection"):
    # project both to match the crs ---> spatical calculations should be done in utm33n
    data_proj = projector.project_WSG84_to_UTM33N_gdf(data)
    buffer_proj = projector.project_WSG84_to_UTM33N_gdf(buffer)
    assert data_proj.crs == buffer_proj.crs

    # build overlay in utm33n
    overlay = gpd.overlay(buffer_proj,polygon_to_gdf(data_proj,data_proj.crs),how=how,keep_geom_type=False )

    # caluclate the green ratio
    ratio = calc_ratio(buffer_proj,overlay)
    return ratio

def return_sub_graph(G,nodes,home,buffer_dist=1500,is_projected=True):
    buff_wsg48 = create_point_buffer(home,buffer_dist,is_projected=is_projected,project_buffer_to='EPSG:4326')
    buff = projector.project_WSG84_to_UTM33N_gdf(buff_wsg48)
    intersecting_nodes = nodes[nodes.intersects(buff_wsg48['geometry'][0])].index
    G_sub = G.subgraph(intersecting_nodes)

    if is_valid(G_sub):
        try:
            G_simple = ox.simplification.simplify_graph(G_sub)
        except Exception as e:
            G_simple = G_sub
        buff_area = buff['geometry'][0].area
        return_tuple =  (ox.utils_graph.get_largest_component(G_simple), ox.basic_stats(G_simple,buff_area) )
        return_tuple[1]["intersection_3_way_density_km"] = ox.stats.intersection_count(G=G_simple, min_streets=3) / (buff_area / 1_000_000)
        return return_tuple
    else:
        if is_projected:
            print(f"Error: No valid subgraph found for home {projector.project_UTM33N_to_WSG84(home)} ")
            print(f"Found {len(intersecting_nodes)} in G for home location")
        else:
            print(f"Error: No valid subgraph found for home {home} ")
            print(f"Found {len(intersecting_nodes)} in G for home location")
        return None,None

def reachability_polygon(G,home_lat_lon,trip_times,travel_speed,edge_buff=150, node_buff=150, infill=False):
    # NOTE: function based of https://github.com/gboeing/osmnx-examples/blob/main/notebooks/13-isolines-isochrones.ipynb
    center_node = ox.distance.nearest_nodes(G, home_lat_lon[1], home_lat_lon[0])#[0]
    G_utm = ox.project_graph(G,to_crs='EPSG:32633')
    meters_per_minute = travel_speed * 1000 / 60  # km per hour to m per minute
    for _, _, _, data in G_utm.edges(data=True, keys=True):
        data["time"] = data["length"] / meters_per_minute
    isochrone_polys = make_iso_polys(G_utm,center_node,trip_times, edge_buff=edge_buff, node_buff=node_buff, infill=infill)
    geo_s = gpd.GeoSeries(isochrone_polys)
    geo_df = gpd.GeoDataFrame(geometry=geo_s)
    geo_df = geo_df.set_crs('EPSG:32633')
    return geo_df

###################### WRAPPER ##############################
############################################################

############### Load functions #############################
############################################################

###load osm data around home locaion of the user form disc
def load_data_around_home(path,point,dist=500,is_projected=True,project_to='EPSG:4326'):
    buff_proj = create_point_buffer(point,dist,is_projected=is_projected,project_buffer_to=project_to)
    data = gpd.read_file(path,bbox=buff_proj).set_index('geom_type',drop=True)
    data = data.to_crs(project_to)
    return data

def load_graph_from_pickle(path):
    G = nx.read_gpickle(path)
    nodes = ox.graph_to_gdfs(G, edges=False)
    return G,nodes

############### Load functions #############################
############################################################
