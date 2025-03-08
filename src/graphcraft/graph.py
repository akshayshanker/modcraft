from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, List, Dict

import networkx as nx

from graphcraft.node import Node


@dataclass
class Graph:
    """
    A directed acyclic graph (DAG) for managing computational nodes and their execution.

    This class provides functionality to build and execute a computational graph
    where nodes represent callable components and edges represent dependencies
    between these components. The graph ensures acyclicity and provides
    topologically sorted execution order.

    Parameters
    ----------
    nodes : Dict[str, Node], optional
        Dictionary mapping node names to Node objects. Defaults to empty dict.
    graph : nx.DiGraph, optional
        NetworkX directed graph storing the topology. Defaults to empty DiGraph.

    Attributes
    ----------
    nodes : Dict[str, Node]
        Dictionary storing all nodes in the graph, keyed by their names.
    graph : nx.DiGraph
        NetworkX directed graph representing the computational dependencies.
    sorted_nodes : List[str]
        Cached property containing nodes in topologically sorted order.

    Notes
    -----
    The graph maintains both a dictionary of Node objects and a NetworkX DiGraph
    structure. The NetworkX graph is used for topological operations while the
    nodes dictionary stores the actual computational components.
    """
    nodes: Dict[str, Node] = field(default_factory=dict)
    graph: nx.DiGraph = field(default_factory=nx.DiGraph)

    def add_node(self, node: Node):
        """
        Add a new node to the computational graph.

        Parameters
        ----------
        node : Node
            The node to be added to the graph. Must have a unique name.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If a node with the same name already exists in the graph.

        Notes
        -----
        This method updates both the nodes dictionary and the NetworkX graph
        structure. The node's name is used as the identifier in both cases.
        """
        if node.name in self.nodes:
            raise ValueError(
                f"Node with name '{node.name}' already exists."
            )
        
        self.nodes[node.name] = node
        self.graph.add_node(node.name)

    def add_dependency(self, parent_name: str, child_name: str):
        """
        Create a directed edge representing a dependency between two nodes.

        Parameters
        ----------
        parent_name : str
            Name of the parent node whose output will be used by the child.
        child_name : str
            Name of the child node that depends on the parent's output.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If either node doesn't exist in the graph, or if adding the
            dependency would create a cycle in the graph.

        Notes
        -----
        This method:
        - Updates both the Node objects' parent-child relationships
        - Adds the edge to the NetworkX graph
        - Verifies that the graph remains acyclic
        - Reverts changes if a cycle would be created
        """
        if parent_name not in self.nodes or child_name not in self.nodes:
            raise ValueError(
                "Both nodes must be added before creating a dependency."
            )
        
        self.nodes[child_name].add_parent(self.nodes[parent_name])
        self.graph.add_edge(parent_name, child_name)
        
        if not nx.is_directed_acyclic_graph(self.graph):
            # Revert the edge if adding creates a cycle
            self.graph.remove_edge(parent_name, child_name)

            # Also revert the Node relationship
            self.nodes[parent_name].children.remove(self.nodes[child_name])
            self.nodes[child_name].parents.remove(self.nodes[parent_name])

            raise ValueError(
                "Adding this edge would create a cycle in the graph."
            )

    @cached_property
    def sorted_nodes(self) -> List[str]:
        """
        Get nodes in topologically sorted order.

        Returns
        -------
        List[str]
            List of node names in topological order, ensuring that nodes are
            processed only after all their dependencies.

        Notes
        -----
        This is a cached property, meaning the topological sort is computed
        only once and cached until the graph structure changes. The property
        should be accessed through self.sorted_nodes.
        """
        return list(nx.topological_sort(self.graph))

    def __call__(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the computational graph in topological order.

        Parameters
        ----------
        inputs : Dict[str, Any], optional
            Dictionary mapping node names to their input parameters.
            Each value should be a dictionary of keyword arguments
            for the corresponding node. Defaults to empty dict.

        Returns
        -------
        Dict[str, Any]
            Dictionary mapping node names to their outputs after execution.
            Contains results for all nodes in the graph.

        Notes
        -----
        The execution process:
        1. Iterates through nodes in topological order
        2. For each node:
           - Collects outputs from parent nodes
           - Combines with any provided input parameters
           - Executes the node's component
           - Stores the result for use by dependent nodes

        Examples
        --------
        >>> graph = Graph()
        >>> # ... add nodes and dependencies ...
        >>> results = graph(inputs={'node1': {'param1': 42}})
        >>> print(results['node1'])  # Access output of node1
        """
        if inputs is None:
            inputs = {}
        results = {}

        for node_name in self.sorted_nodes:
            print("Evaluating node: %s..." % node_name)
            node = self.nodes[node_name]
            
            # Gather inputs from parents if available, otherwise use provided inputs
            parent_outputs = [results[parent.name] for parent in node.parents]
            kwargs = inputs.get(node_name, {})
            
            # Execute node and store result
            results[node_name] = node(*parent_outputs, **kwargs)
        
        return results
