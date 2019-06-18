import matplotlib.pyplot as plt
import networkx as nx


def make_nodes(G, nodes_json):
    """Add all nodes from the get-stops query to the NetworkX graph."""
    for stop in nodes_json:
        # The node label is it's stopcode. Other attributes are the name of the
        # station and it's position in latitude, longitude.
        G.add_node(stop["stop_code"], name=stop["name"],
                   pos=(float(stop["lat"]), float(stop["lon"])))


def make_edges(G, stops, line_info, weights):
    """Add edges between nodes in the graph to the NetworkX graph."""
    # Make a 2d list of, in order, stopnumbers per line.
    all_lines = [[line["stop_code"] for line in lines] for lines in line_info]

    # For every stopcode, check if it and the next stopcode are both nodes in
    # the graph. If so, add the edge between them.
    for lines in all_lines:
        for i, stop_code in enumerate(lines):
            if (i < (len(lines) - 1) and G.has_node(stop_code) and
                    G.has_node(lines[i + 1])):
                start = stop_code
                end = lines[i + 1]
                weight = 0
                if start in weights.keys() and end in weights[start].keys():
                    weight = weights[start][end]

                G.add_edge(stop_code, lines[i + 1], weight=weight)


def add_weight(G, begin, end, weight):
    """Add weight to the edge from begin to end in G."""
    G[begin][end]['weight'] = weight


def plot_graph(G):
    """Plot the NetworkX graph using matplotlib."""
    # Set some options for the plot, like node color and size, edge width and
    # with/without labels.
    options = {
        'node_color': 'blue',
        'node_size': 10,
        'width': 0.5,
        'with_labels': False
    }

    # Draw the directed graph in a matplotlib figure.
    plt.figure(figsize=(7, 7))
    nx.draw(G, nx.get_node_attributes(G, "pos"), **options)
    plt.show()
