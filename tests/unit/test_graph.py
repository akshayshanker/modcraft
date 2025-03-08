import pytest
import networkx as nx

from graphcraft.graph import Graph
from graphcraft.node import Node


class TestGraph:
    """
    Test suite for the Graph class functionality.
    """

    def test_graph_initialization(self):
        """
        Test that a Graph is properly initialized with empty collections.
        """
        graph = Graph()
        assert graph.nodes == {}
        assert isinstance(graph.graph, nx.DiGraph)
        assert len(graph.graph.nodes) == 0
        assert len(graph.graph.edges) == 0

    def test_add_node(self):
        """
        Test adding nodes to the graph.
        """
        graph = Graph()
        node1 = Node("node1", lambda: None)
        node2 = Node("node2", lambda: None)

        # Add nodes
        graph.add_node(node1)
        graph.add_node(node2)

        # Check node references
        assert "node1" in graph.nodes
        assert "node2" in graph.nodes
        assert graph.nodes["node1"] is node1
        assert graph.nodes["node2"] is node2

        # Check NetworkX graph
        assert "node1" in graph.graph.nodes
        assert "node2" in graph.graph.nodes

    def test_add_duplicate_node(self):
        """
        Test that adding a node with a duplicate name raises an error.
        """
        graph = Graph()
        node1 = Node("same_name", lambda: None)
        node2 = Node("same_name", lambda: None)

        graph.add_node(node1)
        
        # Adding a node with the same name should raise ValueError
        with pytest.raises(ValueError) as excinfo:
            graph.add_node(node2)
        
        assert "already exists" in str(excinfo.value)

    def test_add_dependency(self):
        """
        Test adding dependencies between nodes.
        """
        graph = Graph()
        node1 = Node("node1", lambda: None)
        node2 = Node("node2", lambda: None)

        graph.add_node(node1)
        graph.add_node(node2)
        
        # Add dependency: node1 -> node2
        graph.add_dependency("node1", "node2")

        # Check Node objects for parent-child relationship
        assert node1 in node2.parents
        assert node2 in node1.children

        # Check NetworkX graph for edge
        assert graph.graph.has_edge("node1", "node2")
        
        # Check topological sort
        assert graph.sorted_nodes == ["node1", "node2"]

    def test_add_dependency_nonexistent_node(self):
        """
        Test that adding a dependency with nonexistent nodes raises an error.
        """
        graph = Graph()
        node1 = Node("node1", lambda: None)
        graph.add_node(node1)
        
        with pytest.raises(ValueError) as excinfo:
            graph.add_dependency("node1", "nonexistent")
        
        assert "must be added before" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            graph.add_dependency("nonexistent", "node1")
        
        assert "must be added before" in str(excinfo.value)

    def test_add_cyclic_dependency(self):
        """
        Test that adding a cyclic dependency raises an error.
        """
        graph = Graph()
        node1 = Node("node1", lambda: None)
        node2 = Node("node2", lambda: None)
        node3 = Node("node3", lambda: None)

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        # Create a valid path: node1 -> node2 -> node3
        graph.add_dependency("node1", "node2")
        graph.add_dependency("node2", "node3")
        
        # Try to create a cycle: node3 -> node1
        with pytest.raises(ValueError) as excinfo:
            graph.add_dependency("node3", "node1")
        
        assert "cycle" in str(excinfo.value)
        
        # Ensure the graph remains unchanged after the failed operation
        assert not graph.graph.has_edge("node3", "node1")
        assert node3 not in node1.parents
        assert node1 not in node3.children

    def test_sorted_nodes(self):
        """
        Test that nodes are properly topologically sorted.
        """
        graph = Graph()
        
        # Create a more complex graph structure
        # A -> B -> D
        # |         ^
        # v         |
        # C --------|
        
        node_a = Node("A", lambda: None)
        node_b = Node("B", lambda: None)
        node_c = Node("C", lambda: None)
        node_d = Node("D", lambda: None)
        
        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)
        graph.add_node(node_d)
        
        graph.add_dependency("A", "B")
        graph.add_dependency("A", "C")
        graph.add_dependency("B", "D")
        graph.add_dependency("C", "D")
        
        # The topological sort could be either ["A", "B", "C", "D"] or ["A", "C", "B", "D"]
        # Both are valid, but we need to ensure A comes first and D comes last
        sorted_nodes = graph.sorted_nodes
        
        assert sorted_nodes[0] == "A"
        assert sorted_nodes[-1] == "D"
        assert set(sorted_nodes[1:3]) == {"B", "C"}

    def test_call_execution(self):
        """
        Test that the graph correctly executes nodes in topological order.
        """
        graph = Graph()
        
        # Create simple numeric functions
        def double(x):
            return x * 2
        
        def add_five(x):
            return x + 5
        
        def square(x):
            return x ** 2
        
        # Add nodes to the graph
        node1 = Node("double", double)
        node2 = Node("add_five", add_five)
        node3 = Node("square", square)
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        # Create a linear pipeline: double -> add_five -> square
        graph.add_dependency("double", "add_five")
        graph.add_dependency("add_five", "square")
        
        # Execute the graph with initial input 3
        results = graph(inputs={"double": {"x": 3}})
        
        # Verify results
        # double(3) = 6
        # add_five(6) = 11
        # square(11) = 121
        assert results["double"] == 6
        assert results["add_five"] == 11
        assert results["square"] == 121

    def test_call_with_complex_dependencies(self):
        """
        Test execution with more complex dependency patterns.
        """
        graph = Graph()
        
        # Define test functions
        def add(a, b):
            return a + b
        
        def multiply(a, b):
            return a * b
        
        def power(base, exponent=2):
            return base ** exponent
        
        # Add nodes to graph
        graph.add_node(Node("add1", add))
        graph.add_node(Node("add2", add))
        graph.add_node(Node("multiply", multiply))
        graph.add_node(Node("power", power))
        
        # Create dependency structure:
        # add1 ----> multiply ---> power
        #       /
        # add2 -
        graph.add_dependency("add1", "multiply")
        graph.add_dependency("add2", "multiply")
        graph.add_dependency("multiply", "power")
        
        # Execute with inputs
        results = graph(inputs={
            "add1": {"a": 2, "b": 3},    # 2 + 3 = 5
            "add2": {"a": 4, "b": 6},    # 4 + 6 = 10
            "power": {"exponent": 3}     # Custom exponent
        })
        
        # Verify results
        assert results["add1"] == 5              # 2 + 3 = 5
        assert results["add2"] == 10             # 4 + 6 = 10
        assert results["multiply"] == 50         # 5 * 10 = 50
        
        # Power node should receive multiple parents:
        # - First arg from multiply: 50
        # - Keyword arg exponent=3 (from inputs)
        assert results["power"] == 125000        # 50^3 = 125000

    def test_call_without_inputs(self):
        """
        Test graph execution without explicit inputs.
        """
        graph = Graph()
        
        # Create a simple node with a function that takes no arguments
        def get_constant():
            return 42
        
        node = Node("constant", get_constant)
        graph.add_node(node)
        
        # Execute without inputs
        results = graph()
        
        assert results["constant"] == 42

    def test_cached_property_behavior(self):
        """
        Test that the sorted_nodes cached property works correctly.
        """
        graph = Graph()
        
        # Add nodes
        graph.add_node(Node("A", lambda: None))
        graph.add_node(Node("B", lambda: None))
        
        # First access - compute and cache
        first_access = graph.sorted_nodes
        
        # Modify the internal graph directly to bypass cache invalidation
        # (this is to test that the property is actually cached)
        graph.graph.add_node("C")
        
        # Second access - should return cached value
        second_access = graph.sorted_nodes
        
        # Should be the same list object (not recomputed)
        assert first_access is second_access
        assert "C" not in second_access