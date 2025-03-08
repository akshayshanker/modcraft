from typing import Any, Callable


class Node:
    """
    Computational node used within the computational
    Directed Acyclic Graph (DAG). The Node takes in a
    name and a callable "Component". If the node is
    called then the component will be executed with the
    provided args and keyword args. 
    """
    
    def __init__(self, name: str, component: Callable):
        """
        Initialize a Node in the computational graph. The node is initialized
        with empty lists for parents and children, which can be populated using
        the add_parent method to build the graph structure.

        Parameters
        ----------
        name : str
            The unique identifier for the node within the graph.
        component : Callable
            The function or class to be executed when the node is called.
            Must be a callable object that can accept arbitrary arguments.

        Returns
        -------
        None
        """
        self.name = name
        self.component = component
        self.parents = []
        self.children = []

    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the node's component function with the provided arguments.
        This method allows the Node object to be called like a function,
        delegating the call to its underlying component.

        Parameters
        ----------
        *args : tuple
            Variable length argument list to be passed to the component.
        **kwargs : dict
            Arbitrary keyword arguments to be passed to the component.

        Returns
        -------
        Any
            The result of executing the component with the provided arguments.
            The specific return type depends on the component's implementation.
        """
        return self.component(*args, **kwargs)

    def add_parent(self, parent_node: "Node"):
        """
        Add a parent node to establish a directed connection in the graph.
        This method updates both the current node's parents list and the
        parent node's children list to maintain bidirectional references.
        This is essential for graph traversal and dependency resolution.

        Parameters
        ----------
        parent_node : Node
            The node to be set as a parent of the current node.
            This creates a directed edge from parent_node to this node.

        Returns
        -------
        None
        """
        self.parents.append(parent_node)
        parent_node.children.append(self)