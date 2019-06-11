import requests
import networkx as nx
import make_graph as mg

def get_stops_json():
    # Send a request to the MYSQL database to get all the stops in JSON format
    url = "http://184.72.120.43:9800/"
    query = "getStops/"

    r = requests.get(url + query)
    stops_json = r.json()
    return stops_json

def get_transport_line_stops_json():
    # Send a request to the MYSQL database to get all the Transport Line Stops
    url = "http://184.72.120.43:9800/"
    query = "getTransportLineStops/"

    r = requests.get(url + query)
    transport_line_stops_json = r.json()
    return transport_line_stops_json

def get_transport_line_json():
    # Send a request to the MYSQL database to get all the Transport Line
    url = "http://184.72.120.43:9800/"
    query = "getTransportLine/"

    r = requests.get(url + query)
    transport_line_json = r.json()
    return transport_line_json


def make_edge_data():
    pass

if __name__ == "__main__":
    # Make a directed graph in networkx
    G = nx.DiGraph()
    mg.make_nodes(G, get_stops_json())
    mg.plot_graph(G)
