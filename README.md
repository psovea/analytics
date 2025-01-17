# Analytics
Python analytics from Prometheus DB

## Coding style
In this repository we use the PEP8 coding style. If you contribute, please make sure your code is PEP8 compliant. Install the PEP8 command line tool with this command:
```bash
    pip install pep8
```
Then you can just use ```pep8 your_python_file.py``` in your terminal to see if your code is PEP8 compliant.


## Fetch prometheus
In fetch_prometheus.py functions are written that query the Prometheus database. Also some functions are made that create the queries and its labels.


## Graph of amsterdam
We made a Graph of all the stops in amsterdam using NetworkX. This graph can be used for testing and for a visual overview of the stops. The graph can be made with the `init_graph(weights)` function from get_graph.py.

### Networkx
To install NetworkX (Python):
```bash
    pip install networkx
```

### Other libraries
We use Matplotlib to plot the graph and the requests module to make a HTTP request, so make sure those are installed on your machine if you want to run our code.


In get_graph.py, data to make the graph in NetworkX is gathered from data endpoints. In make_graph.py the actual graph is made with the correct data. In fetch_prometheus.py functions are written to communicate with the Prometheus database.
