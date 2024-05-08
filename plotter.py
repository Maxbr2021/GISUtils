import numpy as np
from matplotlib import pyplot as plt
import mplleaflet
import utils
from descartes import PolygonPatch
import osmnx as ox




def plot(home_to_plot,*args,map=False,alpha=0.5,figsize=(20,20),id="default",prefix="maps",save_fig=True):
    axes = []
    fig = plt.figure(figsize=figsize)
    axes.append(utils.build_geo_df(home_to_plot).plot(marker="x",color="red"))
    for i, (a,c) in enumerate(args):
        if alpha <= 1:
            alpha += (i*.05)
        axes.append(a.plot(ax = axes[i],color=c,alpha=alpha))
    if map:
        mplleaflet.show(fig=axes[-1].figure,path=f"{prefix}/{id}_map.html")
        return None
    else:
        plt.plot()
        if save_fig:
            plt.savefig(f"{prefix}/{id}_plot.png")
        return None
        
def plot_reachability_G(G,trip_times,isochrone_polys):
    # NOTE: function from https://github.com/gboeing/osmnx-examples/blob/main/notebooks/13-isolines-isochrones.ipynb
    iso_colors = ox.plot.get_colors(n=len(trip_times), cmap="plasma", start=0, return_hex=True)
    fig, ax = ox.plot_graph(G,figsize=((20,20)), show=False, close=False, edge_color="#999999", edge_alpha=0.2, node_size=0)
    for polygon, fc in zip(isochrone_polys, iso_colors):
        patch = PolygonPatch(polygon, fc=fc, ec="none", alpha=0.7, zorder=-1)
        ax.add_patch(patch)
    plt.show()