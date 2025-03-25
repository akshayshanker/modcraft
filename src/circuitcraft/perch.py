from typing import Any, Dict, List, Optional, Set, Union


class Perch:
    """
    Perch in a CircuitCraft circuit.
    
    In CircuitCraft, each perch has two primary attributes:
    - up: A callable object (formerly 'function', like a policy function)
    - down: A callable object (formerly 'distribution', like a probability distribution)
    
    Each perch can also store additional data items as needed.
    """
    
    def __init__(self, name: str, data_types: Optional[Dict[str, Any]] = None):
        """
        Initialize a Perch in the circuit.
        
        Parameters
        ----------
        name : str
            The unique identifier for the perch within the circuit.
        data_types : Dict[str, Any], optional
            Dictionary defining data slots with optional initial values.
            By convention, should include 'up' and 'down' keys.
        
        Examples
        --------
        >>> perch = Perch("policy_perch", {"up": None, "down": None})
        >>> perch = Perch("initial_perch", {"up": initial_policy, "down": initial_distribution})
        """
        self.name = name
        self.data = data_types or {"up": None, "down": None}
        
        # Ensure the perch has up and down keys
        if "up" not in self.data:
            self.data["up"] = None
        if "down" not in self.data:
            self.data["down"] = None
            
        self._initialized_keys = {k for k, v in self.data.items() if v is not None}
    
    @property
    def up(self) -> Any:
        """Get the up attribute of the perch (formerly 'comp')."""
        return self.data.get("up")
    
    @up.setter
    def up(self, value: Any) -> None:
        """Set the up attribute of the perch."""
        self.data["up"] = value
        self._initialized_keys.add("up")
    
    @property
    def down(self) -> Any:
        """Get the down attribute of the perch (formerly 'sim')."""
        return self.data.get("down")
    
    @down.setter
    def down(self, value: Any) -> None:
        """Set the down attribute of the perch."""
        self.data["down"] = value
        self._initialized_keys.add("down")
    
    # For backward compatibility
    @property
    def comp(self) -> Any:
        """Get the up attribute of the perch (backward compatibility with 'comp')."""
        return self.up
    
    @comp.setter
    def comp(self, value: Any) -> None:
        """Set the up attribute of the perch (backward compatibility with 'comp')."""
        self.up = value
    
    @property
    def sim(self) -> Any:
        """Get the down attribute of the perch (backward compatibility with 'sim')."""
        return self.down
    
    @sim.setter
    def sim(self, value: Any) -> None:
        """Set the down attribute of the perch (backward compatibility with 'sim')."""
        self.down = value
    
    def get_data(self, key: str) -> Any:
        """
        Get data stored in the perch by key.
        
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
            If the key doesn't exist in this perch.
        """
        if key not in self.data:
            raise KeyError(f"Key '{key}' not found in perch '{self.name}'")
        return self.data[key]
    
    def set_data(self, key: str, value: Any) -> None:
        """
        Set data in the perch by key.
        
        Parameters
        ----------
        key : str
            Key for the data to set.
        value : Any
            Value to store.
            
        Raises
        ------
        KeyError
            If the key doesn't exist in this perch.
        """
        if key not in self.data:
            raise KeyError(f"Key '{key}' not found in perch '{self.name}'")
        self.data[key] = value
        self._initialized_keys.add(key)
    
    def add_data_key(self, key: str, initial_value: Any = None) -> None:
        """
        Add a new data key to the perch.
        
        Parameters
        ----------
        key : str
            Key for the new data slot.
        initial_value : Any, optional
            Initial value for the data slot, defaults to None.
        """
        if key in self.data:
            raise ValueError(f"Key '{key}' already exists in perch '{self.name}'")
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
        Get all data keys defined in this perch.
        
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
        """String representation of the perch."""
        initialized = ", ".join(sorted(self._initialized_keys))
        return f"Perch({self.name}, initialized=[{initialized}])" 