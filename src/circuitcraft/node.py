from typing import Any, Dict, List, Optional, Set, Union


class Node:
    """
    Node in a CircuitCraft circuit.
    
    In CircuitCraft, nodes store data (policy functions, distributions, etc.)
    rather than computational operations. This is the opposite of traditional
    computational graphs where nodes typically represent operations.
    
    Each node can store multiple data items, accessible by keys.
    """
    
    def __init__(self, name: str, data_types: Optional[Dict[str, Any]] = None):
        """
        Initialize a Node in the circuit.
        
        Parameters
        ----------
        name : str
            The unique identifier for the node within the circuit.
        data_types : Dict[str, Any], optional
            Dictionary defining data slots with optional initial values.
            Keys are data names, values are initial data values (can be None).
        
        Examples
        --------
        >>> node = Node("policy_node", {"policy": None, "distribution": None})
        >>> node = Node("initial_node", {"policy": initial_policy, "distribution": initial_distribution})
        """
        self.name = name
        self.data = data_types or {}
        self._initialized_keys = {k for k, v in self.data.items() if v is not None}
    
    def get_data(self, key: str) -> Any:
        """
        Get data stored in the node by key.
        
        Parameters
        ----------
        key : str
            Key for the data to retrieve.
            
        Returns
        -------
        Any
            The requested data, or None if not present.
            
        Raises
        ------
        KeyError
            If the key doesn't exist in this node.
        """
        if key not in self.data:
            raise KeyError(f"Key '{key}' not found in node '{self.name}'")
        return self.data[key]
    
    def set_data(self, key: str, value: Any) -> None:
        """
        Set data in the node by key.
        
        Parameters
        ----------
        key : str
            Key for the data to set.
        value : Any
            Value to store.
            
        Raises
        ------
        KeyError
            If the key doesn't exist in this node.
        """
        if key not in self.data:
            raise KeyError(f"Key '{key}' not found in node '{self.name}'")
        self.data[key] = value
        self._initialized_keys.add(key)
    
    def add_data_key(self, key: str, initial_value: Any = None) -> None:
        """
        Add a new data key to the node.
        
        Parameters
        ----------
        key : str
            Key for the new data slot.
        initial_value : Any, optional
            Initial value for the data slot, defaults to None.
        """
        if key in self.data:
            raise ValueError(f"Key '{key}' already exists in node '{self.name}'")
        self.data[key] = initial_value
        if initial_value is not None:
            self._initialized_keys.add(key)
    
    def is_initialized(self, keys: Optional[Union[str, List[str]]] = None) -> bool:
        """
        Check if specified data keys are initialized.
        
        Parameters
        ----------
        keys : str or List[str], optional
            Key or list of keys to check. If None, checks all keys.
            
        Returns
        -------
        bool
            True if all specified keys are initialized (have non-None values).
        """
        if keys is None:
            keys = list(self.data.keys())
        elif isinstance(keys, str):
            keys = [keys]
            
        return all(k in self._initialized_keys for k in keys)
    
    def get_data_keys(self) -> Set[str]:
        """
        Get all data keys defined in this node.
        
        Returns
        -------
        Set[str]
            Set of all data keys.
        """
        return set(self.data.keys())
    
    def get_initialized_keys(self) -> Set[str]:
        """
        Get keys that have been initialized with values.
        
        Returns
        -------
        Set[str]
            Set of keys that have values.
        """
        return self._initialized_keys.copy()
    
    def clear_data(self, keys: Optional[Union[str, List[str]]] = None) -> None:
        """
        Clear data (set to None) for specified keys.
        
        Parameters
        ----------
        keys : str or List[str], optional
            Key or list of keys to clear. If None, clears all keys.
        """
        if keys is None:
            keys = list(self.data.keys())
        elif isinstance(keys, str):
            keys = [keys]
            
        for key in keys:
            if key in self.data:
                self.data[key] = None
                self._initialized_keys.discard(key)
                
    def __str__(self) -> str:
        """String representation of the node."""
        initialized = ", ".join(sorted(self._initialized_keys))
        return f"Node({self.name}, initialized=[{initialized}])"