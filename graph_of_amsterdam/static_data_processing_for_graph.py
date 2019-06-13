import requests
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
    query = "get-line-info"
    r = requests.get(url + query)
    line_info_json = r.json()

    return line_info_json


if __name__ == "__main__":
    # Initialize the graph and get the data from the static database.
    G = nx.DiGraph()
    stops = get_stops_json()
    line_info = get_line_info_json()

    # Fill the graph and plot it.
    mg.make_nodes(G, stops)
    mg.make_edges(G, stops, line_info)
    mg.plot_graph(G)
