"""
CircuitCraft - A framework for computational circuits in economics.

In CircuitCraft, computational circuits represent inputs and outputs of functional
operators as perches, with the operators themselves as movers between them.

This approach is particularly valuable for economic problems, where the data are
themselves functions that have meaningful functional relationships to each other
even after they have been solved.
"""

# Version information
__version__ = "1.3.1"  # Updated from 1.3.0: Renamed perch.comp to perch.up and perch.sim to perch.down

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import pickle
from pathlib import Path
import networkx as nx
from networkx.exception import NetworkXUnfeasible

from .circuit_board import CircuitBoard
from .perch import Perch
from .mover import Mover
from .eulerian import add_to_circuit_board

# Add Eulerian circuit functionality to CircuitBoard
add_to_circuit_board()

__all__ = [
    'CircuitBoard',
    'Perch',
    'Mover',
    'create_and_solve_circuit',
    'create_and_solve_backward_circuit',
    'create_and_solve_forward_circuit',
    '__version__'
]

def create_and_solve_circuit(name: str, 
                            nodes: List[Dict[str, Any]],
                            edges: List[Dict[str, Any]],
                            initial_values: Optional[Dict[str, Dict[str, Any]]] = None
                            ) -> CircuitBoard:
    """
    Create and solve a circuit using the workflow: 
    Create -> Finalize Model -> Make Portable -> Initialize -> Solve
    
    This function encapsulates the full circuit creation and solution process
    in a single call, making it easier to use for simple cases.
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of perch specifications, each should contain:
        - 'id': str - Perch identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types (should include 
          'comp' and 'sim')
    edges : List[Dict[str, Any]]
        List of mover specifications, each should contain:
        - 'source': str - Source perch id
        - 'target': str - Target perch id
        - 'edge_type': str - "forward" or "backward"
        - 'operation': Callable or Dict - Operation or map to attach to the mover
        - 'source_key': str (optional) - Key in source perch to read from
        - 'source_keys': List[str] (optional) - Multiple keys in source perch to 
          read from
        - 'target_key': str (optional) - Key in target perch to write to
        - 'parameters': Dict[str, Any] (optional) - Problem-specific parameters
        - 'numerical_hyperparameters': Dict[str, Any] (optional) - Computational 
          tuning values
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for perches, keyed by perch id and then by data key.
        
    Returns
    -------
    CircuitBoard
        The created and solved circuit board.
        
    Examples
    --------
    >>> circuit = create_and_solve_circuit(
    ...     name="SimpleCircuit",
    ...     nodes=[
    ...         {"id": "perch_0", "data_types": ["comp", "sim"]},
    ...         {"id": "perch_1", "data_types": ["comp", "sim"]}
    ...     ],
    ...     edges=[
    ...         {"source": "perch_1", "target": "perch_0", "operation": backward_op, 
    ...          "source_key": "comp", "target_key": "comp", "edge_type": "backward"},
    ...         {"source": "perch_0", "target": "perch_1", "operation": forward_op,
    ...          "source_keys": ["comp", "sim"], "target_key": "sim", 
    ...          "edge_type": "forward"}
    ...     ],
    ...     initial_values={
    ...         "perch_0": {"comp": None, "sim": initial_sim},
    ...         "perch_1": {"comp": initial_comp, "sim": None}
    ...     }
    ... )
    """
    # 1) Create the circuit
    circuit = CircuitBoard(name=name)
    
    # Add perches
    for node_spec in nodes:
        node_id = node_spec['id']
        # Convert data_types to dict if it's a list
        if isinstance(node_spec.get('data_types', {}), list):
            data_types = {key: None for key in node_spec['data_types']}
        else:
            data_types = node_spec.get('data_types', {})
        
        # Ensure data has up and down (formerly comp and sim)
        if 'up' not in data_types:
            data_types['up'] = None
        if 'down' not in data_types:
            data_types['down'] = None
            
        circuit.add_perch(Perch(node_id, data_types))
    
    # Add movers
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        edge_type = edge_spec.get('edge_type', 'forward')
        operation = edge_spec.get('operation')
        source_key = edge_spec.get('source_key')
        source_keys = edge_spec.get('source_keys')
        target_key = edge_spec.get('target_key')
        parameters = edge_spec.get('parameters', {})
        numerical_hyperparameters = edge_spec.get('numerical_hyperparameters', {})
        
        # If an operation is provided, extract map and comp
        map_data = None
        comp_func = None
        
        if operation is not None:
            if callable(operation):
                # If operation is a callable, use it directly as comp
                comp_func = operation
            elif isinstance(operation, dict):
                # If operation is a dict, use it as the map
                map_data = operation
            else:
                # Otherwise, create a simple map with the operation
                map_data = {'operation': operation}
        
        # Add the mover to the circuit
        circuit.add_mover(
            source_name=source,
            target_name=target,
            map_data=map_data,
            parameters=parameters,
            numerical_hyperparameters=numerical_hyperparameters,
            source_key=source_key,
            source_keys=source_keys,
            target_key=target_key,
            edge_type=edge_type
        )
        
        # If we have a comp function, set it directly
        if comp_func is not None:
            circuit.set_mover_comp(source, target, edge_type, comp_func)
    
    # 2) Finalize the model
    circuit.finalize_model()
    
    # 3) Make the circuit portable
    def comp_factory(data):
        """Create a comp function from a map"""
        map_data = data.get('map', {})
        parameters = data.get('parameters', {})
        
        def comp(data_dict):
            """
            Default comp implementation - returns an empty dictionary
            This will be overridden by any explicit comp functions
            """
            return {}
        
        return comp
    
    circuit.make_portable(comp_factory)
    
    # 4) Initialize the circuit
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_perch_data(node_id, values)
    
    # 5) Solve the circuit
    circuit.solve()
    
    return circuit

def create_and_solve_backward_circuit(
    name: str, 
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    initial_values: Optional[Dict[str, Dict[str, Any]]] = None
) -> CircuitBoard:
    """
    Create and solve a backward-only circuit.
    
    This is a specialized version of create_and_solve_circuit that only
    creates and solves backward edges. Useful for policy function iteration
    without forward simulation.
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of perch specifications, each should contain:
        - 'id': str - Perch identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types (should include 
          'comp')
    edges : List[Dict[str, Any]]
        List of backward mover specifications, each should contain:
        - 'source': str - Source perch id
        - 'target': str - Target perch id
        - 'operation': Callable or Dict - Operation or map to attach to the mover
        - 'source_key': str (optional) - Key in source perch to read from 
          (default: 'comp')
        - 'target_key': str (optional) - Key in target perch to write to 
          (default: 'comp')
        - 'parameters': Dict[str, Any] (optional) - Problem-specific parameters
        - 'numerical_hyperparameters': Dict[str, Any] (optional) - Computational 
          tuning values
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for perches, keyed by perch id and then by data key.
        
    Returns
    -------
    CircuitBoard
        The created and solved circuit board with backward edges only.
    """
    # 1) Create the circuit
    circuit = CircuitBoard(name=name)
    
    # Add perches
    for node_spec in nodes:
        node_id = node_spec['id']
        # Convert data_types to dict if it's a list
        if isinstance(node_spec.get('data_types', {}), list):
            data_types = {key: None for key in node_spec['data_types']}
        else:
            data_types = node_spec.get('data_types', {})
        
        # Ensure data has up
        if 'up' not in data_types:
            data_types['up'] = None
            
        circuit.add_perch(Perch(node_id, data_types))
    
    # Add backward movers
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        operation = edge_spec.get('operation')
        source_key = edge_spec.get('source_key', 'up')
        target_key = edge_spec.get('target_key', 'up')
        parameters = edge_spec.get('parameters', {})
        numerical_hyperparameters = edge_spec.get('numerical_hyperparameters', {})
        
        # If an operation is provided, extract map and comp
        map_data = None
        comp_func = None
        
        if operation is not None:
            if callable(operation):
                # If operation is a callable, use it directly as comp
                comp_func = operation
            elif isinstance(operation, dict):
                # If operation is a dict, use it as the map
                map_data = operation
            else:
                # Otherwise, create a simple map with the operation
                map_data = {'operation': operation}
        
        # Add the backward mover to the circuit
        circuit.add_mover(
            source_name=source,
            target_name=target,
            map_data=map_data,
            parameters=parameters,
            numerical_hyperparameters=numerical_hyperparameters,
            source_key=source_key,
            target_key=target_key,
            edge_type="backward"
        )
        
        # If we have a comp function, set it directly
        if comp_func is not None:
            circuit.set_mover_comp(source, target, "backward", comp_func)
    
    # 2) Finalize the model
    circuit.finalize_model()
    
    # 3) Make the circuit portable
    def comp_factory(data):
        """Create a comp function from a map"""
        map_data = data.get('map', {})
        parameters = data.get('parameters', {})
        
        def comp(data_dict):
            """
            Default comp implementation - returns an empty dictionary
            This will be overridden by any explicit comp functions
            """
            return {}
        
        return comp
    
    circuit.make_portable(comp_factory)
    
    # 4) Initialize the circuit
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_perch_data(node_id, values)
    
    # 5) Solve the circuit
    circuit.solve(backward_only=True)
    
    return circuit

def create_and_solve_forward_circuit(
    name: str, 
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    initial_values: Optional[Dict[str, Dict[str, Any]]] = None
) -> CircuitBoard:
    """
    Create and solve a forward-only circuit.
    
    This is a specialized version of create_and_solve_circuit that only
    creates and solves forward edges. Useful for simulations using
    pre-computed policy functions.
    
    Parameters
    ----------
    name : str
        Name of the circuit.
    nodes : List[Dict[str, Any]]
        List of perch specifications, each should contain:
        - 'id': str - Perch identifier
        - 'data_types': Dict[str, Any] - Dictionary of data types (should include 
          'sim')
    edges : List[Dict[str, Any]]
        List of forward mover specifications, each should contain:
        - 'source': str - Source perch id
        - 'target': str - Target perch id
        - 'operation': Callable or Dict - Operation or map to attach to the mover
        - 'source_key': str (optional) - Key in source perch to read from
        - 'source_keys': List[str] (optional) - Multiple keys in source perch to 
          read from
        - 'target_key': str (optional) - Key in target perch to write to 
          (default: 'sim')
        - 'parameters': Dict[str, Any] (optional) - Problem-specific parameters
        - 'numerical_hyperparameters': Dict[str, Any] (optional) - Computational 
          tuning values
    initial_values : Dict[str, Dict[str, Any]], optional
        Initial values for perches, keyed by perch id and then by data key.
        
    Returns
    -------
    CircuitBoard
        The created and solved circuit board with forward edges only.
    """
    # 1) Create the circuit
    circuit = CircuitBoard(name=name)
    
    # Add perches
    for node_spec in nodes:
        node_id = node_spec['id']
        # Convert data_types to dict if it's a list
        if isinstance(node_spec.get('data_types', {}), list):
            data_types = {key: None for key in node_spec['data_types']}
        else:
            data_types = node_spec.get('data_types', {})
        
        # Ensure data has sim
        if 'sim' not in data_types:
            data_types['sim'] = None
            
        circuit.add_perch(Perch(node_id, data_types))
    
    # Add forward movers
    for edge_spec in edges:
        source = edge_spec['source']
        target = edge_spec['target']
        operation = edge_spec.get('operation')
        source_key = edge_spec.get('source_key')
        source_keys = edge_spec.get('source_keys')
        target_key = edge_spec.get('target_key', 'sim')
        parameters = edge_spec.get('parameters', {})
        numerical_hyperparameters = edge_spec.get('numerical_hyperparameters', {})
        
        # Validate source keys
        if source_key is not None and source_keys is not None:
            raise ValueError("Provide either source_key or source_keys, but not both")
        
        # If an operation is provided, extract map and comp
        map_data = None
        comp_func = None
        
        if operation is not None:
            if callable(operation):
                # If operation is a callable, use it directly as comp
                comp_func = operation
            elif isinstance(operation, dict):
                # If operation is a dict, use it as the map
                map_data = operation
            else:
                # Otherwise, create a simple map with the operation
                map_data = {'operation': operation}
        
        # Add the forward mover to the circuit
        circuit.add_mover(
            source_name=source,
            target_name=target,
            map_data=map_data,
            parameters=parameters,
            numerical_hyperparameters=numerical_hyperparameters,
            source_key=source_key,
            source_keys=source_keys,
            target_key=target_key,
            edge_type="forward"
        )
        
        # If we have a comp function, set it directly
        if comp_func is not None:
            circuit.set_mover_comp(source, target, "forward", comp_func)
    
    # 2) Finalize the model
    circuit.finalize_model()
    
    # 3) Make the circuit portable
    def comp_factory(data):
        """Create a comp function from a map"""
        map_data = data.get('map', {})
        parameters = data.get('parameters', {})
        
        def comp(data_dict):
            """
            Default comp implementation - returns an empty dictionary
            This will be overridden by any explicit comp functions
            """
            return {}
        
        return comp
    
    circuit.make_portable(comp_factory)
    
    # 4) Initialize the circuit
    if initial_values:
        for node_id, values in initial_values.items():
            circuit.set_perch_data(node_id, values)
    
    # Mark the circuit as solved so we can do forward simulation without backward solve
    circuit.is_solved = True
    
    # 5) Solve the circuit (forward only)
    circuit.solve(forward_only=True)
    
    return circuit