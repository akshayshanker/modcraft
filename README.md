# GraphCraft

GraphCraft is a graph-based computation library written in Python. It is designed to allow straightforward creation of Directed Acyclic Graph (DAG) based workflows for arbitrary callables. These types of approaches are typical in data processing and machine learning based workflows.

GraphCraft is designed to provide a graph-based 'backbone' for other libraries that naturally suit a graph-based computation approach. It is designed to handle the heavy lifting of ensuring the graph can appropriately process data based on upstream dependencies, allowing downstream tasks to concentrate on their respective data processing modules.

## Features

* `Node` class to track parent and child node relationships
* `Graph` class to create dependencies between nodes, topologically sort the nodes for computation and execute the graph computation
* An example to demonstrate GraphCraft's capabilities

## Example

The following example shows how two callable classes can be assigned to nodes in the graph, with a simple linear dependency, to calculate some basic mathematical operations.

The first callable simply adds its two arguments to the `__call__` method, while the second raises the argument by an exponent provided as a keyword argument.

In the graph the output of the first node is automatically passed to the second node's `__call__` method argument, allowing the array to be raised to the power of 3.

```
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
```

The output of the example is:

```
Evaluating node: add...
Evaluating node: power...
{'add': array([[ 3, 6, 9],
       [12, 15, 18]]),
 'power': array([[  27,  216,  729],
       [1728, 3375, 5832]])}
```

## Installation

You can install GraphCraft using pip:

```
pip install git+https://github.com/mhallsmoore/graphcraft.git@main
```

## Development

### Requirements

* Python 3.9 or higher
* Dependencies are managed with pip and defined in pyproject.toml

### Running Tests

Install development dependencies:

```
pip install git+https://github.com/mhallsmoore/graphcraft.git@main[dev]
```

Run tests from the repository root:

```
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
