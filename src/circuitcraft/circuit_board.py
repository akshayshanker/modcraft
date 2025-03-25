import pickle
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

import networkx as nx
import numpy as np

from .perch import Perch
from .mover import Mover


class CircuitBoard:
    """
    A circuit-board in CircuitCraft represented as a directed graph.
    
    In CircuitCraft, circuits are represented as graphs where:
    - Perches store data (comp and sim)
    - Movers contain maps and computational methods (mathematical representations and their implementations)
    
    The graph maintains both backward and forward edges:
    - Backward edges: For operations like Coleman solving (successor to predecessor)
    - Forward edges: For operations like push-forward (predecessor to successor)
    
    The circuit-board lifecycle is tracked with flags:
    1. has_empty_perches: True if the circuit has placeholder perches with no data
    2. has_model: True if all needed perches and movers have been created and connected
    3. movers_backward_exist: True if the graph contains at least one backward mover
    4. is_portable: True if the circuit can be serialized (no embedded references)
    5. is_solvable: True if the circuit has enough data to run the solve procedure
    6. is_solved: True if the backward solution phase has been completed
    7. is_simulated: True if the forward distribution pass has been completed
    """
    
    def __init__(self, name: str = "circuit_board"):
        """
        Initialize a circuit board.
        
        Parameters
        ----------
        name : str, optional
            Name of the circuit board, default is "circuit_board".
        """
        self.name = name
        self.perches: Dict[str, Perch] = {}
        
        # Use two separate directed graphs for backward and forward operations
        self.backward_graph = nx.DiGraph()
        self.forward_graph = nx.DiGraph()
        
        # Lifecycle flags
        self.has_empty_perches = True
        self.has_model = False
        self.movers_backward_exist = False
        self.is_portable = False
        self.is_solvable = False
        self.is_solved = False
        self.is_simulated = False
    
    def add_perch(self, perch: Perch) -> None:
        """
        Add a perch to the circuit board.
        
        Part of the Circuit Creation step.
        
        Parameters
        ----------
        perch : Perch
            The perch to add.
            
        Raises
        ------
        ValueError
            If a perch with the same name already exists.
        """
        if perch.name in self.perches:
            raise ValueError(f"Perch with name '{perch.name}' already exists")
        
        self.perches[perch.name] = perch
        self.backward_graph.add_node(perch.name)
        self.forward_graph.add_node(perch.name)
        
        # Check if perch has any initialized data
        if perch.comp is not None or perch.sim is not None:
            self.has_empty_perches = False
    
    def add_mover(self, source_name: str, target_name: str,
                 map_data: Optional[Dict[str, Any]] = None,
                 parameters: Optional[Dict[str, Any]] = None,
                 numerical_hyperparameters: Optional[Dict[str, Any]] = None,
                 source_key: Optional[str] = None, 
                 source_keys: Optional[List[str]] = None,
                 target_key: Optional[str] = None, 
                 edge_type: str = "forward") -> None:
        """
        Add a mover to the circuit board.
        
        Part of the Circuit Creation step.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        map_data : Dict[str, Any], optional
            Mathematical representation of the operation.
        parameters : Dict[str, Any], optional
            Problem-specific values.
        numerical_hyperparameters : Dict[str, Any], optional
            Tuning values for the computational method.
        source_key : str, optional
            DEPRECATED: Use source_keys instead.
            Key from source perch to use in the operation.
        source_keys : List[str], optional
            Keys from source perch to use in the operation.
            Default is ["comp"] for backward movers and ["comp", "sim"] for forward movers.
        target_key : str, optional
            Key in target perch where the result will be stored.
            Default is "comp" for backward movers and "sim" for forward movers.
        edge_type : str, optional
            Type of mover: "forward" or "backward".
            Default is "forward".
            
        Raises
        ------
        ValueError
            If either perch doesn't exist.
        """
        if source_name not in self.perches:
            raise ValueError(f"Source perch '{source_name}' doesn't exist")
        if target_name not in self.perches:
            raise ValueError(f"Target perch '{target_name}' doesn't exist")
        
        # Get the appropriate graph
        graph = self._get_graph(edge_type)
        
        # Handle deprecated source_key parameter
        if source_key is not None:
            if source_keys is not None:
                raise ValueError("Cannot provide both source_key and source_keys. Use source_keys only.")
            source_keys = [source_key]
            
        # Set default source_keys and target_key if not provided
        if source_keys is None:
            if edge_type == "backward":
                # For backward movers: Source = comp of the preceding perch
                source_keys = ["comp"]
            else:  # forward
                # For forward movers: Source = sim from the preceding perch
                source_keys = ["sim"]
            
        if target_key is None:
            if edge_type == "backward":
                # For backward movers: Target = comp of the succeeding perch
                target_key = "comp"
            else:  # forward
                # For forward movers: Target = sim of the succeeding perch
                target_key = "sim"
                
        # Create and add the mover
        mover = Mover(
            source_name=source_name,
            target_name=target_name,
            edge_type=edge_type,
            map_data=map_data,
            parameters=parameters,
            numerical_hyperparameters=numerical_hyperparameters,
            source_keys=source_keys,
            target_key=target_key
        )
        
        # Add the edge with the mover object as an attribute
        graph.add_edge(source_name, target_name, mover=mover)
        
        # Set flag for backward movers
        if edge_type == "backward":
            self.movers_backward_exist = True
            
        # Reset the model flag since we've modified the graph
        self.has_model = False
    
    def set_mover_map(self, source_name: str, target_name: str, edge_type: str, map_data: Any) -> None:
        """
        Set the map for a mover edge.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        edge_type : str
            Type of mover: "forward" or "backward".
        map_data : Any
            Mathematical representation of the operation.
            
        Raises
        ------
        ValueError
            If the mover doesn't exist.
        """
        graph = self._get_graph(edge_type)
        
        if not graph.has_edge(source_name, target_name):
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' doesn't exist")
            
        # Get the mover from edge data
        mover = graph[source_name][target_name]["mover"]
        mover.set_map(map_data)
    
    def set_mover_parameters(self, source_name: str, target_name: str, edge_type: str, parameters: Dict[str, Any]) -> None:
        """
        Set the parameters for a mover edge.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        edge_type : str
            Type of mover: "forward" or "backward".
        parameters : Dict[str, Any]
            Problem-specific parameters for this mover.
            
        Raises
        ------
        ValueError
            If the mover doesn't exist.
        """
        graph = self._get_graph(edge_type)
        
        if not graph.has_edge(source_name, target_name):
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' doesn't exist")
            
        # Get the mover from edge data
        mover = graph[source_name][target_name]["mover"]
        mover.set_parameters(parameters)
    
    def set_mover_numerical_hyperparameters(self, source_name: str, target_name: str, edge_type: str, hyperparams: Dict[str, Any]) -> None:
        """
        Set the numerical hyperparameters for a mover edge.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        edge_type : str
            Type of mover: "forward" or "backward".
        hyperparams : Dict[str, Any]
            Numerical hyperparameters for this mover's computational method.
            
        Raises
        ------
        ValueError
            If the mover doesn't exist.
        """
        graph = self._get_graph(edge_type)
        
        if not graph.has_edge(source_name, target_name):
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' doesn't exist")
            
        # Get the mover from edge data
        mover = graph[source_name][target_name]["mover"]
        mover.set_numerical_hyperparameters(hyperparams)
    
    def set_mover_comp(self, source_name: str, target_name: str, edge_type: str, comp_func: Callable) -> None:
        """
        Set the computational method for a mover edge.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        edge_type : str
            Type of mover: "forward" or "backward".
        comp_func : Callable
            The computational function that will transform data.
            
        Raises
        ------
        ValueError
            If the mover doesn't exist.
        """
        graph = self._get_graph(edge_type)
        
        if not graph.has_edge(source_name, target_name):
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' doesn't exist")
            
        # Get the mover from edge data
        mover = graph[source_name][target_name]["mover"]
        mover.set_comp(comp_func)
    
    def _get_graph(self, edge_type: str) -> nx.DiGraph:
        """Get the appropriate graph based on edge type."""
        if edge_type == "forward":
            return self.forward_graph
        elif edge_type == "backward":
            return self.backward_graph
        else:
            raise ValueError(f"Unrecognized edge_type: {edge_type}")
    
    def finalize_model(self) -> None:
        """
        Indicate that all perches and movers have been created.
        Updates the has_model flag to True.
        """
        self.has_model = True
        self._check_solvability()
    
    def _check_solvability(self) -> bool:
        """
        Check if the circuit has enough data to be solved.
        Updates the is_solvable flag if appropriate.
        
        For backward solving: At least one perch must have a comp value.
        For forward simulation: At least one perch must have a sim value.
        """
        if not self.has_model:
            return False
            
        # Check if we have any perches with comp for backward solve
        if self.movers_backward_exist:
            # Need at least one perch with comp initialized for backward solving
            if not any(perch.comp is not None for perch in self.perches.values()):
                return False
                
        # Check if we have initial perches with sim for forward simulation
        if self.forward_graph.edges():
            # Need at least one perch with sim initialized for forward simulation
            initial_perches = self._get_initial_perches("forward")
            if not any(self.perches[p].sim is not None for p in initial_perches):
                return False
        
        # If we reach here, we have enough data to run a solve
        self.is_solvable = True
        return True
    
    def _get_terminal_perches(self, edge_type: str) -> List[str]:
        """Get terminal perches (no outgoing edges) for the specified edge type."""
        graph = self._get_graph(edge_type)
        return [n for n in graph.nodes() if graph.out_degree(n) == 0]
    
    def _get_initial_perches(self, edge_type: str) -> List[str]:
        """Get initial perches (no incoming edges) for the specified edge type."""
        graph = self._get_graph(edge_type)
        return [n for n in graph.nodes() if graph.in_degree(n) == 0]
    
    def create_comps_from_maps(self, comp_factory: Callable[[Dict[str, Any]], Callable]) -> None:
        """
        Create computational methods (comps) from maps for all movers.
        
        Parameters
        ----------
        comp_factory : Callable
            Function that takes a map and returns a comp callable.
        """
        # Process backward movers
        for source, target, data in self.backward_graph.edges(data=True):
            mover = data["mover"]
            if mover.has_map and not mover.has_comp:
                mover.create_comp_from_map(comp_factory)
        
        # Process forward movers
        for source, target, data in self.forward_graph.edges(data=True):
            mover = data["mover"]
            if mover.has_map and not mover.has_comp:
                mover.create_comp_from_map(comp_factory)
        
        # Check portability status
        self._check_portability()
    
    def _check_portability(self) -> None:
        """
        Check if the circuit is portable (can be serialized).
        Updates the is_portable flag if appropriate.
        """
        # For now, we'll consider it portable if all movers with maps have comps
        for graph in [self.backward_graph, self.forward_graph]:
            for _, _, data in graph.edges(data=True):
                mover = data["mover"]
                if mover.has_map and not mover.has_comp:
                    self.is_portable = False
                    return
        
        self.is_portable = True
    
    def execute_mover(self, source_name: str, target_name: str, edge_type: str = "forward") -> Any:
        """
        Execute a single mover in the circuit.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        edge_type : str
            Type of mover: "forward" or "backward".
            
        Returns
        -------
        Any
            Result from executing the mover.
            
        Raises
        ------
        ValueError
            If the mover doesn't exist or has no comp method.
        """
        graph = self._get_graph(edge_type)
        
        if not graph.has_edge(source_name, target_name):
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' doesn't exist")
            
        # Get the source perch and the mover
        source_perch = self.perches[source_name]
        target_perch = self.perches[target_name]
        mover = graph[source_name][target_name]["mover"]
        
        if not mover.has_comp:
            raise ValueError(f"{edge_type} mover from '{source_name}' to '{target_name}' has no comp method")
        
        # Extract data from source perch based on source_keys
        input_data = {}
        for key in mover.source_keys:
            input_data[key] = source_perch.get_data(key)
            
        # If there's only one source key, pass the value directly instead of a dictionary
        if len(mover.source_keys) == 1:
            input_data = input_data[mover.source_keys[0]]
            
        # Execute the mover's comp function
        result = mover.execute(input_data)
        
        # Apply the result to the target perch
        if result is None:
            # Nothing to update if result is None
            pass
        elif isinstance(result, dict):
            # If result is a dictionary, update the target perch with the values
            for key, value in result.items():
                if key in target_perch.get_data_keys():
                    target_perch.set_data(key, value)
        else:
            # If result is not a dictionary, update the target_key directly
            if mover.target_key:
                target_perch.set_data(mover.target_key, result)
                
        return result
    
    def get_movers_dict(self, mover_type=None):
        """
        Get a dictionary mapping from source perch to list of target perches
        with associated movers.
        
        Parameters
        ----------
        mover_type : str, optional
            If provided, only include movers of this type (e.g., 'backward', 'forward')
            
        Returns
        -------
        dict
            Dictionary with source perch names as keys and lists of target perch names as values
        """
        movers_dict = {}
        
        # Find movers in the appropriate graph
        if mover_type == "backward":
            graph = self.backward_graph
        elif mover_type == "forward":
            graph = self.forward_graph
        else:
            # If no type specified, include both graphs
            backward_edges = list(self.backward_graph.edges(data=True))
            forward_edges = list(self.forward_graph.edges(data=True))
            all_edges = backward_edges + forward_edges
            
            for source, target, data in all_edges:
                if source not in movers_dict:
                    movers_dict[source] = []
                movers_dict[source].append(target)
            
            return movers_dict
        
        # Process edges from the specific graph
        for source, target, data in graph.edges(data=True):
            if source not in movers_dict:
                movers_dict[source] = []
            movers_dict[source].append(target)
            
        return movers_dict
    
    def solve_backward(self):
        """
        Solve all backward movers in the circuit.
        
        This performs backward operations (starting from terminal perches)
        using a reversed topological sort of the backward graph.
        """
        # Check that we have at least one backward mover
        if not self.movers_backward_exist:
            raise RuntimeError("Cannot solve backwards: No backward movers exist")
            
        # Check if any perch has a comp value - we need initial values
        initial_perches = [name for name, perch in self.perches.items() if perch.comp is not None]
        if not initial_perches:
            raise RuntimeError("Cannot solve backwards: No perch has a comp value")
            
        print("Perches with initial comp values:", initial_perches)
            
        # Create a topological sort of the backward graph
        try:
            # In backward graph: A->B means B's value depends on A's
            # So we want to solve in the order of the topological sort
            topo_order = list(nx.topological_sort(self.backward_graph))
            print("Topological order:", topo_order)
            
            if not topo_order:
                raise RuntimeError("Cannot solve backwards: Backward graph is empty")
                
        except nx.NetworkXUnfeasible:
            # Graph has cycles
            raise RuntimeError("Backward graph contains cycles; cannot perform topological sort")
            
        # Debug output of all movers
        print("Checking all movers in backward graph:")
        for source, target, mover_data in self.backward_graph.edges(data=True):
            mover = mover_data.get("mover")
            if mover:
                print(f"Edge {source} -> {target}:")
                print(f"  Mover type: {mover.edge_type}")
                print(f"  Has comp: {mover.has_comp}")
                print(f"  comp: {mover.comp}")
                print(f"  Source perch keys: {mover.source_keys}")
                print(f"  Target perch key: {mover.target_key}")
                
                # Debug perch data
                source_perch_data = self.perches[source].get_data(mover.source_keys[0]) if mover.source_keys else None
                target_perch_data = self.perches[target].get_data(mover.target_key) if mover.target_key else None
                print(f"  Source perch data: {source_perch_data}")
                print(f"  Target perch data: {target_perch_data}")
            
        # Solve iteratively - repeat until no changes are made
        iteration = 0
        made_changes = True
        
        # Keep track of previous values to detect actual changes
        previous_values = {}
        for perch_name, perch in self.perches.items():
            previous_values[perch_name] = {}
            for key in perch.get_data_keys():
                previous_values[perch_name][key] = perch.get_data(key)
        
        while made_changes:
            iteration += 1
            print(f"Backward solving iteration {iteration}")
            made_changes = False  # Reset flag for this iteration
            
            # Limit iterations to prevent infinite loops
            if iteration > 100:  # Set a reasonable limit
                print("Maximum iterations reached. Stopping backward solve.")
                break
            
            for source, target, mover_data in self.backward_graph.edges(data=True):
                source_perch = self.perches[source]
                target_perch = self.perches[target]
                
                # Check if source has the required source key values
                source_has_data = True
                source_comp = None
                if mover_data.get("mover") and mover_data["mover"].source_keys:
                    source_key = mover_data["mover"].source_keys[0] # backward movers typically only have one source key
                    source_comp = source_perch.get_data(source_key)
                    source_has_data = source_comp is not None
                    
                print(f"Checking edge {source} -> {target}:")
                print(f"  Source comp: {source_comp}")
                print(f"  Target comp: {target_perch.comp}")
                
                if not source_has_data:
                    # Skip if source doesn't have the required data
                    continue
                    
                # Get the mover for this edge
                mover = mover_data.get("mover")
                
                if mover and mover.has_comp:
                    try:
                        print(f"Executing backward mover from {source} to {target}")
                        
                        # Store previous value to detect changes
                        previous_target_value = None
                        if mover.target_key:
                            previous_target_value = target_perch.get_data(mover.target_key)
                        
                        # Use our execute_mover method for consistency
                        result = self.execute_mover(source, target, "backward")
                        
                        # Check if the target value has actually changed
                        current_target_value = None
                        if mover.target_key:
                            current_target_value = target_perch.get_data(mover.target_key)
                            
                        # Compare values properly for any data type
                        value_changed = False
                        if previous_target_value is None and current_target_value is not None:
                            value_changed = True
                        elif current_target_value is None and previous_target_value is not None:
                            value_changed = True
                        elif isinstance(previous_target_value, np.ndarray) and isinstance(current_target_value, np.ndarray):
                            # Special handling for NumPy arrays
                            value_changed = not np.array_equal(previous_target_value, current_target_value)
                        elif hasattr(previous_target_value, "__eq__") and previous_target_value is not None:
                            # Most objects have __eq__ defined, so use it
                            value_changed = previous_target_value != current_target_value
                        else:
                            # Fallback to id comparison for objects without proper equality
                            value_changed = id(previous_target_value) != id(current_target_value)
                            
                        if value_changed:
                            print(f"  Value changed: {previous_target_value} -> {current_target_value}")
                            made_changes = True
                        
                    except Exception as e:
                        print(f"Error executing backward mover from {source} to {target}: {e}")
        
        # Check if backward solve was successful
        if not any(perch.comp is not None for perch in self.perches.values()):
            print("Backward solve failed: No perch has a comp value after solving")
        else:
            print("Backward solve completed successfully with changes made.")
            
        # Flag the circuit as solved if all perches have comp
        if all(perch.comp is not None for perch in self.perches.values()):
            self.is_solved = True
    
    def solve_forward(self) -> None:
        """
        Solve all forward movers in the circuit.
        
        This performs forward operations (predecessor to successor)
        using a topological sort of the forward graph.
        
        Raises
        ------
        RuntimeError
            If the circuit is not solvable.
        """
        # Check if any perch has a comp value - otherwise we can't simulate
        if not any(perch.comp is not None for perch in self.perches.values()):
            raise RuntimeError("Cannot simulate forward pass: No perch has a comp value.")
        
        # Find initial perches (those with both comp and sim values)
        initial_perches = []
        for name, perch in self.perches.items():
            if perch.comp is not None and perch.sim is not None:
                initial_perches.append(name)
        
        if not initial_perches:
            raise RuntimeError("Cannot simulate forward pass: No perch has both comp and sim values.")
        
        print(f"Initial perches for forward solving: {initial_perches}")
        
        # Keep track of previous values to detect actual changes
        previous_values = {}
        for perch_name, perch in self.perches.items():
            previous_values[perch_name] = {}
            for key in perch.get_data_keys():
                previous_values[perch_name][key] = perch.get_data(key)
        
        # Get topological order for the forward graph
        try:
            topo_order = list(nx.topological_sort(self.forward_graph))
            
            # Solve iteratively - repeat until no changes are made
            iteration = 0
            made_changes = True
            
            while made_changes:
                iteration += 1
                made_changes = False  # Reset flag for this iteration
                
                # Limit iterations to prevent infinite loops
                if iteration > 100:  # Set a reasonable limit
                    print("Maximum iterations reached. Stopping forward solve.")
                    break
                
                # Process perches in topological order
                for perch_name in topo_order:
                    # Skip perches that already have sim values from initialization
                    if perch_name in initial_perches and iteration == 1:
                        continue
                        
                    # Find all predecessors of this perch in the forward graph
                    predecessors = list(self.forward_graph.predecessors(perch_name))
                    
                    # Skip if no predecessors (and not an initial perch)
                    if not predecessors:
                        continue
                        
                    # Try each predecessor to see if we can compute this perch's sim value
                    for pred in predecessors:
                        # Skip predecessors that don't have sim values
                        if self.perches[pred].sim is None:
                            continue
                            
                        # Get the mover from predecessor to this perch
                        mover = self.forward_graph[pred][perch_name].get("mover")
                        if not mover or not mover.has_comp:
                            continue
                            
                        # Store previous value to detect changes
                        previous_value = None
                        if mover.target_key:
                            previous_value = self.perches[perch_name].get_data(mover.target_key)
                        
                        # Use our execute_mover method for consistency
                        try:
                            result = self.execute_mover(pred, perch_name, "forward")
                            
                            # Check if the target value has actually changed
                            current_value = None
                            if mover.target_key:
                                current_value = self.perches[perch_name].get_data(mover.target_key)
                                
                            # Compare values properly for any data type
                            value_changed = False
                            if previous_value is None and current_value is not None:
                                value_changed = True
                            elif current_value is None and previous_value is not None:
                                value_changed = True
                            elif isinstance(previous_value, np.ndarray) and isinstance(current_value, np.ndarray):
                                # Special handling for NumPy arrays
                                value_changed = not np.array_equal(previous_value, current_value)
                            elif hasattr(previous_value, "__eq__") and previous_value is not None:
                                # Most objects have __eq__ defined, so use it
                                value_changed = previous_value != current_value
                            else:
                                # Fallback to id comparison for objects without proper equality
                                value_changed = id(previous_value) != id(current_value)
                                
                            if value_changed:
                                print(f"  Value changed: {previous_value} -> {current_value}")
                                made_changes = True
                        except Exception as e:
                            print(f"Error executing forward mover from {pred} to {perch_name}: {e}")
            
            print("Forward solve complete.")
        except nx.NetworkXError:
            raise RuntimeError("Forward graph contains cycles; cannot perform topological sort")
            
        # Mark as simulated if any sim values were generated
        if any(perch.sim is not None for perch in self.perches.values()):
            self.is_simulated = True
    
    def solve(self):
        """
        Solve the circuit by running backward and forward solving in sequence.
        
        This method will:
        1. Solve backward to populate comp values for all perches
        2. Solve forward to populate sim values for all perches
        
        Returns
        -------
        bool
            True if the circuit was solved successfully, False otherwise.
            
        Raises
        ------
        RuntimeError
            If the circuit is not solvable or an error occurs during solving.
        """
        # Check that the circuit is finalized and has a model
        if not self.has_model:
            raise RuntimeError("Cannot solve: Circuit model is not finalized")
            
        # Check if the circuit is solvable
        if not self.is_solvable:
            raise RuntimeError("Cannot solve: Circuit is not solvable (missing terminal values)")
            
        # Solve backward to compute comp values
        try:
            self.solve_backward()
        except Exception as e:
            print(f"Error during backward solving: {e}")
            return False
            
        # Solve forward to compute sim values
        try:
            self.solve_forward()
        except Exception as e:
            print(f"Error during forward solving: {e}")
            return False
            
        # Update circuit status
        self.is_solved = True
        
        return True
    
    def get_perch_data(self, perch_name: str, key: str) -> Any:
        """
        Get data from a perch by key.
        
        Parameters
        ----------
        perch_name : str
            Name of the perch.
        key : str
            Key of the data to retrieve.
            
        Returns
        -------
        Any
            The requested data.
            
        Raises
        ------
        ValueError
            If the perch doesn't exist.
        KeyError
            If the key doesn't exist in the perch.
        """
        if perch_name not in self.perches:
            raise ValueError(f"Perch '{perch_name}' doesn't exist")
            
        return self.perches[perch_name].get_data(key)
    
    def set_perch_data(self, perch_name: str, data: Dict[str, Any]) -> None:
        """
        Set data on a perch.
        
        Parameters
        ----------
        perch_name : str
            Name of the perch.
        data : Dict[str, Any]
            Dictionary of data to set on the perch.
            
        Raises
        ------
        ValueError
            If the perch doesn't exist.
        KeyError
            If any key doesn't exist in the perch.
        """
        if perch_name not in self.perches:
            raise ValueError(f"Perch '{perch_name}' doesn't exist")
            
        perch = self.perches[perch_name]
        for key, value in data.items():
            perch.set_data(key, value)
            
        # If we're adding data to perches, they're no longer empty
        if data:
            self.has_empty_perches = False
            
        # Adding data might make the circuit solvable
        self._check_solvability()
    
    def save(self, filepath: str) -> None:
        """
        Save the circuit to a file.
        
        This serializes the circuit state using pickle, ensuring that
        all contained objects are serializable.
        
        Parameters
        ----------
        filepath : str
            Path to save the circuit to.
            
        Raises
        ------
        RuntimeError
            If the circuit is not portable.
        """
        if not self.is_portable:
            raise RuntimeError("Circuit is not portable. Call make_portable() before saving.")
            
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
        except Exception as e:
            raise RuntimeError(f"Failed to save circuit: {str(e)}")
    
    @classmethod
    def load(cls, filepath: str) -> 'CircuitBoard':
        """
        Load a circuit from a file.
        
        Parameters
        ----------
        filepath : str
            Path to load the circuit from.
            
        Returns
        -------
        CircuitBoard
            The loaded circuit.
            
        Raises
        ------
        RuntimeError
            If loading fails.
        """
        try:
            with open(filepath, 'rb') as f:
                circuit = pickle.load(f)
                
            if not isinstance(circuit, cls):
                raise TypeError(f"Loaded object is not a {cls.__name__}")
                
            return circuit
        except Exception as e:
            raise RuntimeError(f"Failed to load circuit from {filepath}: {str(e)}")
    
    def make_portable(self, comp_factory: Optional[Callable] = None) -> None:
        """
        Make the circuit portable by ensuring all maps have comps.
        
        Parameters
        ----------
        comp_factory : Callable, optional
            Function that creates comps from maps. If None, a default is used.
        """
        # If no factory provided, create a default that just passes through the data
        if comp_factory is None:
            def default_factory(map_data):
                def comp(input_data: Dict[str, Any]) -> Dict[str, Any]:
                    # Simple identity function - just return the input
                    return input_data
                return comp
            comp_factory = default_factory
        
        # Create comps for all maps
        self.create_comps_from_maps(comp_factory)
    
    def __str__(self) -> str:
        """String representation of the circuit board."""
        perch_count = len(self.perches)
        backward_edge_count = self.backward_graph.number_of_edges()
        forward_edge_count = self.forward_graph.number_of_edges()
        
        status = []
        if self.has_model:
            status.append("modeled")
        if self.is_portable:
            status.append("portable")
        if self.is_solved:
            status.append("solved")
        if self.is_simulated:
            status.append("simulated")
        
        status_str = ", ".join(status) if status else "empty"
        
        return (f"CircuitBoard({self.name}, {perch_count} perches, "
                f"{backward_edge_count} backward movers, {forward_edge_count} forward movers, {status_str})") 