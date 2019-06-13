import requests
import json
import networkx as nx
import make_graph as mg

# The url for the endpoint of the static database.
url = "http://18.216.203.6:5000/"


def get_stops_json():
    """Get data about stops from the static database."""
    query = "get-stops"
    r = requests.get(url + query)
    stops_json = r.json()

    return stops_json


def get_line_info_json():
    """Get data about lines from the static database. """
    query = "get-line-info?operator=GVB"
    r = requests.get(url + query)
    line_info_json = r.json()

    return line_info_json


def get_coor_weight_json():
    """Make a JSON list with lat, lon and weight (punctuality)."""
    G, stops = init_graph()

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
    return json.dumps(list(stop_dict.values()))

def init_graph():
    G = nx.DiGraph()
    G.edges.data('weight', default=1)
    stops = get_stops_json()
    line_info = get_line_info_json()

    # Fill the graph and plot it.
    mg.make_nodes(G, stops)
    mg.make_edges(G, stops, line_info)
    return G, stops
