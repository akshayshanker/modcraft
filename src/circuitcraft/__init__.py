"""
CircuitCraft - A framework for computational circuits in economics.

In CircuitCraft, computational circuits represent inputs and outputs of functional
operators as nodes, with the operators themselves as edges between them.

This approach is particularly valuable for economic problems, where the data are
themselves functions that have meaningful functional relationships to each other
even after they have been solved.
"""

# Version information
__version__ = "1.0.0"  # Major update: Evolution from GraphCraft to CircuitCraft with sequential circuit design

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import pickle
from pathlib import Path

from .graph import Graph
from .node import Node

__all__ = [
    'Graph',
    'Node',
    'create_and_solve_circuit',
    'create_and_solve_backward_circuit',
    'create_and_solve_forward_circuit',
    '__version__'
]

def create_and_solve_circuit(name: str, 
                            nodes: List[Dict[str, Any]],
                            edges: List[Dict[str, Any]],
                            initial_values: Optional[Dict[str, Dict[str, Any]]] = None) -> Graph:
    """
    Create and solve a circuit using the 4-step workflow.
    
    This high-level function combines all steps of the CircuitCraft workflow:
    1. Circuit Creation: Create the graph structure with nodes and edges
    2. Configuration: Assign operations to edges
    3. Initialization: Provide initial values for node data
    4. Solution: Execute operations to compute results
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of node specifications, each should contain:
        - 'id': str - Node identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types and optional initial values
    edges : List[Dict[str, Any]]
        List of edge specifications, each should contain:
        - 'source': str - Source node ID
        - 'target': str - Target node ID
        - 'operation': Callable - Function to execute
        - 'source_key': str or 'source_keys': List[str] - Source data key(s)
        - 'target_key': str - Target data key
        - 'edge_type': str - "forward" or "backward"
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for nodes, keyed by node ID and then by data key.
        
    Returns
    -------
    Graph
        A fully configured and solved circuit.
        
    Raises
    ------
    ValueError
        If the circuit creation fails or the circuit is not solvable.
    """
    # 1. Create circuit structure
    circuit = Graph(name=name)
    
    # Add nodes
    for node_spec in nodes:
        node_id = node_spec['id']
        data_types = node_spec.get('data_types', {})
        node = Node(node_id, data_types)
        circuit.add_node(node)
    
    # Add edges (structure only)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        edge_type = edge_spec.get('edge_type', 'forward')
        circuit.add_edge(source, target, edge_type=edge_type)
    
    # 2. Configure (assign operations to edges)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        operation = edge_spec['operation']
        edge_type = edge_spec.get('edge_type', 'forward')
        
        # Handle source keys
        source_key = edge_spec.get('source_key')
        source_keys = edge_spec.get('source_keys')
        target_key = edge_spec['target_key']
        
        if source_key is not None:
            circuit.set_edge_operation(source, target, operation,
                                    source_key=source_key, target_key=target_key,
                                    edge_type=edge_type)
        else:
            circuit.set_edge_operation(source, target, operation,
                                    source_keys=source_keys, target_key=target_key,
                                    edge_type=edge_type)
    
    # Validate configuration
    circuit.configure()
    
    # 3. Initialize with values
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_node_data(node_id, values)
        circuit.is_initialized = True
    
    # 4. Solve circuit
    if circuit.is_solvable:
        circuit.solve()
    else:
        raise ValueError("Circuit is not solvable with the provided initial values")
    
    return circuit

def create_and_solve_backward_circuit(name: str, 
                                    nodes: List[Dict[str, Any]],
                                    edges: List[Dict[str, Any]],
                                    initial_values: Optional[Dict[str, Dict[str, Any]]] = None) -> Graph:
    """
    Create a circuit and solve only the backward operations using the 4-step workflow.
    
    This is useful when you only need to compute backward solving operations
    (e.g., Coleman operator in economic models) without forward operations.
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of node specifications, each should contain:
        - 'id': str - Node identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types and optional initial values
    edges : List[Dict[str, Any]]
        List of edge specifications, each should contain:
        - 'source': str - Source node ID
        - 'target': str - Target node ID
        - 'operation': Callable - Function to execute
        - 'source_key': str or 'source_keys': List[str] - Source data key(s)
        - 'target_key': str - Target data key
        - 'edge_type': str - "forward" or "backward"
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for nodes, keyed by node ID and then by data key.
        
    Returns
    -------
    Graph
        A circuit with backward operations solved.
        
    Raises
    ------
    ValueError
        If the circuit creation fails or the circuit is not solvable.
    """
    # 1. Create circuit structure
    circuit = Graph(name=name)
    
    # Add nodes
    for node_spec in nodes:
        node_id = node_spec['id']
        data_types = node_spec.get('data_types', {})
        node = Node(node_id, data_types)
        circuit.add_node(node)
    
    # Add edges (structure only)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        edge_type = edge_spec.get('edge_type', 'forward')
        circuit.add_edge(source, target, edge_type=edge_type)
    
    # 2. Configure (assign operations to edges)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        operation = edge_spec['operation']
        edge_type = edge_spec.get('edge_type', 'forward')
        
        # Handle source keys
        source_key = edge_spec.get('source_key')
        source_keys = edge_spec.get('source_keys')
        target_key = edge_spec['target_key']
        
        if source_key is not None:
            circuit.set_edge_operation(source, target, operation,
                                    source_key=source_key, target_key=target_key,
                                    edge_type=edge_type)
        else:
            circuit.set_edge_operation(source, target, operation,
                                    source_keys=source_keys, target_key=target_key,
                                    edge_type=edge_type)
    
    # Validate configuration
    circuit.configure()
    
    # 3. Initialize with values
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_node_data(node_id, values)
        circuit.is_initialized = True
    
    # 4. Solve only backward operations
    if circuit.is_solvable:
        circuit.solve_backward()
    else:
        raise ValueError("Circuit is not solvable with the provided initial values")
    
    return circuit

def create_and_solve_forward_circuit(name: str, 
                                   nodes: List[Dict[str, Any]],
                                   edges: List[Dict[str, Any]],
                                   initial_values: Optional[Dict[str, Dict[str, Any]]] = None) -> Graph:
    """
    Create a circuit and solve only the forward operations using the 4-step workflow.
    
    This is useful when you only need to compute forward operations
    (e.g., push-forward operations in economic models) without backward solving.
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of node specifications, each should contain:
        - 'id': str - Node identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types and optional initial values
    edges : List[Dict[str, Any]]
        List of edge specifications, each should contain:
        - 'source': str - Source node ID
        - 'target': str - Target node ID
        - 'operation': Callable - Function to execute
        - 'source_key': str or 'source_keys': List[str] - Source data key(s)
        - 'target_key': str - Target data key
        - 'edge_type': str - "forward" or "backward"
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for nodes, keyed by node ID and then by data key.
        
    Returns
    -------
    Graph
        A circuit with forward operations solved.
        
    Raises
    ------
    ValueError
        If the circuit creation fails or the circuit is not solvable.
    """
    # 1. Create circuit structure
    circuit = Graph(name=name)
    
    # Add nodes
    for node_spec in nodes:
        node_id = node_spec['id']
        data_types = node_spec.get('data_types', {})
        node = Node(node_id, data_types)
        circuit.add_node(node)
    
    # Add edges (structure only)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        edge_type = edge_spec.get('edge_type', 'forward')
        circuit.add_edge(source, target, edge_type=edge_type)
    
    # 2. Configure (assign operations to edges)
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        operation = edge_spec['operation']
        edge_type = edge_spec.get('edge_type', 'forward')
        
        # Handle source keys
        source_key = edge_spec.get('source_key')
        source_keys = edge_spec.get('source_keys')
        target_key = edge_spec['target_key']
        
        if source_key is not None:
            circuit.set_edge_operation(source, target, operation,
                                    source_key=source_key, target_key=target_key,
                                    edge_type=edge_type)
        else:
            circuit.set_edge_operation(source, target, operation,
                                    source_keys=source_keys, target_key=target_key,
                                    edge_type=edge_type)
    
    # Validate configuration
    circuit.configure()
    
    # 3. Initialize with values
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_node_data(node_id, values)
        circuit.is_initialized = True
    
    # 4. Solve only forward operations
    if circuit.is_solvable:
        circuit.solve_forward()
    else:
        raise ValueError("Circuit is not solvable with the provided initial values")
    
    return circuit 