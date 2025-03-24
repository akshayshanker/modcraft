# CircuitBoard API Reference

## Checking for Eulerian Cycles

A CircuitBoard is designed to form an Eulerian circuit where you can traverse from a 
terminal perch through all backward movers and then return to the same perch via all 
forward movers. You can check this property using the following method:

```python
def is_eulerian_circuit(self):
    """
    Check if this circuit forms an Eulerian cycle from terminal perches through
    backward movers and back via forward movers.
    
    Returns
    -------
    bool
        True if the circuit forms an Eulerian cycle, False otherwise
    """
    import networkx as nx
    
    # Check if both graphs have edges
    if not self.backward_graph.edges() or not self.forward_graph.edges():
        return False  # Need both backward and forward edges for a complete circuit
    
    # Get the terminal perches in the backward graph
    terminal_perches = self._get_terminal_perches("backward")
    if not terminal_perches:
        return False  # No terminal perches, cannot be Eulerian
    
    # Create a combined graph with both backward and forward edges
    combined_graph = nx.DiGraph()
    combined_graph.add_nodes_from(self.backward_graph.nodes())
    
    # Add edges with attributes indicating direction
    for u, v, data in self.backward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="backward")
    
    for u, v, data in self.forward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="forward")
    
    # For an Eulerian circuit in a directed graph:
    # 1. All nodes must have equal in-degree and out-degree
    # 2. All nodes must be in a single strongly connected component
    
    # Check in-degree equals out-degree for all nodes
    for node in combined_graph.nodes():
        if combined_graph.in_degree(node) != combined_graph.out_degree(node):
            return False
    
    # Check if graph is strongly connected (one SCC containing all nodes)
    if not nx.is_strongly_connected(combined_graph):
        return False
    
    # If we have terminal perches, check that there is a valid Eulerian cycle
    # that starts at a terminal perch, follows backward edges, and returns via forward edges
    for terminal_perch in terminal_perches:
        # See if we can find a valid path
        path = find_backward_forward_path(combined_graph, terminal_perch)
        if path:
            return True
    
    return False
```

## Finding an Eulerian Path

You can also find an explicit Eulerian path in the circuit:

```python
def find_eulerian_path(self):
    """
    Find an Eulerian path in the circuit, starting from a terminal perch,
    going through all backward movers, and returning via forward movers.
    
    Returns
    -------
    list or None
        A list of perch names forming the path, or None if no path exists
    """
    import networkx as nx
    
    # Check if both graphs have edges
    if not self.backward_graph.edges() or not self.forward_graph.edges():
        return None  # Need both backward and forward edges for a complete path
    
    # Create a combined graph with both backward and forward edges
    combined_graph = nx.DiGraph()
    combined_graph.add_nodes_from(self.backward_graph.nodes())
    
    # Add edges with attributes indicating direction
    for u, v, data in self.backward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="backward")
    
    for u, v, data in self.forward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="forward")
    
    # Get the terminal perches in the backward graph
    terminal_perches = self._get_terminal_perches("backward")
    if not terminal_perches:
        return None  # No terminal perches, cannot form Eulerian path
    
    # Try to find a valid path for each terminal perch
    for terminal_perch in terminal_perches:
        path = find_backward_forward_path(combined_graph, terminal_perch)
        if path:
            return path
    
    return None
```

## Helper Function for Finding Paths

The `find_backward_forward_path` function is used to find a valid path:

```python
def find_backward_forward_path(graph, start_node):
    """
    Find a path that starts at the given node, follows backward edges until it can't anymore,
    then follows forward edges back to the start node.
    
    Parameters
    ----------
    graph : nx.DiGraph
        The combined graph with edge_type attributes
    start_node : str
        The starting node (terminal perch)
    
    Returns
    -------
    list or None
        A valid path if found, None otherwise
    """
    import networkx as nx
    
    # Create subgraphs for backward and forward edges
    backward_edges = [(u, v) for u, v, data in graph.edges(data=True) 
                     if data.get('edge_type') == 'backward']
    forward_edges = [(u, v) for u, v, data in graph.edges(data=True) 
                    if data.get('edge_type') == 'forward']
    
    backward_graph = nx.DiGraph()
    backward_graph.add_nodes_from(graph.nodes())
    backward_graph.add_edges_from(backward_edges)
    
    forward_graph = nx.DiGraph()
    forward_graph.add_nodes_from(graph.nodes())
    forward_graph.add_edges_from(forward_edges)
    
    # Find all nodes reachable from start_node via backward edges
    initial_perches = set()
    for node in backward_graph.nodes():
        # If we can reach this node from the start_node via backward edges,
        # it's an initial perch from the perspective of our Eulerian path
        if nx.has_path(backward_graph, start_node, node):
            initial_perches.add(node)
    
    # For each initial perch, check if we can return to start_node via forward edges
    for initial_perch in initial_perches:
        if nx.has_path(forward_graph, initial_perch, start_node):
            # We found a valid path: start_node to initial_perch via backward edges,
            # then initial_perch back to start_node via forward edges
            try:
                backward_path = nx.shortest_path(backward_graph, start_node, initial_perch)
                forward_path = nx.shortest_path(forward_graph, initial_perch, start_node)
                return backward_path + forward_path[1:]  # Avoid duplicating the initial_perch
            except nx.NetworkXNoPath:
                # This should not happen given our checks, but handle it anyway
                continue
    
    return None
```

## Usage Example

```python
from circuitcraft import CircuitBoard, Perch

# Create a circuit
circuit = CircuitBoard(name="TestCircuit")

# Add perches
circuit.add_perch(Perch("perch_A", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_B", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_C", {"comp": None, "sim": None}))

# Connect with movers
circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_A",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

circuit.add_mover(
    source_name="perch_C", 
    target_name="perch_B",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

circuit.add_mover(
    source_name="perch_A", 
    target_name="perch_B",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_C",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

circuit.add_mover(
    source_name="perch_C", 
    target_name="perch_A",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

# Check if the circuit forms an Eulerian cycle
is_eulerian = circuit.is_eulerian_circuit()
print(f"The circuit is Eulerian: {is_eulerian}")  # Should be True

# Find an explicit Eulerian path
path = circuit.find_eulerian_path()
if path:
    print("Eulerian path found:")
    print(" -> ".join(path))
else:
    print("No Eulerian path found.")
```

## Visualizing the Eulerian Circuit

CircuitCraft also provides a method to visualize the Eulerian circuit:

```python
def visualize_eulerian_path(self, path=None):
    """
    Generate a visualization of the Eulerian path in the circuit.
    
    Parameters
    ----------
    path : list, optional
        The Eulerian path to highlight. If None, attempt to find one.
        
    Returns
    -------
    matplotlib.figure.Figure
        The figure containing the visualization
    """
    # Implementation uses matplotlib and networkx drawing functions
    # to create a graph visualization with backward edges in blue,
    # forward edges in red, and the Eulerian path highlighted
```

Example usage:

```python
# Visualize the Eulerian path
fig = circuit.visualize_eulerian_path()
fig.savefig("eulerian_circuit.png")
```
