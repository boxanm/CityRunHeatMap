import numpy as np
import scipy.spatial
import os.path
import gpxpy
import osmnx
import random
from math import sin, cos, sqrt, radians
from customClasses import Point

import scipy.cluster.hierarchy
import itertools as itertools
import matplotlib.pyplot as plt

def to_Cartesian(lon, lat, alt = 0):
    """Convert geodetic coordinates to ECEF."""
    A = 6378.137
    B = 6356.7523142
    ESQ = 6.69437999014 * 0.001
    lat, lon = radians(lat), radians(lon)
    xi = sqrt(1 - ESQ * sin(lat))
    x = (A / xi + alt) * cos(lat) * cos(lon)
    y = (A / xi + alt) * cos(lat) * sin(lon)
    z = (A / xi * (1 - ESQ) + alt) * sin(lat)
    return x, y, z

if __name__ == "__main__":
    a = [(1, 2),(2, 3),(4, 1),(1, 0),(1, 5),(4.9, -2),(-1.9, 2.5),(0.9, 3),        (-2.3, -2), (-2.15, -2), (-2, -2), (-1.85, -2) ]
    b = [(-1.1, 2),(-1.1, 3),(-2.1, 2),(1.5, 0),(1, 5.5),(5, -2),(-2, 2.5),(1, 3), (-2.3, -1.9), (-2.15, -1.9), (-2, -1.9), (-1.85, -1.9)]
    c = [(-1, 2),(-1, 3),(-2, 2),(0, 0),(3, 5),(5.1, -2),(-2.1, 2.5),(1.1, 3),      (-2.3, -1.95), (-2.15, -1.95), (-2, -1.95), (-1.85, -1.95)]


    tolerance = 0.2 #TODO determine exactly what this number should be to represent 20 meters
    tolerance_cluster = 0.2

    all_tracks = []
    all_tracks.append(a)
    all_tracks.append(b)
    all_tracks.append(c)

    lon_lat_list = []
    for track in all_tracks:
        lon = []
        lat = []
        for point in track:
            lon.append(point[0])
            lat.append(point[1])
        lon_lat_list.append((lon,lat))

    for lon_lat,shape in zip(lon_lat_list, itertools.cycle(['v', '^', '<', '>', 's', 'p', '*', '8', 'd'])):
        plt.scatter(lon_lat[0],lon_lat[1],marker = shape, c = 'b', s = 200, label = shape)


    labelled_pts = np.vstack([np.hstack([a, np.ones((a.shape[0], 1)) * i])
    for i, a in enumerate(all_tracks)])

    tree = scipy.spatial.KDTree(labelled_pts[:, :2]) #tree contains all points in all loaded files


    # points_within_tolerance = tree.query_ball_point(labelled_pts[:, :2], tolerance)
    points_within_tolerance = tree.query_ball_tree(tree2, tolerance)


    print('=========points_within_tolerance===================')
    print(points_within_tolerance)



    trees = []
    for track in all_tracks:
        trees.append(scipy.spatial.KDTree(track))
    points_within_tolerance = []

    for i, tree1 in enumerate(trees):
        for j, tree2 in enumerate(trees):
            if j <= i or tree1 == tree2:
                continue
            print(i,j)
            points_within_tolerance.append([tree1.query_ball_tree(tree2, tolerance),i])
            print(points_within_tolerance[-1])

    all_points = []
    for points, i in points_within_tolerance:
        print('=========points_within_tolerance=================')
        for indexes in points:
            if indexes != []:
                for idx in indexes:
                    print(a[idx], end = ' ')
                    all_points.append(all_tracks[i][idx])
        print()

    my_dict = {i:all_points.count(i) for i in all_points}
    print()
    print('=========Dictionary=================')
    print(my_dict)

    value_max = max(my_dict.values())
    print(value_max)
    cmap = plt.cm.Reds
    for key, value in my_dict.items():
        print("Color: " , cmap(0.3 + 0.7*(value/value_max)) , "\nSize: " , 100 + value*7)
        plt.scatter(key[0], key[1], color = cmap(0.3 + 0.7*(value/value_max)),s = 70 + value*7)

    plt.grid()
    plt.legend()
    plt.show()
    # all_trails = []
    # all_trails.append(np.vstack(a))
    # # all_trails.append(np.vstack(b))
    # all_trails.append(np.vstack(c))
    #
    #
    # labelled_pts = np.vstack([np.hstack([a, np.ones((a.shape[0], 1)) * i])
    # for i, a in enumerate(all_trails)])
    #
    # print('=========labelled_pts===================')
    # print(labelled_pts)
    # print('=========labels===================')
    # print(labelled_pts[:,2 ])#labels say to what gpx file a point belongs
    # tree = scipy.spatial.KDTree(labelled_pts[:, :2]) #tree contains all points in all loaded files
    # tree2 = scipy.spatial.KDTree(b)
    #
    #
    # # points_within_tolerance = tree.query_ball_point(labelled_pts[:, :2], tolerance)
    # points_within_tolerance = tree.query_ball_tree(tree2, tolerance)
    #
    #
    # print('=========points_within_tolerance===================')
    # print(points_within_tolerance)
    #
    # print(len(labelled_pts))
    # for a in points_within_tolerance:
    #     print("a: ", a)
    #     if(a != []):
    #         plt.scatter(b[a[0]][0],b[a[0]][1])
    #     # print(np.any(labelled_pts[a, 2] != labelled_pts[a[0], 2]))
    # plt.show()
    # vfunc = np.vectorize(lambda a: np.any(labelled_pts[a, 2] != labelled_pts[a[0], 2]))
    #
    # # print(vfunc)
    # matches = vfunc(points_within_tolerance)
    # # for match in matches:
    # #     print(match)
    # #     print(labelled_pts[match, :2])
    # #     print(labelled_pts[match])
    # # # print('mathces: ' , matches)
    # # print(len(matches))
    # # print(labelled_pts[matches, :2])
    # matching_points = labelled_pts[matches, :2]
    #
    # print('=========matching_points===================')
    # print(matching_points)
    #
    # for point, shape in zip(matching_points, itertools.cycle(['*'])):
    #     plt.scatter(point[0], point[1], c='green', marker=shape, s=300)
    # # plt.show()
    #
    #
    # clusters = scipy.cluster.hierarchy.fclusterdata(matching_points, t = tolerance_cluster, criterion = 'distance') #podle tolerance_cluster rozseka matching_points na jednotlive clustery
    #
    #
    # print('=========clusters===================')
    # print(clusters)
    #
    #
    #
    #
    # cmap = plt.cm.Reds
    # for lon_lat in all_trails:
    #     plt.scatter(lon_lat[:, 0], lon_lat[:, 1], s=200)
    #
    #
    # print('Num of segments: ' , len(set(clusters)))
    # for clust_idx, shape in zip(set(clusters), itertools.cycle(['o', 'v', '^', '<', '>', 's', 'p', '*', '8', 'd'])):
    #     print(matching_points[clusters == clust_idx, 0], matching_points[clusters == clust_idx, 1])
    #     plt.scatter(matching_points[clusters == clust_idx, 0], matching_points[clusters == clust_idx, 1], c='blue', marker=shape, s=60)
    #
    # plt.grid()
    # plt.show()
