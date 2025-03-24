import pickle
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

import networkx as nx

from .node import Node


class Graph:
    """
    A circuit in CircuitCraft represented as a directed graph.
    
    In CircuitCraft, circuits are represented as graphs where:
    - Nodes store data (policy functions, distributions)
    - Edges contain operations (functions that transform data)
    
    The graph maintains both backward and forward edges:
    - Backward edges: For operations like Coleman solving (successor to predecessor)
    - Forward edges: For operations like push-forward (predecessor to successor)
    
    The graph follows a clear workflow:
    1. Circuit Creation: Create the graph structure with nodes and edges and parameters
    2. Configuration: Set up nodes and edges with operations
    3. Initialization: Provide initial values for node data
    4. Solution: Execute operations to compute results node by node
    
    The graph tracks its state through boolean flags:
    - is_configured: Graph structure is complete (nodes and edges defined)
    - is_initialized: Initial values are provided
    - is_solvable: Ready for computation
    - is_solved: Computation is complete
    """
    
    def __init__(self, name: str = "circuit"):
        """
        Initialize a circuit graph.
        
        Parameters
        ----------
        name : str, optional
            Name of the circuit, default is "circuit".
        """
        self.name = name
        self.nodes: Dict[str, Node] = {}
        
        # Use two separate directed graphs for backward and forward operations
        self.backward_graph = nx.DiGraph()
        self.forward_graph = nx.DiGraph()
        
        # Edge data storage
        self.edges: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        
        # State tracking
        self._configured = False
        self._initialized = False
        self._solved = False
    
    def add_node(self, node: Node) -> None:
        """
        Add a node to the circuit.
        
        Part of the Circuit Creation step.
        
        Parameters
        ----------
        node : Node
            The node to add.
            
        Raises
        ------
        ValueError
            If a node with the same name already exists.
        """
        if node.name in self.nodes:
            raise ValueError(f"Node with name '{node.name}' already exists")
        
        self.nodes[node.name] = node
        self.backward_graph.add_node(node.name)
        self.forward_graph.add_node(node.name)
    
    def add_edge(self, source_name: str, target_name: str,
                source_key: Optional[str] = None, source_keys: Optional[List[str]] = None,
                target_key: Optional[str] = None, edge_type: str = "forward") -> None:
        """
        Add an edge to the circuit without operations.
        
        Part of the Circuit Creation step. This only creates the graph structure
        without assigning operations, which are assigned during the Configuration step.
        
        Parameters
        ----------
        source_name : str
            Name of the source node.
        target_name : str
            Name of the target node.
        source_key : str, optional
            Single source data key if only one source key is needed.
        source_keys : List[str], optional
            List of source data keys if multiple source keys are needed.
        target_key : str, optional
            Target data key where the result will be stored.
        edge_type : str, optional
            Type of edge: "forward" or "backward", default is "forward".
            Forward edges: source → target (push-forward operations)
            Backward edges: target → source (backward solving operations)
            
        Raises
        ------
        ValueError
            If source_key and source_keys are both provided or both None,
            or if the nodes don't exist.
        """
        # Validate nodes exist
        if source_name not in self.nodes:
            raise ValueError(f"Source node '{source_name}' doesn't exist")
        if target_name not in self.nodes:
            raise ValueError(f"Target node '{target_name}' doesn't exist")
        
        # Validate source key(s)
        if (source_key is None and source_keys is None):
            source_keys = []  # No source keys specified, will be set during configuration
        elif (source_key is not None and source_keys is not None):
            raise ValueError("Provide either source_key or source_keys, but not both")
        
        # Convert single source_key to list for consistent handling
        if source_key is not None:
            source_keys = [source_key]
        
        # Add edge to appropriate graph
        if edge_type == "forward":
            self.forward_graph.add_edge(source_name, target_name)
        else:  # backward
            self.backward_graph.add_edge(target_name, source_name)
        
        # Store edge data with placeholders for operations
        edge_key = (source_name, target_name, edge_type)
        self.edges[edge_key] = {
            'backward_func': None,
            'forward_func': None,
            'source_keys': source_keys,
            'target_key': target_key
        }
    
    def set_edge_operation(self, source_name: str, target_name: str, 
                          operation: Union[Callable, Tuple[Optional[Callable], Optional[Callable]]],
                          source_key: Optional[str] = None, source_keys: Optional[List[str]] = None,
                          target_key: Optional[str] = None, edge_type: str = "forward") -> None:
        """
        Assign an operation to an existing edge.
        
        Part of the Configuration step. This assigns operations to edges that were
        created during the Circuit Creation step.
        
        Parameters
        ----------
        source_name : str
            Name of the source node.
        target_name : str
            Name of the target node.
        operation : Callable or Tuple[Optional[Callable], Optional[Callable]]
            Function(s) to attach to the edge. Can be:
            - A single function (used for both forward and backward operations)
            - A tuple (backward_func, forward_func) where either can be None
        source_key : str, optional
            Single source data key if only one source key is needed.
        source_keys : List[str], optional
            List of source data keys if multiple source keys are needed.
        target_key : str
            Target data key where the result will be stored.
        edge_type : str, optional
            Type of edge: "forward" or "backward", default is "forward".
            
        Raises
        ------
        ValueError
            If the edge doesn't exist, if source_key and source_keys are both provided or both None,
            or if the operation doesn't support the requested operation type.
        """
        # Check if edge exists
        edge_key = (source_name, target_name, edge_type)
        if edge_key not in self.edges:
            raise ValueError(f"No edge exists from '{source_name}' to '{target_name}' with type '{edge_type}'")
        
        # Validate source key(s)
        if (source_key is None and source_keys is None) or \
           (source_key is not None and source_keys is not None):
            raise ValueError("Provide either source_key or source_keys, but not both")
        
        # Convert single source_key to list for consistent handling
        if source_key is not None:
            source_keys = [source_key]
        
        # Validate target_key
        if target_key is None:
            raise ValueError("target_key must be provided")
        
        # Validate keys exist in nodes
        source_node = self.nodes[source_name]
        target_node = self.nodes[target_name]
        
        for key in source_keys:
            if key not in source_node.get_data_keys():
                raise ValueError(f"Source key '{key}' not found in node '{source_name}'")
        
        if target_key not in target_node.get_data_keys():
            raise ValueError(f"Target key '{target_key}' not found in node '{target_name}'")
        
        # Process operation
        backward_func = None
        forward_func = None
        
        if callable(operation):
            # If a single function is provided, use it for the specified edge type
            if edge_type == "forward":
                forward_func = operation
            else:  # backward
                backward_func = operation
        elif isinstance(operation, tuple) and len(operation) == 2:
            # If a tuple of (backward_func, forward_func) is provided, extract them
            backward_func, forward_func = operation
        else:
            raise ValueError("Operation must be a callable or a tuple of (backward_func, forward_func)")
        
        # Validate operation type
        if edge_type == "forward" and forward_func is None:
            raise ValueError("No forward function provided for forward edge")
        if edge_type == "backward" and backward_func is None:
            raise ValueError("No backward function provided for backward edge")
        
        # Update edge data with operation and keys
        edge_data = self.edges[edge_key]
        edge_data['backward_func'] = backward_func
        edge_data['forward_func'] = forward_func
        edge_data['source_keys'] = source_keys
        edge_data['target_key'] = target_key
    
    def configure(self) -> None:
        """
        Configure the circuit.
        
        This is the explicit Configuration step in the workflow. It verifies that
        all edges have operations assigned and marks the circuit as configured.
        
        Raises
        ------
        ValueError
            If any edge is missing operations or if the circuit structure is invalid.
        """
        # Validate that all nodes have the necessary data keys
        for edge_key, edge_data in self.edges.items():
            source_name, target_name, edge_type = edge_key
            source_keys = edge_data['source_keys']
            target_key = edge_data['target_key']
            
            # Verify source and target nodes exist
            if source_name not in self.nodes:
                raise ValueError(f"Source node '{source_name}' doesn't exist")
            if target_name not in self.nodes:
                raise ValueError(f"Target node '{target_name}' doesn't exist")
            
            # Verify operations are assigned
            if edge_type == "forward" and edge_data['forward_func'] is None:
                raise ValueError(f"Forward operation not assigned for edge from '{source_name}' to '{target_name}'")
            if edge_type == "backward" and edge_data['backward_func'] is None:
                raise ValueError(f"Backward operation not assigned for edge from '{target_name}' to '{source_name}'")
            
            # Verify source keys are specified
            if not source_keys:
                raise ValueError(f"Source keys not specified for edge from '{source_name}' to '{target_name}'")
            
            # Verify target key is specified
            if target_key is None:
                raise ValueError(f"Target key not specified for edge from '{source_name}' to '{target_name}'")
            
            # Verify source keys exist in source node
            source_node = self.nodes[source_name]
            for key in source_keys:
                if key not in source_node.get_data_keys():
                    raise ValueError(f"Source key '{key}' not found in node '{source_name}'")
            
            # Verify target key exists in target node
            target_node = self.nodes[target_name]
            if target_key not in target_node.get_data_keys():
                raise ValueError(f"Target key '{target_key}' not found in node '{target_name}'")
        
        # Mark the circuit as configured
        self._configured = True
    
    def set_node_data(self, node_name: str, data: Dict[str, Any]) -> None:
        """
        Set data for a node.
        
        Part of the Initialization step.
        
        Parameters
        ----------
        node_name : str
            Name of the node.
        data : Dict[str, Any]
            Dictionary mapping data keys to values.
            
        Raises
        ------
        ValueError
            If the node doesn't exist.
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' doesn't exist")
        
        node = self.nodes[node_name]
        for key, value in data.items():
            node.set_data(key, value)
    
    def get_node_data(self, node_name: str, key: str) -> Any:
        """
        Get data from a node.
        
        Parameters
        ----------
        node_name : str
            Name of the node.
        key : str
            Data key to retrieve.
            
        Returns
        -------
        Any
            The requested data.
            
        Raises
        ------
        ValueError
            If the node doesn't exist.
        KeyError
            If the key doesn't exist in the node.
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' doesn't exist")
        
        return self.nodes[node_name].get_data(key)
    
    @property
    def is_configured(self) -> bool:
        """
        Check if the circuit is fully configured.
        
        This corresponds to the Configuration step in the workflow.
        
        Returns
        -------
        bool
            True if the circuit is configured.
        """
        return self._configured
    
    @is_configured.setter
    def is_configured(self, value: bool) -> None:
        """
        Set the circuit's configured state.
        
        Parameters
        ----------
        value : bool
            The new configured state value.
        """
        # Only allow setting to True if the circuit structure is valid
        if value:
            # Validate that the circuit can be configured
            try:
                self.configure()
            except ValueError as e:
                raise ValueError(f"Cannot mark circuit as configured: {str(e)}")
        else:
            self._configured = False
    
    @property
    def is_initialized(self) -> bool:
        """
        Check if the circuit is initialized with values.
        
        This corresponds to the Initialization step in the workflow.
        
        Returns
        -------
        bool
            True if the circuit is initialized.
        """
        return self._initialized
    
    @is_initialized.setter
    def is_initialized(self, value: bool) -> None:
        """
        Set the circuit's initialized state.
        
        Parameters
        ----------
        value : bool
            The new initialized state value.
        """
        self._initialized = value
    
    @property
    def is_solved(self) -> bool:
        """
        Check if the circuit is solved.
        
        This corresponds to the Solution step in the workflow being completed.
        
        Returns
        -------
        bool
            True if the circuit is solved.
        """
        return self._solved
    
    @property
    def is_portable(self) -> bool:
        """
        Check if the circuit is portable (can be serialized).
        
        A circuit is portable if it has no computational objects attached.
        In practice, it means the circuit is configured but not yet solved.
        
        Returns
        -------
        bool
            True if the circuit is portable.
        """
        # A portable circuit is configured but not solved
        return self.is_configured and not self.is_solved
    
    @property
    def is_solvable(self) -> bool:
        """
        Check if the circuit is solvable.
        
        A circuit is solvable if it has completed the Configuration and Initialization
        steps of the workflow and is ready for the Solution step.
        
        Returns
        -------
        bool
            True if the circuit is solvable.
        """
        if not self.is_configured:
            return False
        
        if not self.is_initialized:
            return False
        
        # Check if all required nodes have initial values
        for node_name in self.backward_graph.nodes():
            node = self.nodes[node_name]
            # Check predecessors in backward graph - these are source nodes for backward operations
            predecessors = list(self.backward_graph.predecessors(node_name))
            if not predecessors:
                # Terminal node in backward graph must have all values initialized
                if not node.is_initialized():
                    return False
        
        return True
    
    @property
    def has_backward_edges(self) -> bool:
        """
        Check if the circuit has backward edges.
        
        Returns
        -------
        bool
            True if the circuit has backward edges.
        """
        return len(self.backward_graph.edges()) > 0
    
    @property
    def has_forward_edges(self) -> bool:
        """
        Check if the circuit has forward edges.
        
        Returns
        -------
        bool
            True if the circuit has forward edges.
        """
        return len(self.forward_graph.edges()) > 0
    
    def solve(self) -> Dict[str, Dict[str, Any]]:
        """
        Solve the circuit.
        
        This is the Solution step in the workflow, which should be performed after:
        1. Circuit Creation: Creating nodes and edges
        2. Configuration: Setting up operations
        3. Initialization: Providing initial values
        
        This method:
        1. Checks if the circuit is solvable
        2. Solves backward operations first
        3. Solves forward operations second
        4. Updates the circuit state
        
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Dictionary mapping node names to dictionaries of data.
            
        Raises
        ------
        ValueError
            If the circuit is not solvable.
        """
        if not self.is_configured:
            raise ValueError("Circuit is not configured. Complete the Configuration step first.")
            
        if not self.is_initialized:
            raise ValueError("Circuit is not initialized. Complete the Initialization step first.")
            
        if not self.is_solvable:
            raise ValueError("Circuit is not solvable. Check if all required node data is properly initialized.")
        
        # First, perform backward operations
        self.solve_backward()
        
        # Second, perform forward operations
        self.solve_forward()
        
        # Gather results
        results = {}
        for node_name, node in self.nodes.items():
            results[node_name] = {key: node.get_data(key) for key in node.get_initialized_keys()}
        
        # Update circuit state to mark the Solution step as complete
        self._solved = True
        
        return results
    
    def solve_backward(self) -> None:
        """
        Solve only the backward operations in the circuit.
        
        This method executes operations along backward edges in
        topological order of the backward graph.
        
        Raises
        ------
        ValueError
            If the circuit is not solvable for backward operations.
        """
        if not self.is_solvable:
            raise ValueError("Circuit is not solvable for backward operations")
            
        if self.has_backward_edges:
            for node_name in nx.topological_sort(self.backward_graph):
                # For each node in backward graph's topological order
                for succ_name in self.backward_graph.successors(node_name):
                    # Edge in backward graph: node → succ
                    edge_key = (succ_name, node_name, "backward")
                    if edge_key in self.edges:
                        edge_data = self.edges[edge_key]
                        backward_func = edge_data['backward_func']
                        source_keys = edge_data['source_keys']
                        target_key = edge_data['target_key']
                        
                        if backward_func is None:
                            continue
                        
                        # Get source data from successor node
                        succ_node = self.nodes[succ_name]
                        source_data = [succ_node.get_data(key) for key in source_keys]
                        
                        # Apply backward operation
                        result = backward_func(*source_data)
                        
                        # Store result in target node
                        self.nodes[node_name].set_data(target_key, result)
    
    def solve_forward(self) -> None:
        """
        Solve only the forward operations in the circuit.
        
        This method executes operations along forward edges in
        topological order of the forward graph.
        
        Raises
        ------
        ValueError
            If the circuit is not solvable for forward operations.
        """
        if not self.is_solvable:
            raise ValueError("Circuit is not solvable for forward operations")
            
        if self.has_forward_edges:
            for node_name in nx.topological_sort(self.forward_graph):
                # For each node in forward graph's topological order
                for succ_name in self.forward_graph.successors(node_name):
                    # Edge in forward graph: node → succ
                    edge_key = (node_name, succ_name, "forward")
                    if edge_key in self.edges:
                        edge_data = self.edges[edge_key]
                        forward_func = edge_data['forward_func']
                        source_keys = edge_data['source_keys']
                        target_key = edge_data['target_key']
                        
                        if forward_func is None:
                            continue
                        
                        # Get source data from node
                        source_data = [self.nodes[node_name].get_data(key) for key in source_keys]
                        
                        # Apply forward operation
                        result = forward_func(*source_data)
                        
                        # Store result in successor node
                        self.nodes[succ_name].set_data(target_key, result)
    
    def execute_edge(self, source_name: str, target_name: str, edge_type: str = "forward") -> Any:
        """
        Execute a single edge operation between two nodes.
        
        This provides fine-grained control to execute individual operations
        when the relevant nodes already have the required data.
        
        Parameters
        ----------
        source_name : str
            Name of the source node.
        target_name : str
            Name of the target node.
        edge_type : str, optional
            Type of edge: "forward" or "backward", default is "forward".
            
        Returns
        -------
        Any
            The result of the operation.
            
        Raises
        ------
        ValueError
            If the edge doesn't exist, or if required data is missing,
            or if there's no operation for the requested direction.
        KeyError
            If the nodes don't exist.
        """
        # Validate nodes exist
        if source_name not in self.nodes:
            raise KeyError(f"Source node '{source_name}' doesn't exist")
        if target_name not in self.nodes:
            raise KeyError(f"Target node '{target_name}' doesn't exist")
        
        # For backward edges, the direction is flipped in the internal representation
        if edge_type == "backward":
            edge_key = (target_name, source_name, "backward")
        else:
            edge_key = (source_name, target_name, "forward")
        
        # Check if the edge exists
        if edge_key not in self.edges:
            raise ValueError(f"No {edge_type} edge exists from '{source_name}' to '{target_name}'")
        
        # Get edge data
        edge_data = self.edges[edge_key]
        source_keys = edge_data['source_keys']
        target_key = edge_data['target_key']
        
        # Get the actual source node (depends on edge type)
        if edge_type == "backward":
            source_node = self.nodes[target_name]  # For backward edges, target is the source of data
            operation = edge_data['backward_func']
        else:
            source_node = self.nodes[source_name]  # For forward edges, source is the source of data
            operation = edge_data['forward_func']
        
        # Validate operation exists
        if operation is None:
            raise ValueError(f"No {edge_type} operation defined for this edge")
        
        # Check if source node has all required data
        for key in source_keys:
            if not source_node.is_initialized(key):
                raise ValueError(f"Source node '{source_node.name}' is missing required data key '{key}'")
        
        # Get source data
        source_data = [source_node.get_data(key) for key in source_keys]
        
        # Apply operation
        result = operation(*source_data)
        
        # Store result in the appropriate node
        if edge_type == "backward":
            # For backward edges, store in the "source" node in the graph
            self.nodes[source_name].set_data(target_key, result)
        else:
            # For forward edges, store in the target node
            self.nodes[target_name].set_data(target_key, result)
        
        return result
    
    def save(self, filepath: str) -> None:
        """
        Save the circuit to a file.
        
        Parameters
        ----------
        filepath : str
            Path to save the circuit.
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filepath: str) -> 'Graph':
        """
        Load a circuit from a file.
        
        Parameters
        ----------
        filepath : str
            Path to load the circuit from.
            
        Returns
        -------
        Graph
            The loaded circuit.
        """
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def to_portable(self) -> 'Graph':
        """
        Create a portable version of this circuit.
        
        A portable circuit has the same structure but no data.
        It can be serialized and shared.
        
        Returns
        -------
        Graph
            A portable version of this circuit.
        """
        portable = Graph(name=f"{self.name}_portable")
        
        # Copy nodes without data
        for node_name, node in self.nodes.items():
            new_node = Node(node_name, {key: None for key in node.get_data_keys()})
            portable.add_node(new_node)
        
        # Copy edges without operations
        for edge_key, edge_data in self.edges.items():
            source_name, target_name, edge_type = edge_key
            source_keys = edge_data['source_keys']
            target_key = edge_data['target_key']
            
            # Create placeholder operations (None) for portable version
            portable_op = (None, None)
            
            if len(source_keys) == 1:
                source_key = source_keys[0]
                portable.add_edge(source_name, target_name, portable_op,
                                source_key=source_key, target_key=target_key,
                                edge_type=edge_type)
            else:
                portable.add_edge(source_name, target_name, portable_op,
                                source_keys=source_keys, target_key=target_key,
                                edge_type=edge_type)
        
        # Set circuit state
        portable._configured = True
        portable._initialized = False
        portable._solved = False
        
        return portable
    
    def mark_configured(self) -> None:
        """Mark the circuit as configured."""
        self._configured = True
    
    def __str__(self) -> str:
        """String representation of the circuit."""
        nodes_str = ", ".join(self.nodes.keys())
        status = []
        if self.is_configured:
            status.append("configured")
        if self.is_initialized:
            status.append("initialized")
        if self.is_solvable:
            status.append("solvable")
        if self.is_solved:
            status.append("solved")
        if self.is_portable:
            status.append("portable")
        
        status_str = ", ".join(status)
        return f"Circuit({self.name}, nodes=[{nodes_str}], status=[{status_str}])"
