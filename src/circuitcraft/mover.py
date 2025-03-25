"""
Mover in a CircuitCraft circuit.

In CircuitCraft, movers contain functional relationships between perches, with
four key attributes:
- map: Mathematical representation of the operation
- parameters: Generic, problem-specific values
- numerical_hyperparameters: Tuning values for the computational method
- comp: Computational callable instantiated from the map
"""

from typing import Any, Dict, List, Optional, Callable, Union


class Mover:
    """
    Mover in a CircuitCraft circuit.
    
    In CircuitCraft, movers represent functional relationships between perches. 
    Each mover contains:
    
    1. map: The mathematical representation of the operation (can be equations, 
       instructions, grid sizes, etc.)
    2. parameters: Generic, problem-specific values
    3. numerical_hyperparameters: Tuning values for the computational method
    4. comp: The computational callable instantiated from the map
    
    The mover direction determines whether it's a backward or forward operation.
    """
    
    def __init__(self, 
                 source_name: str, 
                 target_name: str,
                 edge_type: str = "forward",
                 map_data: Optional[Dict[str, Any]] = None,
                 parameters: Optional[Dict[str, Any]] = None,
                 numerical_hyperparameters: Optional[Dict[str, Any]] = None,
                 comp: Optional[Callable] = None,
                 source_keys: Optional[List[str]] = None,
                 target_key: Optional[str] = None):
        """
        Initialize a Mover in the circuit.
        
        Parameters
        ----------
        source_name : str
            The name of the source perch.
        target_name : str
            The name of the target perch.
        edge_type : str
            The type of mover: "forward" or "backward".
        map_data : Dict[str, Any], optional
            Mathematical representation of the operation.
        parameters : Dict[str, Any], optional
            Generic, problem-specific values.
        numerical_hyperparameters : Dict[str, Any], optional
            Tuning values for the computational method.
        comp : Callable, optional
            Computational callable instantiated from the map.
        source_keys : List[str], optional
            Keys from the source perch used in the operation.
        target_key : str, optional
            Key in the target perch where the result is stored.
        """
        self.source_name = source_name
        self.target_name = target_name
        self.edge_type = edge_type
        self.map_data = map_data or {}
        self.parameters = parameters or {}
        self.numerical_hyperparameters = numerical_hyperparameters or {}
        self.comp = comp
        self.source_keys = source_keys or []
        self.target_key = target_key
        
    @property
    def has_map(self) -> bool:
        """Check if the mover has a map defined."""
        return bool(self.map_data)
        
    @property
    def has_comp(self) -> bool:
        """Check if the mover has a comp function instantiated."""
        return self.comp is not None
        
    def set_map(self, map_data: Dict[str, Any]) -> None:
        """
        Set the mathematical representation (map) for this mover.
        
        Parameters
        ----------
        map_data : Dict[str, Any]
            Mathematical representation containing all information needed
            to define the computational operation.
        """
        self.map_data = map_data
        
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set the parameters for this mover.
        
        Parameters
        ----------
        parameters : Dict[str, Any]
            Problem-specific parameters for this mover.
        """
        self.parameters = parameters
        
    def set_numerical_hyperparameters(self, hyperparams: Dict[str, Any]) -> None:
        """
        Set the numerical hyperparameters for this mover.
        
        Parameters
        ----------
        hyperparams : Dict[str, Any]
            Numerical hyperparameters for this mover's computational method.
        """
        self.numerical_hyperparameters = hyperparams
        
    def set_comp(self, comp: Callable) -> None:
        """
        Set the computational callable (comp) for this mover.
        
        Parameters
        ----------
        comp : Callable
            The computational function that will transform data.
        """
        self.comp = comp
        
    def create_comp_from_map(self, comp_factory: Callable[[Dict[str, Any]], Callable]) -> None:
        """
        Create a comp function from the mover's map using an external factory function.
        
        Parameters
        ----------
        comp_factory : Callable
            Function that takes map_data, parameters, and numerical_hyperparameters 
            and returns a comp callable.
            
        Raises
        ------
        ValueError
            If no map is defined for this mover.
        """
        if not self.has_map:
            raise ValueError("Cannot create comp function: No map defined for this mover")
            
        self.comp = comp_factory({
            "map": self.map_data,
            "parameters": self.parameters,
            "numerical_hyperparameters": self.numerical_hyperparameters
        })
        
    def execute(self, data: Any) -> Any:
        """
        Execute the mover's comp function with the provided data.
        
        Parameters
        ----------
        data : Any
            Input data for the comp function. This can be a dictionary, array, or any other data type.
            
        Returns
        -------
        Any
            Result from executing the comp function.
            
        Raises
        ------
        ValueError
            If no comp function is defined for this mover.
        """
        if not self.has_comp:
            raise ValueError("Cannot execute: No comp function defined for this mover")
            
        return self.comp(data)
        
    def __str__(self) -> str:
        """String representation of the mover."""
        edge_dir = "→" if self.edge_type == "forward" else "←"
        status = []
        if self.has_map:
            status.append("mapped")
        if self.has_comp:
            status.append("executable")
        status_str = ", ".join(status) if status else "empty"
        return f"Mover({self.source_name} {edge_dir} {self.target_name}, {status_str})" 