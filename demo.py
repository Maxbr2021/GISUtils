import analyzer as an
import plotter
import time
import data_utils

### load and save GIS data to disk ###
######################################

### configure GIS content and locations
tags, cities = data_utils.configure()
if len(cities) > 1:
    for city in cities:
        data_utils.get_street_network(city)
else:
    data_utils.get_street_network(cities)
# data_utils.compose(cities[0],cities[1]) you may want to combine multiple (street) networks to one big graph

### download GIS data for each tage in the config file and for each location
for tag in tags:
    data_utils.save(tag,data_utils.get_osm_for_place(cities,tags[tag]))



#### main driver code ###
#########################

### iterates through all home locations (gps data points) and calculates different metrics
do_plot = True
output_data_path = "data_out.csv"
analyer = an.Analyzer("data.csv",500,1000,"GisData/roads_walk_Berlin.pkl",15,5)


for location in analyer.stats.values:
    id, home_pos = location[0],location[1:]
    iso = analyer.get_iso_plot(home_pos)
    shop_intersection,shop_count = analyer.return_count("GisData/shop_tags.geojson",home_pos)
    analyer.set_attribut(id,"shop_count",shop_count)
    poi_intersection,poi_count = analyer.return_count("GisData/poi_tags.geojson",home_pos)
    analyer.set_attribut(id,"poi_count",poi_count)
    home_buffer, green_space, green_ratio = analyer.return_ratio("GisData/green_tags.geojson",home_pos)
    analyer.set_attribut(id,"green_ratio",green_ratio)
    analyer.stats.to_csv(output_data_path,index=False)

    if do_plot: ### allow to plot the data to a map or a figure for visual inspection
        plotter.plot(home_pos,(iso,"black"),(home_buffer,"yellow"),(green_space,"green"),(poi_intersection,"black"),figsize=(20,20),id=int(id))
        plotter.plot(home_pos,(iso,"black"),(home_buffer,"yellow"),(green_space,"green"),(poi_intersection,"black"),map=True,id=int(id))


