import os
import osmnx as osmnx

place_name = "Grenoble, France" #da se udelat jako list nekolika mist
point1 = (45.1904, 5.7607)

print("================Downloading maps===================")
distance_type_var = 'network'
network_type_var = 'walk'
path = 'maps/'
for distance in range(1000,10000,1000):
    filename = 'grenoble_'+str(distance)+'.graphml'
    if(filename in os.listdir('data/' + path)):
        print(filename, ' already dowloaded, skipping')
        continue
    # graph = osmnx.graph_from_place(place_name, network_type = network_type_var)
    graph = osmnx.graph_from_point(point1, distance, distance_type = distance_type_var, network_type = network_type_var)
    osmnx.save_graphml(graph, filename = path+filename)
    print(filename, ' dowloaded')
