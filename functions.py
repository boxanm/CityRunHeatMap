import math
import os.path
import datetime
import gpxpy
import osmnx as osmnx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from customClasses import Point
import numpy as np

def loadMap(filename = None, path = None, download = False, saveMap = False):
    place_name = "Grenoble, France" #da se udelat jako list nekolika mist
    point1 = (45.1904, 5.7607)

    distance = 5000
    distance_type_var = 'network'
    network_type_var = 'walk'

    print("==============   Loading map   ==================")
    if(not filename and not path and not download):
        print('No map specified')
    elif(filename and path):
        graph = osmnx.load_graphml(filename = filename,folder = path)
        print("Map loaded")
        return osmnx.plot_graph(graph, show = False, close = False)
    elif(download):
        # graph = osmnx.graph_from_place(place_name, network_type = network_type_var)
        # graph = osmnx.graph_from_point(point1, distance, distance_type = distance_type_var, network_type = network_type_var)
        if(saveMap):
            osmnx.save_graphml(graph, filename = 'graph1.hraphml')
        print("Map loaded")
        return osmnx.plot_graph(graph, show = False, close = False)

    return None, None

def loadFiles(path, download = False):
    print("================Searching for gpx files===================")
    gpx_files = []
    if(not path and not download):
        print('No files specified')
    elif(path):
        for file in os.listdir(path):
            if file.endswith(".gpx"):
                gpx_files.append(os.path.join(path, file))
                print(' ', os.path.join(path, file))
        return gpx_files
    return []

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx;

def naiveSearch(cells_width,cells_height,point_lon, point_lat):
    return (find_nearest(cells_width,point_lon), find_nearest(cells_height,point_lat))

 #https://math.stackexchange.com/questions/354852/function-design-a-logarithm-asymptotic-to-one

def logarithmAsymptotic(x):
    a = 30
    return (a*math.log10(1+x))/(1+a*math.log10(1+x))

def normalize(x, minimum, maximum):
    if(minimum == 0):
        minimum = 1
    return (x - minimum)/(maximum - minimum)

def deleteDuplicateLabels():
    handles, labels = plt.gca().get_legend_handles_labels()
    i =1
    while i<len(labels):
        if labels[i] in labels[:i]:
            del(labels[i])
            del(handles[i])
        else:
            i +=1
    # (handles,labels).sort()#TODO sort
    return handles, labels

#returns haversine distance between 2 points in meters
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lon1, lat1 = coord1
    lon2, lat2 = coord2


    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))#sjednotit poradi lat, lon

def euclidean(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1-lat2)**2+(lon1-lon2)**2)

def find_collective_segments2(gpx_files):
    threshold_segment_distance = 100
    threshold_point_distance = 25
    iteration_speed_const = 20


    points_segments = []
    for file in gpx_files:
        gpx_file = open(file,'r')
        gpx = gpxpy.parse(gpx_file)

        points = []
        lat = []
        lon = []
        lastPoint = None
        for track in gpx.tracks:
            for segment in track.segments:
                for gps_point in segment.points:
                    point = Point(gps_point.latitude,gps_point.longitude,lastPoint)
                    if(len(points) != 0):
                        lastPoint.addNext(point)
                    points.append(point)
                    lastPoint = point
                    lat.append(point.latitude)
                    lon.append(point.longitude)
            plt.plot(lon,lat, label = gpx.time)
        points[-1].addNext(None)
        points_segments.append((points,gpx.time))
    iteration_speed = 1
    intersections_points = []
    inter = []
    index = 0
    iterations = 0
    miss_counter = 0
    counter = 0
    times_done = []

    distance_points_min = 1000000

    for points1, time1 in points_segments:
        counter = 0

        for points2, time2 in points_segments:
            if(time1 == time2):
                print('same track')
                continue
            if(time2 in times_done):
                print("already done")
                continue

            intersections_points.append([])
            index+=1
            print('num of segments: ' , len(intersections_points))
            for point1 in points1:
                # print("New point:")
                iterations = 0
                miss_counter = 0
                distance_points_min = 1000000
                iteration_speed=1
                for point2 in points2:
                    # print(" ",iterations)
                    iterations+=1
                    if(point1.prev != None and point1.prev.neighbor != None):
                        point2 = point1.prev.neighbor
                        distance = haversine(point1.getLatLon(), point2.getLatLon())
                        # print('Shortcut')
                        while(distance <= distance_points_min):
                            if(point2.next == None):
                                break
                            # print('  Smaller distance! ' , distance)
                            distance_points_min = distance
                            nearestPoint = point2
                            point2 = point2.next
                            distance = haversine(point1.getLatLon(), point2.getLatLon())
                        break

                    distance = euclidean(point1.getLatLon(), point2.getLatLon())
                    if(distance <= distance_points_min):
                        # print('  Smaller distance! ' , distance)
                        distance_points_min = distance
                        nearestPoint = point2
                if(nearestPoint != None):
                    distance_points_min = haversine(point1.getLatLon(), nearestPoint.getLatLon())
                else:
                    distance_points_min = 1000000
                if(distance_points_min < threshold_point_distance):
                    if(len(intersections_points[-1]) == 0):
                        print('empty segment, continuing')
                    else:
                        distance = haversine(point1.getLatLon(),intersections_points[-1][-1].getLatLon())
                        # print("=== segment distance: " , distance)
                        if(distance > threshold_segment_distance):
                            # print("distance between " + str(point1.getLatLon()) +
                             # " and " + str(intersections_points[-1][-1].getLatLon()) + ": " +
                             # str(distance) + "=> starting new segment: ", index+1)
                            index+=1
                            intersections_points.append([])
                    if(nearestPoint != None):
                        point1.addNeighbor(nearestPoint)
                        if(nearestPoint in points2):
                            points2.remove(nearestPoint)
                        nearestPoint = None
                    intersections_points[-1].append(point1)
                    counter+=1
            print("-----------" + str(time1) + "  " + str(time2) + ": " + str(counter))
        counter = 0
        times_done.append(time1)
    print("Segments found: ", len(intersections_points))
    intersections_points = [x for x in intersections_points if(len(x)!=0) ]
    print("Segments after prunning: ", len(intersections_points))
    return (intersections_points)

def plot_tracks(gpx_files):
    for file in gpx_files:
        gpx_file = open(file,'r')
        gpx = gpxpy.parse(gpx_file)
        lon = []
        lat = []
        for track in gpx.tracks:
            for segment in track.segments:
                for gps_point in segment.points:
                    lon.append(gps_point.longitude)
                    lat.append(gps_point.latitude)
        plt.plot(lon,lat)

def split_tracks(tracks):#TODO rozdelit cestu tam a zpet na dve casti
    for track in tracks:
        for i in range(len(track)):
            for j in range(i+1, len(track)):#TODO +1 vymenit za hodnotu zjistenou z prumerne a maximalni vzdalenosti dvou gpx bodu
                ...

def find_segments(gpx_files):
    threshold_segment_distance = 100
    threshold_point_distance = 25
    iteration_speed_const = 20


    points_segments = []
    for file in gpx_files:
        gpx_file = open(file,'r')
        gpx = gpxpy.parse(gpx_file)

        points = []
        lastPoint = None
        for track in gpx.tracks:
            for segment in track.segments:
                for gps_point in segment.points:
                    point = Point(gps_point.latitude,gps_point.longitude,lastPoint)
                    if(len(points) != 0):
                        lastPoint.addNext(point)
                    points.append(point)
                    lastPoint = point
        points[-1].addNext(None)
        points_segments.append((points,gpx.time))
        print(len(points))

    distance_points_min = 1000000

    for i in range(len(points_segments)):#TODO pro jeden bod projit vsechny ostatni point_segments
        points1, time1 = points_segments[i]
        print('GPS track ' ,i, 'lenght: ' , len(points1))

        for j in range(i+1,len(points_segments)):
            deleted_counter = 0
            points2, time2 = points_segments[j]

            for point1 in points1:
                distance_points_min = 1000000
                for point2 in points2:
                    if(point1.prev != None and point1.prev.neighbor != None):
                        point2 = point1.prev.neighbor
                        distance = haversine(point1.getLatLon(), point2.getLatLon())
                        # print('Shortcut')
                        while(distance <= distance_points_min):
                            if(point2.next == None):
                                break
                            # print('  Smaller distance! ' , distance)
                            distance_points_min = distance
                            nearestPoint = point2
                            point2 = point2.next
                            distance = haversine(point1.getLatLon(), point2.getLatLon())
                        break

                    distance = euclidean(point1.getLatLon(), point2.getLatLon())
                    if(distance <= distance_points_min):
                        # print('  Smaller distance! ' , distance)
                        distance_points_min = distance
                        nearestPoint = point2
                if(nearestPoint != None):
                    distance_points_min = haversine(point1.getLatLon(), nearestPoint.getLatLon())
                else:
                    distance_points_min = 1000000
                    print('none')
                if(distance_points_min < threshold_point_distance):
                    point1.addNeighbor(nearestPoint)
                    # print(nearestPoint in points_segments[j][0])
                    # if(nearestPoint in points_segments[j][0]):
                    deleted_counter+=1
                        # if(not nearestPoint in points2):
                    points_segments[j][0].remove(nearestPoint)
                    # else:
                    #     print('nenalezen')
                    nearestPoint = None
            print("================" + "Tracks ", i, "&", j,":", deleted_counter, "neighbors")
    print(end='\n\n\n')
    segments = []
    for points, time in points_segments:
        print('len: ' , len(points))
        density_change_counter = 0
        lastPoint = None
        last_change_density = 0
        segments.append(([],time))
        print('new list of points, adding segment')
        for point in points:
            if(lastPoint == None):
                last_change_density = point.density
                segments[-1][0].append(point)
            else:
                if(haversine(point.getLatLon(), lastPoint.getLatLon()) > threshold_segment_distance):
                    print('change in distance')
                    segments.append(([],time))
                    segments[-1][0].append(point)
                    last_change_density = point.density
                # elif(point.density != lastPoint.density):
                if(last_change_density !=  point.density):
                    density_change_counter += 1
                    if(density_change_counter >= 5):
                        print('change in density, adding new segment')
                        segments.append(([],time))
                        segments[-1][0].append(point)
                        density_change_counter = 0
                        last_change_density = point.density
                else:
                    segments[-1][0].append(point)
            # print('point: ', point)
            lastPoint = point
            # print('lastPoint: ', lastPoint)
    print('num of segments: ', len(segments))


    dens_max = 1
    for points,time in segments:
        for point in points:
            if(point.density > dens_max):
                dens_max = point.density

    print("dens max" , dens_max)


    cmap = plt.cm.plasma
    for points,time in segments:
        points_segment = []
        for point in points:
            points_segment.append((point.longitude,point.latitude))
        if(points[0].density < 10):
            label = 'Density: 0' + str(points[0].density)
        else:
            label = 'Density: ' + str(points[0].density)
        plt.plot(*zip(*points_segment), color = cmap(0.5 + points[0].density/(2*dens_max)),linewidth=(2+3*points[0].density/dens_max), label = label)


    #delete duplicate labels
    handles, labels = deleteDuplicateLabels()


    return(handles, labels)

def count_total_distance(gpx_files):
        distance = 0
        for file in gpx_files:
            gpx_file = open(file,'r')
            gpx = gpxpy.parse(gpx_file)
            lon = []
            lat = []
            for track in gpx.tracks:
                for segment in track.segments:
                    lastPoint = (segment.points[0].latitude, segment.points[0].longitude)
                    for gps_point in segment.points:
                        distance += haversine((gps_point.latitude, gps_point.longitude), lastPoint)
                        lastPoint = (gps_point.latitude, gps_point.longitude)
        return round(distance/1000,2)

if __name__ == "__main__":

    #find all gpx files


    path = 'data/gpx/'
    file1_gpx = 'beh_9.gpx'
    file2_gpx = 'beh_10.gpx'
    file3_gpx = 'beh_13.gpx'
    file4_gpx = 'beh_4.gpx'
    file5_gpx = 'beh_3.gpx'
    file6_gpx = 'beh_2.gpx'
    file7_gpx = 'beh_1.gpx'
    gpx_files = []
    gpx_files.append(os.path.join(path, file1_gpx))
    gpx_files.append(os.path.join(path, file2_gpx))
    gpx_files.append(os.path.join(path, file3_gpx))
    gpx_files.append(os.path.join(path, file4_gpx))
    gpx_files.append(os.path.join(path, file5_gpx))
    gpx_files.append(os.path.join(path, file6_gpx))
    gpx_files.append(os.path.join(path, file7_gpx))

    print(count_total_distance(gpx_files), "km")


    # handles, labels = find_segments(gpx_files)
    # plt.legend(handles, labels,loc='best')
    # plt.show()
