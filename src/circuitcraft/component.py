import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Component(ABC):
    """
    Base class for operations in CircuitCraft.
    
    .. warning:: DEPRECATED: This class is deprecated. 
       Use direct functions for operations instead.
    
    Components are the functional units that are attached to edges in a circuit.
    They define forward and backward operations, similar to movers in StageMAker.
    
    A component can have:
    1. A backward_operation - transforms data from successor to predecessor node
    2. A forward_operation - transforms data from predecessor to successor node
    
    Components track their own state with properties like:
    - has_params: Whether parameters have been defined
    - is_configured: Whether the component is fully configured
    """
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize a Component with a name and optional parameters.
        
        Parameters
        ----------
        name : str
            Unique identifier for the component.
        params : Dict[str, Any], optional
            Configuration parameters for the component.
        """
        warnings.warn(
            "Component class is deprecated. Use direct functions for operations instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.name = name
        self.params = params or {}
        self._configured = False
    
    def backward_operation(self, *args, **kwargs) -> Any:
        """
        Transform data from successor to predecessor node.
        
        This is typically used for backward solving operations like
        the Coleman operator in economic models.
        
        Raises
        ------
        NotImplementedError
            If the component doesn't implement a backward operation.
        """
        raise NotImplementedError("Component does not implement backward operation")
    
    def forward_operation(self, *args, **kwargs) -> Any:
        """
        Transform data from predecessor to successor node.
        
        This is typically used for forward operations like
        push-forward operations in economic models.
        
        Raises
        ------
        NotImplementedError
            If the component doesn't implement a forward operation.
        """
        raise NotImplementedError("Component does not implement forward operation")
    
    def has_backward(self) -> bool:
        """
        Check if this component has a backward operation.
        
        Returns
        -------
        bool
            True if the component implements a backward operation.
        """
        return self._has_implementation('backward_operation')
    
    def has_forward(self) -> bool:
        """
        Check if this component has a forward operation.
        
        Returns
        -------
        bool
            True if the component implements a forward operation.
        """
        return self._has_implementation('forward_operation')
    
    def _has_implementation(self, method_name: str) -> bool:
        """
        Helper method to check if a method is implemented.
        
        Parameters
        ----------
        method_name : str
            Name of the method to check.
            
        Returns
        -------
        bool
            True if the method is implemented in a subclass.
        """
        method = getattr(self, method_name)
        return method.__code__ != getattr(Component, method_name).__code__
    
    def configure(self, **kwargs) -> None:
        """
        Configure the component with additional parameters.
        
        Parameters
        ----------
        **kwargs : Any
            Additional parameters to configure the component.
        """
        self.params.update(kwargs)
        self._configured = True
    
    @property
    def is_configured(self) -> bool:
        """
        Check if the component is configured.
        
        Returns
        -------
        bool
            True if the component is configured.
        """
        return self._configured
    
    @property
    def has_params(self) -> bool:
        """
        Check if the component has parameters.
        
        Returns
        -------
        bool
            True if the component has parameters.
        """
        return bool(self.params) 