import requests
import json
import networkx as nx
import make_graph as mg
import fetch_prometheus as fp

# The url for the endpoint of the static database.
url = "http://18.224.29.151:5000/"


def get_stops_json():
    """Get data about stops from the static SQL database."""
    query = "get-stops"
    r = requests.get(url + query)
    stops_json = r.json()

    return stops_json


def get_line_info_json():
    """Get data about lines from the static SQL database."""
    query = "get-line-info?operator=GVB"
    r = requests.get(url + query)
    line_info_json = r.json()

    return line_info_json


def get_coor_weight_json(period='d', vehicle_type=None, operator=None,
                         area=None):
    """Make a JSON list with lat, lon and weight (punctuality)."""
    # Get the current (last 15 sec) weights for the edges from Prometheus.
    current_data = fp.heatmap_punctuality(period, vehicle_type, operator, area)

    # Make the directed graph.
    G, stops = init_graph(current_data)

    # Make a JSON object that is sent to front-end.
    stop_dict = {}
    for source, dest, attributes in G.edges.data():
        if dest in stop_dict:
            stop_dict[dest][2] += attributes['weight']
        else:
            stop_dict[dest] = [
                G.nodes[dest]['pos'][0],
                G.nodes[dest]['pos'][1],
                attributes['weight']
            ]
    return list(stop_dict.values())


def init_graph(weights):
    """Initialize a directed graph with data from the endpoints."""
    G = nx.DiGraph()

    # Get and extract the right info needed to make the graph.
    stops = get_stops_json()
    line_info = get_line_info_json()

    # Make the nodes and edges of the directed graph.
    mg.make_nodes(G, stops)
    mg.make_edges(G, stops, line_info, weights)
    return G, stops
