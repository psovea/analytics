import requests
import networkx as nx
import make_graph as mg

url = "http://18.216.203.6:5000/"


def get_stops_json():
    # Send a request to the MYSQL database to get all the stops in JSON format
    # url = "http://18.216.203.6:5000/"
    query = "get-stops?town=Amsterdam"

    r = requests.get(url + query)
    stops_json = r.json()
    return stops_json


def get_transport_line_stops_json():
    # Send a request to the MYSQL database to get all the Transport Line Stops
    # url = "http://184.72.120.43:9800/"
    query = "get-lines"

    r = requests.get(url + query)
    transport_line_stops_json = r.json()
    return transport_line_stops_json


def get_transport_line_json():
    # Send a request to the MYSQL database to get all the Transport Line
    # url = "http://184.72.120.43:9800/"
    query = "get-line-info"

    r = requests.get(url + query)
    transport_line_json = r.json()
    return transport_line_json


def make_edge_data():
    pass


if __name__ == "__main__":
    # Make a directed graph in networkx
    # print(get_stops_json()[0])
    G = nx.DiGraph()
    mg.make_nodes(G, get_stops_json())
    mg.plot_graph(G)
