import numpy as np
import scipy.spatial
import os.path
import gpxpy
import osmnx
import random
from math import sin, cos, sqrt, radians

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
    filename = 'grenoble_5000.hraphml'
    path_gpx = 'data/gpx/'
    path_maps = 'data/maps/'
    file1_gpx = 'beh_9.gpx'
    file2_gpx = 'beh_10.gpx'
    file3_gpx = 'beh_13.gpx'
    file4_gpx = 'beh_4.gpx'
    file5_gpx = 'beh_3.gpx'
    file6_gpx = 'beh_2.gpx'
    file7_gpx = 'beh_1.gpx'
    gpx_files = []
    gpx_files.append(os.path.join(path_gpx, file1_gpx))
    gpx_files.append(os.path.join(path_gpx, file2_gpx))
    gpx_files.append(os.path.join(path_gpx, file3_gpx))
    # gpx_files.append(os.path.join(path_gpx, file4_gpx))
    # gpx_files.append(os.path.join(path_gpx, file5_gpx))
    # gpx_files.append(os.path.join(path_gpx, file6_gpx))
    # gpx_files.append(os.path.join(path_gpx, file7_gpx))
    #
    # graph = osmnx.load_graphml(filename = filename,folder = path_maps)
    # fig, ax1 = osmnx.plot_graph(graph, show = False, close = False)

    lat_lot_list = []
    for file in gpx_files:
        gpx_file = open(file,'r')
        gpx = gpxpy.parse(gpx_file)

        lon_lat = []
        points_cartesian = []
        for track in gpx.tracks:
            print(track.name + " " + str(gpx.time))
            for segment in track.segments:
                for point in segment.points:
                    lon_lat.append([point.longitude,point.latitude])
                    # points_cartesian.append(to_Cartesian(point.longitude,point.latitude))
        lat_lot_list.append(np.vstack(lon_lat))

    all_trails = lat_lot_list

    tolerance = 0.0001 #TODO determine exactly what this number should be to represent 20 meters
    tolerance_cluster = 0.001


    labelled_pts = np.vstack([np.hstack([a, np.ones((a.shape[0], 1)) * i])
    for i, a in enumerate(all_trails)])

    print(labelled_pts)
    print(labelled_pts[:,2 ])#labels say to what gpx file a point belongs
    tree = scipy.spatial.KDTree(labelled_pts[:, :2]) #tree contains all points in all loaded files

    points_within_tolerance = tree.query_ball_point(labelled_pts[:, :2], tolerance)


    vfunc = np.vectorize(lambda a: np.any(labelled_pts[a, 2] != labelled_pts[a[0], 2]))

    # print(vfunc)
    matches = vfunc(points_within_tolerance)
    # for match in matches:
    #     print(match)
    #     print(labelled_pts[match, :2])
    #     print(labelled_pts[match])
    # # print('mathces: ' , matches)
    # print(len(matches))
    # print(labelled_pts[matches, :2])
    matching_points = labelled_pts[matches, :2]
    #
    import scipy.cluster.hierarchy

    clusters = scipy.cluster.hierarchy.fclusterdata(matching_points, t = tolerance_cluster, criterion = 'distance')

    print('number of clusters: ' , len(clusters))
    for i, match in enumerate(matching_points):
        print('Matching points ' , i , ' size: ', len(match))

    import itertools as itertools
    import matplotlib.pyplot as plt

    cmap = plt.cm.Reds
    for lon_lat in all_trails:
        plt.plot(lon_lat[:, 0], lon_lat[:, 1], c=cmap(0.4+(random.random())/2))



    print(len(set(clusters)))

    for clust_idx, shape, size in zip(set(clusters), itertools.cycle(['o', 'v', '^', '<', '>', 's', 'p', '*', '8', 'd']), itertools.cycle([40, 50, 60])):
        plt.scatter(matching_points[clusters == clust_idx, 0], matching_points[clusters == clust_idx, 1], c='blue', marker=shape, s=size)

    plt.show()
