"""
Eulerian circuit checking functionality for CircuitCraft.

This module provides methods to check if a CircuitBoard forms an Eulerian circuit,
particularly one that starts at a terminal perch, traverses through backward movers,
and returns to the terminal perch via forward movers.
"""

import networkx as nx
from .circuit_board import CircuitBoard

def is_eulerian_circuit(circuit: CircuitBoard) -> bool:
    """
    Check if a circuit forms an Eulerian cycle from terminal perches through
    backward movers and back via forward movers.
    
    Parameters
    ----------
    circuit : CircuitBoard
        The circuit to check
        
    Returns
    -------
    bool
        True if the circuit forms an Eulerian cycle, False otherwise
    """
    # Check if both graphs have edges
    if not circuit.backward_graph.edges() or not circuit.forward_graph.edges():
        return False  # Need both backward and forward edges for a complete circuit
    
    # Get the terminal perches in the backward graph
    terminal_perches = circuit._get_terminal_perches("backward")
    if not terminal_perches:
        return False  # No terminal perches, cannot be Eulerian
    
    # Create a combined graph with both backward and forward edges
    # but with appropriate attributes to distinguish them
    combined_graph = nx.DiGraph()
    
    # Add nodes from either graph (they should have the same nodes)
    combined_graph.add_nodes_from(circuit.backward_graph.nodes())
    
    # Add edges with attributes indicating direction
    for u, v, data in circuit.backward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="backward")
    
    for u, v, data in circuit.forward_graph.edges(data=True):
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

def find_eulerian_path(circuit: CircuitBoard):
    """
    Find an Eulerian path in the circuit, starting from a terminal perch,
    going through all backward movers, and returning via forward movers.
    
    Parameters
    ----------
    circuit : CircuitBoard
        The circuit to check
        
    Returns
    -------
    list or None
        A list of perch names forming the path, or None if no path exists
    """
    # Check if both graphs have edges
    if not circuit.backward_graph.edges() or not circuit.forward_graph.edges():
        return None  # Need both backward and forward edges for a complete path
    
    # Create a combined graph with both backward and forward edges
    combined_graph = nx.DiGraph()
    combined_graph.add_nodes_from(circuit.backward_graph.nodes())
    
    # Add edges with attributes indicating direction
    for u, v, data in circuit.backward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="backward")
    
    for u, v, data in circuit.forward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="forward")
    
    # Get the terminal perches in the backward graph
    terminal_perches = circuit._get_terminal_perches("backward")
    if not terminal_perches:
        return None  # No terminal perches, cannot form Eulerian path
    
    # Try to find a valid path for each terminal perch
    for terminal_perch in terminal_perches:
        path = find_backward_forward_path(combined_graph, terminal_perch)
        if path:
            return path
    
    return None

def visualize_eulerian_path(circuit: CircuitBoard, path=None):
    """
    Generate a visualization of the Eulerian path in the circuit.
    
    Parameters
    ----------
    circuit : CircuitBoard
        The circuit to visualize
    path : list, optional
        The Eulerian path to highlight. If None, attempt to find one.
        
    Returns
    -------
    matplotlib.figure.Figure
        The figure containing the visualization
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
    except ImportError:
        raise ImportError("Matplotlib is required for visualization. Install with 'pip install matplotlib'")
    
    if path is None:
        path = find_eulerian_path(circuit)
    
    # Create a figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create a combined graph for visualization
    combined_graph = nx.DiGraph()
    combined_graph.add_nodes_from(circuit.backward_graph.nodes())
    
    # Add backward edges
    for u, v, data in circuit.backward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="backward")
    
    # Add forward edges
    for u, v, data in circuit.forward_graph.edges(data=True):
        combined_graph.add_edge(u, v, edge_type="forward")
    
    # Get positions for nodes using a layout algorithm
    pos = nx.spring_layout(combined_graph)
    
    # Draw network background
    nx.draw_networkx_nodes(combined_graph, pos, ax=ax, node_color='lightgray', node_size=500)
    
    # Draw node labels
    nx.draw_networkx_labels(combined_graph, pos, ax=ax)
    
    # Draw edges with different colors for backward and forward
    backward_edges = [(u, v) for u, v, data in combined_graph.edges(data=True) 
                     if data.get('edge_type') == 'backward']
    forward_edges = [(u, v) for u, v, data in combined_graph.edges(data=True) 
                    if data.get('edge_type') == 'forward']
    
    nx.draw_networkx_edges(combined_graph, pos, ax=ax, edgelist=backward_edges, 
                          edge_color='blue', arrows=True, width=1.5,
                          label='Backward')
    nx.draw_networkx_edges(combined_graph, pos, ax=ax, edgelist=forward_edges, 
                          edge_color='red', arrows=True, width=1.5,
                          label='Forward')
    
    # Highlight the path if provided
    if path:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        edge_colors = []
        for u, v in path_edges:
            if any(u == edge[0] and v == edge[1] for edge in backward_edges):
                edge_colors.append('darkblue')
            else:
                edge_colors.append('darkred')
        
        nx.draw_networkx_edges(combined_graph, pos, ax=ax, edgelist=path_edges, 
                              edge_color=edge_colors, arrows=True, width=3.0)
        plt.title("Eulerian Circuit in CircuitCraft")
    else:
        plt.title("Circuit Visualization (No Eulerian Circuit Found)")
    
    plt.legend()
    plt.tight_layout()
    
    return fig

# Add these methods to CircuitBoard class
def add_to_circuit_board():
    """Add eulerian methods to CircuitBoard class"""
    CircuitBoard.is_eulerian_circuit = is_eulerian_circuit
    CircuitBoard.find_eulerian_path = find_eulerian_path
    CircuitBoard.visualize_eulerian_path = visualize_eulerian_path 