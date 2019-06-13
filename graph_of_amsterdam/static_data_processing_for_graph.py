import requests
import networkx as nx
import make_graph as mg

url = "http://18.216.203.6:5000/"


def get_stops_json():
    """
    """
    query = "get-stops"

    r = requests.get(url + query)
    stops_json = r.json()
    return stops_json


def get_line_info_json():
    query = "get-line-info"
    r = requests.get(url + query)
    line_info_json = r.json()

    return line_info_json


if __name__ == "__main__":
    G = nx.DiGraph()
    stops = get_stops_json()
    line_info = get_line_info_json()

    mg.make_nodes(G, stops)
    mg.make_edges(G, stops, line_info)
    mg.plot_graph(G)
