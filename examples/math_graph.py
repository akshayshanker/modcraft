import pprint

import numpy as np

from graphcraft.graph import Graph
from graphcraft.node import Node


class Add:
    def __call__(self, a, b):
        return a + b


class Power:
    def __call__(self, a, exponent=2):
        return a ** exponent


# Instantiate our callable functions
add = Add()
power = Power()

# Create our NumPy arrays to be operated on
a = np.array([[1, 2, 3], [4, 5, 6]])
b = np.array([[2, 4, 6], [8, 10, 12]])

# Instantiate the computational graph and add
# the nodes to this graph, via assigning the
# functions to the nodes
graph = Graph()
graph.add_node(Node("add", add))
graph.add_node(Node("power", power))

# Define dependencies (DAG structure) between
# the nodes in the graph (add -> power)
graph.add_dependency("add", "power")

# Define the arguments and keyword arguments
# for the graph and execute it
inputs = {
    "add": {"a": a, "b": b},
    "power": {"exponent": 3}
}
results = graph(inputs)

# Print the results
pprint.pprint(results)
