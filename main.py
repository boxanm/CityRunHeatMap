#TODO propojit se stahovanim informaci
#TODO prebarvit graf podle poctu bodu
import os.path
import datetime
import gpxpy
import osmnx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import functions as functions

filename = 'grenoble_5000.hraphml'
path_gpx = 'data/gpx/'
path_maps = 'data/maps/'

startDate = datetime.datetime(2019, 1, 21)

#load graph



print("==============   Loading map   ==================")
print("")
graph = osmnx.load_graphml(filename = filename,folder = path_maps)
fig, ax1 = osmnx.plot_graph(graph, show = False, close = False)
print("Done")

#find all gpx files
gpx_files = []
print("================  Found following files  ===================")

for file in os.listdir(path_gpx):
    if file.endswith(".gpx"):
        gpx_files.append(os.path.join(path_gpx, file))
        print(os.path.join(path_gpx, file))

print("===================  Activities  ============================")

functions.plot_tracks(gpx_files)

print("==================Finding collecive segments=====================")

handles, labels = functions.find_segments(gpx_files)
plt.legend(handles, labels,loc='best')
plt.show()

print("=================Total distance you ran=====================")
total_distance = functions.count_total_distance(gpx_files)
print(total_distance, "km")
