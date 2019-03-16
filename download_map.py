
import osmnx as osmnx

place_name = "Grenoble, France" #da se udelat jako list nekolika mist
point1 = (45.1904, 5.7607)

for i in range(4500,5000,500):
    distance = i
    distance_type_var = 'network'
    network_type_var = 'walk'
    filename = 'grenoble_'+str(distance)+'.hraphml'
    path = 'maps/'
    # graph = osmnx.graph_from_place(place_name, network_type = network_type_var)
    graph = osmnx.graph_from_point(point1, distance, distance_type = distance_type_var, network_type = network_type_var)
    osmnx.save_graphml(graph, filename = path+filename)
