
import osmnx as osmnx
import networkx as nx
import random
import matplotlib.cm as cm
from matplotlib import pyplot as plt

#finds shortest path between two nodes in an OSMNX graph1
def find_shortest_path(node1, node2, graph):
    return nx.shortest_path(graph, source = node1, target = node2)

if __name__ == "__main__":

    filename = 'grenoble_2500.hraphml'
    path_gpx = 'data/gpx/'
    path_maps = 'data/maps/'


    graph = osmnx.load_graphml(filename = filename,folder = path_maps)

    nodes = list(graph.nodes())

    point1 = (45.20926888100802898406982421875, 5.76389609836041927337646484375)
    point2 = (45.19823712296783924102783203125, 5.78004048205912113189697265625)

    node1 = osmnx.get_nearest_node(graph,point1)
    node2 = osmnx.get_nearest_node(graph,point2)


    route = find_shortest_path(node1, node2, graph)
    osmnx.plot.plot_graph_route(graph, route)
    # cmap = plt.cm.plasma
    # route_list = []
    # route_colours = []
    # node_colours = []
    # for i in range(0,10):
    #     node1 = random.choice(nodes)
    #     node2 = random.choice(nodes)
    #
    #     print(node1, node2)
    #     route = find_shortest_path(node1, node2, graph)
    #     print(route)
    #     route_list.append(route)
    #     colour = cmap(i/10)
    #     route_colours.append(colour)
    #     node_colours.append(colour)
    #     node_colours.append(colour)
    # osmnx.plot.plot_graph_routes(graph, route_list, route_color=route_colours, orig_dest_node_color=node_colours)
