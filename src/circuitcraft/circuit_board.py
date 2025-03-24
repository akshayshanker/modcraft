import pickle
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

import networkx as nx

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
        
        Part of the Circuit Creation step. This creates the graph structure and optionally
        adds a map (mathematical representation) to the mover.
        
        Parameters
        ----------
        source_name : str
            Name of the source perch.
        target_name : str
            Name of the target perch.
        map_data : Dict[str, Any], optional
            Mathematical representation of the operation.
        parameters : Dict[str, Any], optional
            Problem-specific parameters for this mover.
        numerical_hyperparameters : Dict[str, Any], optional
            Numerical hyperparameters for this mover's computational method.
        source_key : str, optional
            Single source data key if only one source key is needed.
        source_keys : List[str], optional
            List of source data keys if multiple source keys are needed.
        target_key : str, optional
            Target data key where the result will be stored.
        edge_type : str, optional
            Type of mover: "forward" or "backward", default is "forward".
            Forward movers: source → target (push-forward operations)
            Backward movers: target → source (backward solving operations)
            
        Raises
        ------
        ValueError
            If source_key and source_keys are both provided or both None,
            or if the perches don't exist.
        """
        # Validate perches exist
        if source_name not in self.perches:
            raise ValueError(f"Source perch '{source_name}' doesn't exist")
        if target_name not in self.perches:
            raise ValueError(f"Target perch '{target_name}' doesn't exist")
        
        # Validate source key(s)
        if (source_key is None and source_keys is None):
            source_keys = []  # No source keys specified, will be set during configuration
        elif (source_key is not None and source_keys is not None):
            raise ValueError("Provide either source_key or source_keys, but not both")
        
        # Convert single source_key to list for consistent handling
        if source_key is not None:
            source_keys = [source_key]
        
        # Create the mover
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
        
        # Add mover to the specified direction
        if edge_type == "forward":
            # Add to forward graph
            self.forward_graph.add_edge(source_name, target_name, mover=mover)
        elif edge_type == "backward":
            # Add to backward graph and set flag
            self.backward_graph.add_edge(source_name, target_name, mover=mover)
            self.movers_backward_exist = True
        else:
            raise ValueError(f"Unrecognized edge_type: {edge_type}")
    
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
    
    def _check_solvability(self) -> None:
        """
        Check if the circuit has enough data to be solved.
        Updates the is_solvable flag if appropriate.
        """
        if not self.has_model:
            return False
            
        # Check if we have terminal perches with comp for backward solve
        if self.movers_backward_exist:
            # Need at least one perch with comp initialized for backward solving
            terminal_perches = self._get_terminal_perches("backward")
            if not any(self.perches[p].comp is not None for p in terminal_perches):
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
    
    def execute_mover(self, source_name: str, target_name: str, edge_type: str = "forward") -> Dict[str, Any]:
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
        Dict[str, Any]
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
        
        # Prepare input data based on source keys
        input_data = {}
        if mover.source_keys:
            for key in mover.source_keys:
                input_data[key] = source_perch.get_data(key)
        else:
            # If no source keys specified, use all available data
            input_data = {"comp": source_perch.comp, "sim": source_perch.sim}
        
        # Execute the mover
        result = mover.execute(input_data)
        
        # Update target perch if we have a target key
        if mover.target_key and result:
            if mover.target_key in result:
                target_perch.set_data(mover.target_key, result[mover.target_key])
        else:
            # Update comp and sim if present in result
            if "comp" in result:
                target_perch.comp = result["comp"]
            if "sim" in result:
                target_perch.sim = result["sim"]
        
        return result
    
    def solve_backward(self) -> None:
        """
        Solve all backward movers in the circuit.
        
        This performs backward operations (predecessor to successor)
        using a topological sort of the backward graph.
        
        Raises
        ------
        RuntimeError
            If the circuit is not solvable.
        """
        if not self.is_solvable:
            raise RuntimeError("Circuit is not solvable. Check if terminal perches have comp values.")
        
        # Find all terminal perches (no outgoing edges in backward graph)
        terminal_perches = set(self._get_terminal_perches("backward"))
        
        # Ensure at least one terminal perch has a function initialized
        if not any(self.perches[p].comp is not None for p in terminal_perches):
            raise RuntimeError("No terminal perch has a comp value. Cannot start backward solve.")
        
        # We need to traverse the graph in reverse topological order
        try:
            # Get the topological ordering of the backward graph
            topo_order = list(nx.topological_sort(self.backward_graph))
            
            # Reverse it to go from terminal perches backward
            for target_name in reversed(topo_order):
                # Get all incoming edges (from source to target)
                for source_name in self.backward_graph.predecessors(target_name):
                    # Execute the backward mover from source to target
                    self.execute_mover(source_name, target_name, edge_type="backward")
                
        except nx.NetworkXUnfeasible:
            raise RuntimeError("Backward graph contains cycles; cannot perform topological sort")
            
        # Mark as solved
        self.is_solved = True
    
    def solve_forward(self) -> None:
        """
        Simulate all forward movers in the circuit.
        
        This performs forward operations (successor to predecessor)
        using a topological sort of the forward graph.
        
        Raises
        ------
        RuntimeError
            If the circuit is not solved or lacks initial sim values.
        """
        if not self.is_solved:
            raise RuntimeError("Cannot simulate forward pass: Backward solve not completed yet.")
        
        # Find all initial perches (no incoming edges in forward graph)
        initial_perches = set(self._get_initial_perches("forward"))
        
        # Ensure at least one initial perch has a distribution initialized
        if not any(self.perches[p].sim is not None for p in initial_perches):
            raise RuntimeError("No initial perch has a sim value. Cannot start forward simulation.")
        
        # Traverse the graph in topological order for forward simulation
        try:
            # Get the topological ordering of the forward graph
            topo_order = list(nx.topological_sort(self.forward_graph))
            
            # Go from initial perches forward
            for source_name in topo_order:
                # Get all outgoing edges (from source to target)
                for target_name in self.forward_graph.neighbors(source_name):
                    # Execute the forward mover from source to target
                    self.execute_mover(source_name, target_name, edge_type="forward")
                
        except nx.NetworkXUnfeasible:
            raise RuntimeError("Forward graph contains cycles; cannot perform topological sort")
            
        # Mark as simulated
        self.is_simulated = True
    
    def solve(self, backward_only: bool = False, forward_only: bool = False) -> None:
        """
        Solve the entire circuit by executing all movers in the appropriate order.
        
        By default, performs both backward and forward solving. Can be restricted to
        just one direction using the arguments.
        
        Parameters
        ----------
        backward_only : bool
            If True, only perform backward solving.
        forward_only : bool
            If True, only perform forward simulation.
            
        Raises
        ------
        RuntimeError
            If the circuit is not solvable or correctly initialized.
        ValueError
            If both backward_only and forward_only are True.
        """
        if backward_only and forward_only:
            raise ValueError("Cannot specify both backward_only and forward_only as True")
        
        # Check solvability
        if not self.is_solvable and not self._check_solvability():
            raise RuntimeError("Circuit is not solvable. Ensure proper initialization.")
        
        # Determine which passes to run
        do_backward = not forward_only
        do_forward = not backward_only
        
        # Execute backwards pass if needed
        if do_backward and self.movers_backward_exist:
            self.solve_backward()
        
        # Execute forwards pass if needed and if we have forward edges
        if do_forward and self.forward_graph.edges():
            # If we just did a backward solve, we're ready to go forward
            # If not, check if we're already solved
            if not do_backward and not self.is_solved:
                raise RuntimeError("Cannot perform forward simulation without backward solve")
            self.solve_forward()
    
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