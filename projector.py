import numpy as np
import pandas as pd
import geopandas as gpd






def project_WSG84_to_UTM33N(lat, lon):
    gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=gpd.points_from_xy(lon, lat))
    gdf = gdf.set_crs('EPSG:4326').to_crs('EPSG:32633')

    gdf['x'] = list(map(lambda val: val.x, gdf.geometry.values))
    gdf['y'] = list(map(lambda val: val.y, gdf.geometry.values))
    return (gdf.x.values, gdf.y.values)

def project_UTM33N_to_WSG84(x, y):
    if type(x) == float or type(x) == np.float64:
        x = [x]
        y = [y]

    gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=gpd.points_from_xy(x, y))
    gdf = gdf.set_crs('EPSG:32633').to_crs('EPSG:4326')

    gdf['lon'] = list(map(lambda x: x.x, gdf.geometry.values))
    gdf['lat'] = list(map(lambda x: x.y, gdf.geometry.values))
    return (gdf.lat.values, gdf.lon.values)

def project_WSG84_to_UTM33N_gdf(gdf):
    if not gdf.crs == 'EPSG:4326':
        raise RuntimeError(f"Gdf not in the right crs\nSource crs:{gdf.crs}")
    return gdf.to_crs('EPSG:32633')

def project_UTM33N_to_WSG84_gdf(gdf):
    if not gdf.crs == 'EPSG:32633':
        raise RuntimeError(f"Gdf not in the right crs\nSource crs:{gdf.crs}")
    return gdf.to_crs('EPSG:4326')
    
