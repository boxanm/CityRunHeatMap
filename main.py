import os.path
import datetime
import gpxpy
import osmnx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import functions as functions
from collections import Counter, OrderedDict
import time
import math
import argparse
from customClasses import Cell

parser = argparse.ArgumentParser()

parser.add_argument('-a', '--activities', help='download new activities from garmin connect', action='store_true')
parser.add_argument('-d', '--downloadMap', help='download map')


place_name = "Grenoble, France" #da se udelat jako list nekolika mist
point1 = (45.1904, 5.7607)

distance = 5000
distance_type_var = 'network'
network_type_var = 'walk'

filename = 'grenoble_4000.graphml'
path_gpx = 'data/gpx/'
path_maps = 'data/maps/'

startDate = datetime.datetime(2019, 1, 21)

start = time.time()
lap = time.time()


cmap = plt.cm.gist_heat
grid_size = 10 #grid size in meters


max_density = 0
min_density = 1000000
color_change_threshold = 0.2
last_color = 0
segment_len = 0
fade_size = 5
fade_last_segment_len = 10
min_segment_len = 100
type = 'running'
datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'


# find all gpx files
gpx_files = functions.loadFiles(path_gpx)
print("Done in: ", time.time() - lap, " s")
lap = time.time()

print("================ Extracting gps locations===================")
max_latitude = -500
min_latitude = 500
max_longitude = -500
min_longitude = 500
lon_lat_list = []
for file in gpx_files:
    gpx_file = open(file,'r')
    gpx = gpxpy.parse(gpx_file)
    lon = []
    lat = []
    last_point = (0,0)
    # if(datetime.datetime.strptime(file.time, datetime_format) < startDate):#TODO date
    #     print('activity too old ')
    #     continue
    for track in gpx.tracks:
        if(track.type != type):
            continue
        for segment in track.segments:
            for gps_point in segment.points:
                if(functions.haversine(last_point, (gps_point.longitude, gps_point.latitude)) > 2):
                    #to avoid bias in heat in uphills, when you move slower
                    lon.append(gps_point.longitude)
                    lat.append(gps_point.latitude)
                    if(max_latitude < gps_point.latitude):
                        max_latitude = gps_point.latitude
                    if(min_latitude > gps_point.latitude):
                        min_latitude = gps_point.latitude
                    if(max_longitude < gps_point.longitude):
                        max_longitude = gps_point.longitude
                    if(min_longitude > gps_point.longitude):
                        min_longitude = gps_point.longitude
                last_point = (gps_point.longitude, gps_point.latitude)
    lon_lat_list.append((lon,lat))
print("Done in: ", time.time() - lap, " s")
lap = time.time()

loc_width = functions.haversine((max_longitude,max_latitude),(min_longitude,max_latitude))
loc_height = functions.haversine((max_longitude,max_latitude),(max_longitude,min_latitude))
num_width = loc_width / grid_size #number of cells in width
num_height = loc_height / grid_size #number of cells in height
cell_size_width = (max_longitude - min_longitude) / num_width
cell_size_height = (max_latitude - min_latitude) / num_height
print("The location's dimensions are: ",round(loc_width,3), "x" , round(loc_height,3) , " m")
print('with ', round(num_width), "x", round(num_height) ," cells in the grid")
print("and cell's sizes of: ", cell_size_width, "x" ,cell_size_height)



#load map
lap = time.time()
map, img_map = functions.loadOSMMap(download = True, extent=(max_longitude, max_latitude, min_longitude, min_latitude), zoom=15)
print("Done in: ", time.time() - lap, " s")

lap = time.time()
cells_width = np.arange(min_longitude, max_longitude, cell_size_width)
cells_height = np.arange(min_latitude, max_latitude, cell_size_height)

print("================  Adding to Dictionary  ===================")

grid_dict = {}
for lon,lat in lon_lat_list:
    for point in zip(lon,lat):
        x,y = functions.naiveSearch(cells_width, cells_height, point[0], point[1])
        if not (x,y) in grid_dict.keys():
            grid_dict[(x,y)] = Cell(min_longitude + x*cell_size_width,min_latitude + y*cell_size_height)
            grid_dict[(x,y)].addUsage()
        grid_dict[(x,y)].addUsage()

print("Done in: ", time.time() - lap, " s")
lap = time.time()

print("============Neighbors adjustement============")
for key, point in grid_dict.items():
    sum = 0
    if (key[0]-1, key[1]) in grid_dict:
        sum += grid_dict[key[0]-1, key[1]].density/4
    if (key[0], key[1]-1) in grid_dict:
        sum += grid_dict[key[0], key[1]-1].density/4
    if (key[0]+1, key[1]) in grid_dict:
        sum += grid_dict[key[0]+1, key[1]].density/4
    if (key[0], key[1]+1) in grid_dict:
        sum += grid_dict[key[0], key[1]+1].density/4
    if (key[0]-1, key[1]-1) in grid_dict:
        sum += grid_dict[key[0]-1, key[1]-1].density/8
    if (key[0]-1, key[1]+1) in grid_dict:
        sum += grid_dict[key[0]-1, key[1]+1].density/8
    if (key[0]+1, key[1]-1) in grid_dict:
        sum += grid_dict[key[0]+1, key[1]-1].density/8
    if (key[0]+1, key[1]+1) in grid_dict:
        sum += grid_dict[key[0]+1, key[1]+1].density/8
    point.density_norm = sum

print("Done in: ", time.time() - lap, " s")
lap = time.time()

print("============Density normalization============")
counter = Counter()
for point in grid_dict.values():
    counter[point.density_norm] += 1
    min_density = min(min_density, point.density_norm)
    max_density = max(max_density, point.density_norm)
orderedDict = OrderedDict(sorted(counter.items(), key=lambda t: t[0]))



# min_density = 1
print("Min: ", min_density, " Max:", max_density)

counter = Counter()
for point in grid_dict.values():
    point.density_norm = functions.normalize(point.density_norm, min_density, max_density)
    point.color = functions.logarithmAsymptotic(point.density_norm)
    counter[point.density_norm] += 1

print("Done in: ", time.time() - lap, " s")
lap = time.time()
segment = [[],[]]
all_segments = [] #lon, lat, color
print("============Plotting tracks============")
for lon, lat in lon_lat_list:
    for point in zip(lon,lat):
        x,y = functions.naiveSearch(cells_width, cells_height, point[0], point[1])
        if((x,y) not in grid_dict.keys()):
            print("unknown point")
        color = grid_dict[(x,y)].color
        if(abs(color - last_color) > color_change_threshold and segment_len > min_segment_len): #change of density
            all_segments.append([segment[0][:-fade_last_segment_len],segment[1][:-fade_last_segment_len],last_color])

            #fade into a new segment
            end_last_segment = (segment[0][-fade_last_segment_len-1:],segment[1][-fade_last_segment_len-1:])
            end_last_segment[0].append(point[0])
            end_last_segment[1].append(point[1])

            color_change = (last_color - color)/len(end_last_segment[0])
            for i in range(len(end_last_segment[0])-1):
                all_segments.append([[end_last_segment[0][i],end_last_segment[0][i+1]],[end_last_segment[1][i],end_last_segment[1][i+1]],
                last_color - (i+1)*color_change])

            last_point = (segment[0][-1],segment[1][-1])
            segment[0] = []
            segment[1] = []
            segment_len = 0
            last_color = color

        segment_len+=1
        segment[0].append(point[0])
        segment[1].append(point[1])
    all_segments.append([segment[0], segment[1], last_color])
    segment_len = 0
    segment[0] = []
    segment[1] = []

all_segments.sort(key = lambda x: x[2])
for segment in all_segments:
    x, y = zip(*(map.rev_geocode((p1, p2)) for p1, p2 in zip(segment[0], segment[1])))
    plt.plot(x, y, color = cmap(segment[2]), linewidth = 7)

# figure_tracks.show()
plt.imshow(img_map)
print("Done in: ", time.time() - lap, " s")
lap = time.time()

print("============Plotting density histogram============")
figure_histogram = plt.figure(2)
orderedDict2 = OrderedDict(sorted(counter.items(), key=lambda t: t[0]))
plt.bar(orderedDict.keys(), orderedDict.values(), color = 'red')
figure_histogram.show()


print("============Plotting color distribution============")
figure_function = plt.figure(3)
plot_list = [functions.logarithmAsymptotic(x) for x in orderedDict2.keys()]
plt.scatter(orderedDict2.keys(), plot_list)
figure_function.show()

print("====================Total time: ", time.time() - start, " s==========================")

plt.show()
