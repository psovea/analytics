import matplotlib.pyplot as plt
import networkx as nx


def make_nodes(G, nodes_json):
    # Insert all stops (nodes) into the Graph
    # i = 0
    for stop in nodes_json:
        # for key, value in stop.items():
        if ((float(stop["lat"]), float(stop["lon"])) != (47.974766, 3.3135424)):
            G.add_node(stop["stop_code"], name=stop["name"], pos=(float(stop["lat"]), float(stop["lon"])))
        # i = i + 1


def make_edges():
    # Insert the edges between stops (nodes)
    pass


def plot_graph(G):
    # plot the graph
    plt.subplot(121)
    nx.draw(G, nx.get_node_attributes(G, "pos"), with_labels=False)
    plt.show()
