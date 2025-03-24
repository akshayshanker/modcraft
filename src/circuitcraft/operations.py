import warnings
from typing import Any, Optional, Dict, Callable, List, Union

from .component import Component


class Operation(Component):
    """
    A simplified Component implementation that wraps a callable.
    
    .. warning:: DEPRECATED: This class is deprecated. 
       Use direct functions for operations instead.
    
    This class provides a simpler interface compared to implementing
    a full Component subclass, especially for simple operations.
    
    It can be used in either forward or backward mode, or both.
    """
    
    def __init__(self, name: str, forward_func: Optional[Callable] = None, 
                backward_func: Optional[Callable] = None,
                params: Optional[Dict[str, Any]] = None):
        """
        Initialize an Operation with optional forward and backward functions.
        
        Parameters
        ----------
        name : str
            Name of the operation.
        forward_func : Callable, optional
            Function to use for forward operations.
        backward_func : Callable, optional
            Function to use for backward operations.
        params : Dict[str, Any], optional
            Parameters for the operation.
        
        Raises
        ------
        ValueError
            If neither forward_func nor backward_func is provided.
        """
        super().__init__(name, params)
        
        warnings.warn(
            "Operation class is deprecated. Use direct functions for operations instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        self._forward_func = forward_func
        self._backward_func = backward_func
        
        if forward_func is None and backward_func is None:
            raise ValueError("At least one of forward_func or backward_func must be provided")
    
    def forward_operation(self, *args, **kwargs) -> Any:
        """
        Apply the forward operation.
        
        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the forward function.
        **kwargs : dict
            Keyword arguments to pass to the forward function.
            
        Returns
        -------
        Any
            Result of the forward function.
            
        Raises
        ------
        NotImplementedError
            If no forward function was provided.
        """
        if self._forward_func is None:
            return super().forward_operation(*args, **kwargs)
        return self._forward_func(*args, **kwargs)
    
    def backward_operation(self, *args, **kwargs) -> Any:
        """
        Apply the backward operation.
        
        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the backward function.
        **kwargs : dict
            Keyword arguments to pass to the backward function.
            
        Returns
        -------
        Any
            Result of the backward function.
            
        Raises
        ------
        NotImplementedError
            If no backward function was provided.
        """
        if self._backward_func is None:
            return super().backward_operation(*args, **kwargs)
        return self._backward_func(*args, **kwargs)
    
    def has_forward(self) -> bool:
        """Check if this operation has a forward function."""
        return self._forward_func is not None
    
    def has_backward(self) -> bool:
        """Check if this operation has a backward function."""
        return self._backward_func is not None 