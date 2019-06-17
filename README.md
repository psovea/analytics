# Analytics
Python analytics from Prometheus DB


## Graph of amsterdam
We made a Graph of all the stops in amsterdam using NetworkX. The graph can be made with the `init_graph(weights)` function from get_graph.py.

### Networkx
To install NetworkX (Python):
```bash
    pip install networkx
```

### Other libraries
We use Matplotlib to plot the graph and the requests module to make a HTTP request, so make sure those are installed on your machine if you want to run our code.


In get_graph.py, data to make the graph in NetworkX is gathered from data endpoints. In make_graph.py the actual graph is made with the correct data. In fetch_prometheus.py functions are written to communicate with the Prometheus database.
