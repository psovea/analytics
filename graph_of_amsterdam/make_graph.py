import matplotlib.pyplot as plt
import networkx as nx

def make_nodes(G, nodes_json):
    for stop in nodes_json:
        if ((float(stop["lat"]), float(stop["lon"])) != (47.974766, 3.3135424)):
            G.add_node(stop["stop_code"], name=stop["name"], pos=(float(stop["lat"]), float(stop["lon"])))


def make_edges(G, stops, line_info):
    # Insert the edges between stops (nodes)
    l = [[line["stop_code"] for line in lines] for lines in line_info]
    for lines in l:
        for i, stop_code in enumerate(lines):
            if i < (len(lines) - 1) and G.has_node(stop_code) and G.has_node(lines[i + 1]):
                G.add_edge(stop_code, lines[i + 1])



def plot_graph(G):
    # plot the graph
    options = {
        'node_color': 'blue',
        'node_size': 10,
        'width': 0.5,
        'with_labels': False
    }

    plt.figure(figsize=(7,7))
    nx.draw(G, nx.get_node_attributes(G, "pos"), **options)
    plt.show()
