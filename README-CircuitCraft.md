# CircuitCraft

CircuitCraft is an experimental framework for computational graphs focused on economic modeling.

## Concept

In most graph-based AI-ML packages, computational graphs focus on computational operations as nodes
without a clear representation of the data flow or results as part of the graph.

In CircuitCraft, **computational circuits** represent inputs and outputs of functional operators as nodes, with the operators
themselves as edges between them.

This approach is particularly valuable for economic problems, where the data have meaningful functional
relationships to each other once they have been solved.

## What Makes a Circuit a Circuit?

A CircuitCraft **circuit** has the following key characteristics:

1. **Node-Edge Structure**: Circuits represent inputs and outputs of functional operators as nodes, with the operators themselves as edges between them.

2. **Directional Solving**: Each circuit has two types of directed edges:
   - **Backward edges**: Used for computing core functions (e.g., policy functions)
   - **Forward edges**: Used for applying these functions to transform data (e.g., distributions)

3. **Circuit Lifecycle**:
   - **Mathematical Definition**: The structure and relationships are defined
   - **Parameterization**: Concrete parameter values are assigned
   - **Component Assembly**: Operations are attached to edges
   - **Initialization**: Initial data values are set
   - **Solving**: The circuit is executed (backward and forward passes)
   - **Analysis**: Results are extracted and analyzed

4. **Dataflow Clarity**: Each node stores meaningful data that represents the state of the computation at that point.

## Key Components

CircuitCraft has the following core components:

### 1. Nodes

Nodes store data, such as:
- Policy functions
- Probability distributions
- State variables

Each node can contain multiple data items accessed by keys.

```python
from circuitcraft.node import Node

# Create a node with two data types
node = Node("policy_node", {"policy": None, "distribution": None})

# Later, set data values
node.set_data("policy", policy_function)
```

### 2. Operations

Operations are simply functions that transform data between nodes:

```python
# Define simple operations as functions
def backward_operation(data):
    """Square the x value (backward operation)"""
    x = data.get("x")
    if x is not None:
        return {"x": x**2}
    return {}

def forward_operation(data):
    """Transform y based on x (forward operation)"""
    x = data.get("x")
    y = data.get("y") 
    if x is not None and y is not None:
        return {"y": y + 0.5 * x}
    return {}
```

### 3. Circuits (Graphs)

Circuits connect nodes using operations, forming a directed graph with two types of edges:
- **Backward edges**: For solving operations (successor to predecessor)
- **Forward edges**: For push-forward operations (predecessor to successor)

```python
from circuitcraft.graph import Graph

# Create a circuit
circuit = Graph(name="SimpleCircuit")

# Add nodes
circuit.add_node(Node("node_0", {"x": None, "y": None}))
circuit.add_node(Node("node_1", {"x": None, "y": None}))

# Connect with operations
circuit.add_edge("node_1", "node_0", backward_operation,
                source_key="x", target_key="x",
                edge_type="backward")

circuit.add_edge("node_0", "node_1", forward_operation,
                source_keys=None, target_key=None,  # Use full data object
                edge_type="forward")
```

## Workflow

CircuitCraft follows a clear workflow:

1. **Circuit Creation**: Create the graph structure
2. **Configuration**: Set up nodes and edges
3. **Initialization**: Provide initial values
4. **Solution**: Execute operations to compute results
5. **Persistence**: Save and load circuit states

Each phase is tracked with boolean flags:
- `is_configured`
- `is_initialized`
- `is_solvable`
- `is_solved`

## Minimal Circuit Example

Here's a minimal example showing how to create and solve a simple mathematical circuit:

```python
# Create a basic circuit
circuit = Graph(name="SimpleCircuit")

# Add nodes
circuit.add_node(Node("node_0", {"x": None, "y": None}))
circuit.add_node(Node("node_1", {"x": None, "y": None}))
circuit.add_node(Node("node_2", {"x": None, "y": None}))

# Define operations
def backward_operation(data):
    """Square the x value (backward operation)"""
    x = data.get("x")
    if x is not None:
        return {"x": x**2}
    return {}

def forward_operation(data):
    """Transform y based on x (forward operation)"""
    x = data.get("x")
    y = data.get("y") 
    if x is not None and y is not None:
        return {"y": y + 0.5 * x}
    return {}

# Connect nodes with operations
# Backward edge from node_1 to node_0
circuit.add_edge("node_1", "node_0", backward_operation, 
                source_key="x", target_key="x",
                edge_type="backward")

# Forward edge from node_0 to node_1
circuit.add_edge("node_0", "node_1", forward_operation, 
                source_keys=None, target_key=None,  # Use full data object
                edge_type="forward")

# Forward edge from node_1 to node_2
circuit.add_edge("node_1", "node_2", forward_operation, 
                source_keys=None, target_key=None,  # Use full data object
                edge_type="forward")

# Initialize with values
circuit.set_node_data("node_2", {"x": 4})    # Initial terminal value for backward pass
circuit.set_node_data("node_0", {"y": 3})    # Initial initial value for forward pass
circuit.is_initialized = True

# Solve the circuit
circuit.solve()

# Access results
x0 = circuit.get_node_data("node_0", "x")  # Should be 16 (4² = 16)
y2 = circuit.get_node_data("node_2", "y")  # Transformed y value

print(f"node_0.x = {x0}")
print(f"node_2.y = {y2}")
```

## Relationship to Economic Modeling

CircuitCraft's structure aligns with economic modeling principles:

1. **Sequential Structure with Directional Edges**:
   - **Backward edges**: Computing policy functions through backward induction
   - **Forward edges**: Applying policies to transform distributions forward through time

2. **Functional Operators on Edges**:
   - Operations live on edges rather than nodes
   - This separates data (nodes) from transformations (edges)
   - Mirrors mathematical operators in economic theory

3. **Circuit States**:
   - **Unfulfilled circuits**: Circuit structure exists but hasn't been fully solved
   - **Fulfilled circuits**: All computations have been completed
   - Corresponds to the distinction between model specification and model solution

4. **Backward-Forward Workflow**:
   - First solve backward for policies (like policy functions in economic models)
   - Then solve forward for outcomes (like simulation in economic models)
   - Natural alignment with how recursive economic problems are solved 