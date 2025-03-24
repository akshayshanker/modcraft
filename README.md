# CircuitCraft

CircuitCraft is an experimental module for computing recursive functional 
operations commonly found in infintie dimensional decision making problems and 
economic models with uncertainty and heterogeneous agents.

## Concept

In traditional computational frameworks, functional operations are often represented as 
nodes, with data flowing through them without a natural graph structure.

In CircuitCraft, inputs and outputs of functional operators are represented as 
**nodes**, with the operators as **directed edges**. This approach is 
grounded in operator theory for dynamic economic models, where data (policy 
functions, distributions, value functions) have meaningful functional relationships\
to the modeller. 

The key structure that CircuitCraft introduces is the **circuit-board**: a directed 
graph with two directed acyclic sub-graphs (**backward** and **forward**). The 
backward sub-graph can be viewed as the transpose of the forward sub-graph, while 
the complete circuit-board forms an **Eulerian circuit**.

A circuit-board can be instantiated with only a mathematical representation and 
partially populated nodes. A mover can contain computational operators (mathematical 
objects), which we call **movers**, yet remain unsolved.

In a circuit-board, each node has two primary attributes: **function** and 
**distribution**, both of which are arbitrary callable objects. The backward mover 
takes the function attribute as input, while a forward mover uses both function 
and density attributes as input. This design requires populating **terminal nodes**
with functions and **initial nodes** with densities.

### Core Structure

A CircuitCraft circuit has the following characteristics:

1. **Nodes**: Store "data" (can be arbitrary objects or callables, in economics,
                 these are objects like policy functions, distributions, or value functions)
2. **Edges**: Contain operations (functional operators that transform data)
3. **Directional Flow**: Backward edges (e.g, for solving) and forward edges (e.g, for simulating)
4. **State Tracking**: Clear graph states with **configuration**, **portable**, and **populated** states.

In our terminology, we make an important distinction between **functional 
operators** (which are abstract mathematical objects), a mathematical represenation 
of that opertator on the computer (which we call a **map*) and a mover, 
which is the computational callable instantiated froma map.

To this end, an edge will have two attributes: **map** and **mover**. The 
map will be arbitrary object which stores the mathematical representation 
of the functional operator, while the mover will be an arbitrary callable object. 

A map along with populated initial and terminal nodes are sufficient to define 
a circuit-board since all edges are implicitly defined. This corresponds to a 
**configured** circuit-board. A portable circuit-board is one where the movers
have also been populated. Finally a **populated** circuit-board is one where 
the solution has been computed for all nodes. 

> [!ALERT]
> We have not yet defined a mathematical structure for nodes seperate to the maps
>. This is because maps will define the type of objects stored in nodes. 

## Components

### Nodes

Each node contains two keys: **function** and **distribution**, both of which are arbitrary 
callable objects.

```python
from circuitcraft.node import Node

# Create a node
node = Node("terminal_node", {"function": None, "distribution": None})

# Set data
node.set_data("function", terminal_policy_function)
```

### Operations

Operations are functions that transform data between nodes.

```python
# Define operations as functions
def backward_operation(data):
    """Square the input value (backward operation)"""
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

### Circuits (Graphs)

Circuits connect nodes with operations, forming directed graphs with two types of edges:

```python
from circuitcraft.graph import Graph

# Create a circuit
circuit = Graph(name="SimpleCircuit")

# Add nodes
circuit.add_node(Node("node_0", {"x": None, "y": None}))
circuit.add_node(Node("node_1", {"x": None, "y": None}))

# Connect nodes with operations
# Backward edge
circuit.add_edge("node_1", "node_0", backward_operation, 
                source_key="x", target_key="x",
                edge_type="backward")

# Forward edge
circuit.add_edge("node_0", "node_1", forward_operation, 
                source_keys=None, target_key=None,  # Use full data object
                edge_type="forward")
```

## Workflow

CircuitCraft follows a clear workflow:

1. **Circuit Creation**: Create the graph structure with nodes and edges
   - Add nodes using `add_node()`
   - Connect nodes with edges using `add_edge()` (without operations)
   - Define the graph topology and data structure

2. **Configuration**: Set up operations on edges
   - Assign operations to edges using `set_edge_operation()`
   - Verify that the graph structure is valid
   - Mark the circuit as configured by setting `is_configured = True`

3. **Initialization**: Provide initial values for node data 
   - Set initial values with `set_node_data()`
   - Mark the circuit as initialized by setting `is_initialized = True`
   - Initialize values at endpoints (terminal nodes)

4. **Solution**: Execute operations to compute results node by node
   - Call `solve()` method to execute all operations
   - First solves backward edges, then forward edges
   - Results can be accessed with `get_node_data()`

Each phase is tracked with boolean flags:
- `is_configured`: Configuration step is complete
- `is_initialized`: Initialization step is complete
- `is_solvable`: Both configuration and initialization are complete with valid data
- `is_solved`: Solution step is complete

```python
# Complete workflow example
circuit = Graph(name="SimpleCircuit")

# 1. Circuit Creation - Create nodes and graph structure
circuit.add_node(Node("node_0", {"x": None, "y": None}))
circuit.add_node(Node("node_1", {"x": None, "y": None}))
circuit.add_edge("node_1", "node_0", edge_type="backward")

# 2. Configuration - Assign operations to edges
def backward_operation(data):
    """Square the input value (backward operation)"""
    x = data.get("x")
    if x is not None:
        return {"x": x**2}
    return {}

circuit.set_edge_operation("node_1", "node_0", backward_operation, 
                           source_key="x", target_key="x")
circuit.is_configured = True

# 3. Initialization - Provide initial values
circuit.set_node_data("node_1", {"x": 4})
circuit.is_initialized = True

# 4. Solution - Execute operations
circuit.solve()  # Executes all operations

# Access results
result = circuit.get_node_data("node_0", "x")
```

## Example

Here's a minimal example of a circuit:

```python
# Create a circuit
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
circuit.add_edge("node_1", "node_0", backward_operation, 
                source_key="x", target_key="x",
                edge_type="backward")
circuit.add_edge("node_0", "node_1", forward_operation, 
                source_keys=None, target_key=None,
                edge_type="forward")
circuit.add_edge("node_1", "node_2", forward_operation, 
                source_keys=None, target_key=None,
                edge_type="forward")

# Initialize with values
circuit.set_node_data("node_2", {"x": 4})
circuit.set_node_data("node_0", {"y": 3})
circuit.is_initialized = True

# Solve the circuit
circuit.solve()

# Access results
x0 = circuit.get_node_data("node_0", "x")  # Should be 16 (4² = 16)
y2 = circuit.get_node_data("node_2", "y")  # Transformed value

print(f"node_0.x = {x0}")
print(f"node_2.y = {y2}")
```

## Key Features

- **Separate Backward and Forward Solvers**: Flexibility to execute only backward or forward operations
- **Individual Edge Execution**: Fine-grained control to execute specific operations
- **Function-Based Operations**: Use ordinary Python functions for transformations
- **State Tracking**: Clear lifecycle states from configuration to solution

# Relationship to Economic Modeling

CircuitCraft's structure aligns with economic modeling principles:

1. **Sequential Structure with Directional Edges**:
   - **Strictly sequential**: Each node has at most one incoming and one outgoing edge in each direction
   - **Backward edges**: Computing policy functions through backward induction, where each step depends on the next period's solution
   - **Forward edges**: Applying policies to transform distributions forward through time in a sequential chain
   - This sequential structure naturally maps to time-indexed economic variables and state transitions

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

For example, let $\mathbb{C}$ be the Coleman operator acting on a next period policy function $\sigma^{\text{nxt}}$ to yield a policy function $\sigma$

$$
\sigma = \mathbb{C}[\sigma^{\text{nxt}}], \qquad \sigma^{\text{nxt}} \in V, 
$$

where $V$ is some Polish space -- on the computer, $V$ is a space of "callables of 
some type". We refer to this as the `backward operation'.

Starting with an instance of the object $\sigma^{\text{nxt}} \in V$, once 
we compute $\sigma^{\text{nxt}}$, we are not done. We may want to call on $\sigma$ and then $\sigma^{\text{nxt}}$ to simulate a model or push-forward a measure as follows

$$
\mu_{1} = \mu_{0} \circ \sigma^{-1},
$$

and then 

$$
\mu_{2} = \mu_{1} \circ \sigma^{\text{nxt},-1}.
$$

For the push-forward operations, $\sigma$ and $\sigma^{\text{nxt}}$ are
equally "important" to be stored as nodes in a graph; for general equilibrium 
computations, the measures in turn also become important to be stored as nodes
in a graph.

Before we compute the problem, suppose we know $\sigma$ and $\mu_{0}$, and we 
know the operator $\mathbb{C}$ is well-defined. We then have a mathematical 
graph where the nodes are ${\mu_{2}}$, $\{\sigma^{\text{nxt}}, \mu_{1}\}$ and $\{\sigma, \mu_{0}\}$. The backward operation can be represented by an edge from $\sigma^{\text{nxt}}$ to $\sigma$ -- the idea here is to make the leap and say the edge is the pair ${\sigma^{\text{nxt}}, \mathbb{C}}$. Practically this means 
simply attaching property $\mathbb{C}$ to the edge from $\sigma^{\text{nxt}}$ to $\sigma$.

Even before we solve for $\sigma$, the graph above has a representation implicitly
as soon as we specify the initial policy function $\sigma^{\text{nxt}}$, the initial distribution $\mu_{0}$, and the operator $\mathbb{C}$. We can then attach
the computer representation of $\sigma^{\text{nxt}}$ to the node $\sigma^{\text{nxt}}$, the computer representation of the policies and distributions to 
their respective nodes once we solve or populate the graph.

Given an initial values $\sigma$ and $\mu_{0}$, we can represent a graph for the above problem as follows

```
                          ┌───────────────────┐
                          │  Node_0: {σ,μ₀}   │
                          └───────────────────┘
                               ↑     ↓
                               │     │
       backward solve          │     │      forward push 
        σ = C[σⁿˣᵗ]            │     │       μ₁ = μ₀ ∘ σ⁻¹
                               │     │
                               │     │
                               │     ▼
                          ┌───────────────────┐                     ┌───────────────┐
                          │ Node_1: {σⁿˣᵗ,μ₁} │────────────────────→│ Node_2: {,μ₂} │
                          └───────────────────┘                     └───────────────┘
                                                   forward push
                                                   μ₂ = μ₁ ∘ (σⁿˣᵗ)⁻¹
```

## Circuit Architecture

We call the above graph a **circuit-board**. CircuitCraft creates circuit-boards with a directed graph with two directed acyclic sub-graphs (**backward** and **forward**).

The sequential constraint is a defining feature of CircuitCraft circuits - each node can have at most one incoming and one outgoing edge in each direction. This means both the backward and forward paths form simple chains rather than complex networks, directly matching the sequential nature of economic processes.

A circuit object contains a common set of nodes and backward and forward edges
which produce a backward path and a forward path.

Each node in a circuit-board is a two-tuple of arbitrary callables.

Each edge links a node to another node via a callable on the first (second) item of each node to the first (second) item of the other node. Acting and returning the first item of a node is the **backward** operation and acting and returning the second item of a node is the **forward** operation.

We can instantiate a circuit-board with only a mathematical representation and an initial value for each end (i.e., a first item of the terminal node and the second item of the initial node). In the above diagram, the terminal node is node_0 and the initial node is node_2.

We can then solve the circuit and lazily populate each node and edge with the results.

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

This example demonstrates:
1. Creating a circuit with 3 nodes
2. Defining backward and forward operations
3. Connecting nodes with directional edges
4. Initializing with values at the endpoints
5. Solving the circuit (backward and forward passes)
6. Accessing the computed results

# Implementation Examples

## Mathematical Operations Circuit

```python
"""
CircuitCraft Example: Mathematical Operations Circuit
------------------------------------------------
This example demonstrates the CircuitCraft concept with simple mathematical operations
following a creation → configuration → solution workflow.

Key elements:
1. Nodes store data (policy functions, distributions)
2. Edges store operations and their direction determines whether they're backward or forward:
   - Backward edges: Point upward in the diagram (σⁿˣᵗ → σ)
   - Forward edges: Point downward/rightward (μ₀, σ → μ₁)
"""

from circuitcraft.graph import Graph
from circuitcraft.node import Node
from circuitcraft.operations import Operation
import numpy as np

#----------------------------------------------
# 1. COMPONENT DEFINITION
#----------------------------------------------
class Square(Operation):
    """Operation for backward-directed edge: Square a vector"""
    def __call__(self, x):
        return x**2  # Element-wise square

class MatrixOperation(Operation):
    """Operation for forward-directed edge: Transform matrix using vector"""
    def __call__(self, matrix, vector):
        # Create a transformation using the vector to modify the matrix
        v_column = vector.reshape(-1, 1)  # Column vector
        outer_product = v_column @ v_column.T  # Outer product creates a symmetric matrix
        # Apply transformation: scale original matrix + rank-1 update
        return matrix + 0.1 * (matrix @ outer_product)

#----------------------------------------------
# 2. LAYOUT DESIGN
#----------------------------------------------
# Build a circuit with empty nodes
circuit = Graph(name="MathCircuit")
print(f"Empty circuit created: {circuit.name}")
print(f"Circuit is configured: {circuit.is_configured}")  # False - configuration needed

# Create our nodes - initially empty
circuit.add_node(Node("node_0", {"policy": None, "distribution": None}))
circuit.add_node(Node("node_1", {"policy": None, "distribution": None}))
circuit.add_node(Node("node_2", {"policy": None, "distribution": None}))

# Create the operations to be used in edges
square_op = Square(name="backward_solve")  # Operation for backward-directed edge
matrix_op = MatrixOperation(name="forward_push")  # Operation for forward-directed edges

#----------------------------------------------
# 3. CONNECTION ROUTING
#----------------------------------------------
# Connect nodes with operations
# The direction of the edge determines backward vs forward:

# BACKWARD EDGE: node_1 → node_0 (upward direction in diagram)
circuit.add_edge("node_1", "node_0", square_op, 
                source_key="policy", target_key="policy",
                edge_type="backward")

# FORWARD EDGE: node_0 → node_1 (downward direction in diagram)
circuit.add_edge("node_0", "node_1", matrix_op, 
                source_keys=["distribution", "policy"], target_key="distribution",
                edge_type="forward")

# FORWARD EDGE: node_1 → node_2 (rightward direction in diagram)
circuit.add_edge("node_1", "node_2", matrix_op, 
                source_keys=["distribution", "policy"], target_key="distribution",
                edge_type="forward")

# Verify the connections
print(f"Circuit has backward edges: {circuit.has_backward_edges}")  # True
print(f"Circuit has forward edges: {circuit.has_forward_edges}")  # True
print(f"Circuit is configured: {circuit.is_configured}")  # True
print(f"Circuit is initialized: {circuit.is_initialized}")  # False - needs input values
print(f"Circuit is solvable: {circuit.is_solvable}")  # False

#----------------------------------------------
# 4. SIGNAL INITIALIZATION
#----------------------------------------------
# Initialize with concrete values
# For CircuitCraft, we initialize:
# 1. Policy in initial node for backward path (node_1)
# 2. Distribution in terminal node for backward path (node_0)

# Initial policy function σⁿˣᵗ
σⁿˣᵗ = np.array([2, 3, 4])

# Initial distribution μ₀ (non-diagonal matrix with rich structure)
μ₀ = np.array([[1, 0.1, 0.2],        # Non-diagonal matrix
               [0.1, 2, 0.3],         # Has off-diagonal elements
               [0.2, 0.3, 3]])        # Similar to a covariance matrix

# Set initial values
circuit.set_node_data("node_1", {"policy": σⁿˣᵗ})
circuit.set_node_data("node_0", {"distribution": μ₀})

# Verify initialization status
print(f"Circuit is initialized: {circuit.is_initialized}")  # True
print(f"Circuit is solvable: {circuit.is_solvable}")  # True

#----------------------------------------------
# 5. OPERATION EXECUTION
#----------------------------------------------
# Execute the graph
# 1. First backward edges (node_1 → node_0)
# 2. Then forward edges (node_0 → node_1 → node_2)
results = circuit.solve()

print(f"Circuit solution complete: {circuit.is_solved}")  # True

# Inspect the results
σ = circuit.get_node_data("node_0", "policy")
μ₁ = circuit.get_node_data("node_1", "distribution")
μ₂ = circuit.get_node_data("node_2", "distribution")

print(f"σ = {σ}")  # [4, 9, 16]
print(f"μ₁ shape: {μ₁.shape}")  # (3, 3)
print(f"μ₂ shape: {μ₂.shape}")  # (3, 3)

#----------------------------------------------
# 6. STATE PERSISTENCE
#----------------------------------------------
# Save the solved circuit to a file
circuit.save("math_circuit.pkl")

# Later, load the circuit
loaded_circuit = Graph.load("math_circuit.pkl")
print(f"Loaded circuit state: {loaded_circuit.is_solved}")  # True

# Can also save a portable version (without computational objects)
# Create a schematic-only version
portable_circuit = circuit.to_portable()
print(f"Portable circuit has data: {portable_circuit.is_initialized}")  # False
print(f"Portable circuit is solved: {portable_circuit.is_solved}")  # False
"""

# Circuit Schematic:
#
#       Node_0: {σ, μ₀}
#           ↑       ↓
#           |       | FORWARD EDGE: (μ₀, σ → μ₁)
#           |       | MatrixOperation
#           |       |
#   BACKWARD|       |
#      EDGE:|       |
#   (σⁿˣᵗ → σ)|       |
#    Square op      |
#           |       ↓
#       Node_1: {σⁿˣᵗ, μ₁} ——→ Node_2: {None, μ₂}
#                             FORWARD EDGE: (μ₁, σⁿˣᵗ → μ₂)
#                             MatrixOperation
#
# This circuit demonstrates CircuitCraft's key elements:
# 1. Nodes store data (policy functions, distributions)
# 2. Edge direction determines operation type (backward/forward)
# 3. Operations are contained within edges
#
# Results from this circuit:
# 1. BACKWARD EDGE (node_1 → node_0):
#    σ = (σⁿˣᵗ)² = [4, 9, 16]         # Result of Square operation
# 
# 2. FORWARD EDGES:
#    a. node_0 → node_1:
#       μ₁ = μ₀ + 0.1 * (μ₀ @ outer_product(σ))  # First transformation
#    
#    b. node_1 → node_2:
#       μ₂ = μ₁ + 0.1 * (μ₁ @ outer_product(σⁿˣᵗ))  # Second transformation
#
# The workflow follows a standard pattern:
# 1. Component Definition - Define the operations
# 2. Layout Design - Create the structure
# 3. Connection Routing - Define relationships between components
# 4. Signal Initialization - Set initial values for computation
# 5. Operation Execution - Process operations to compute values
# 6. State Persistence - Save and load the circuit state
```

## Simplified Interface

For those who prefer a more concise approach, CircuitCraft offers high-level functions:

```python
from circuitcraft import create_and_solve_circuit, Operation
import numpy as np

# Define components
class Square(Operation):
    """Backward operation: Square a vector"""
    def __call__(self, x):
        return x**2

class MatrixOperation(Operation):
    """Forward operation: Transform matrix using vector"""
    def __call__(self, matrix, vector):
        import numpy as np
        v_column = vector.reshape(-1, 1)
        outer_product = v_column @ v_column.T
        return matrix + 0.1 * (matrix @ outer_product)

# Create and solve a circuit in one step
math_circuit = create_and_solve_circuit(
    name="QuickMathCircuit",
    # Define component layout
    nodes=[
        {"id": "node_0", "data_types": ["policy", "distribution"]},
        {"id": "node_1", "data_types": ["policy", "distribution"]},
        {"id": "node_2", "data_types": ["distribution"]}
    ],
    # Define connection topology
    edges=[
        {"source": "node_1", "target": "node_0", "operation": Square(), 
         "source_key": "policy", "target_key": "policy", "edge_type": "backward"},
        {"source": "node_0", "target": "node_1", "operation": MatrixOperation(),
         "source_keys": ["distribution", "policy"], "target_key": "distribution", "edge_type": "forward"},
        {"source": "node_1", "target": "node_2", "operation": MatrixOperation(),
         "source_keys": ["distribution", "policy"], "target_key": "distribution", "edge_type": "forward"},
    ],
    # Initialize values
    initial_values={
        "node_0": {"distribution": np.array([[1, 0.1, 0.2], [0.1, 2, 0.3], [0.2, 0.3, 3]])},
        "node_1": {"policy": np.array([2, 3, 4])}
    }
)

# Verify completion status
print(f"Circuit solution status: {math_circuit.is_solved}")  # True

# Access results
σ = math_circuit.get_node_data("node_0", "policy")
μ₁ = math_circuit.get_node_data("node_1", "distribution")
print(f"σ = {σ}")  # [4, 9, 16]
```

