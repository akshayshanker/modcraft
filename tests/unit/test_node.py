import pytest

from graphcraft.node import Node


class TestNode:
    """
    Test suite for the Node class functionality.
    """

    def test_node_initialization(self):
        """
        Test that a Node is properly initialized with the expected attributes.
        """
        # Create a simple callable for the component
        def dummy_function(x, y):
            return x + y

        # Initialize the node
        node = Node("test_node", dummy_function)

        # Check attributes
        assert node.name == "test_node"
        assert node.component == dummy_function
        assert node.parents == []
        assert node.children == []

    def test_node_callable(self):
        """
        Test that a Node properly delegates to its component when called.
        """
        # Test with a simple function
        def adder(a, b):
            return a + b

        node = Node("adder", adder)
        result = node(3, 4)
        assert result == 7

        # Test with a class that implements __call__
        class Multiplier:
            def __call__(self, a, b):
                return a * b

        mult_component = Multiplier()
        node = Node("multiplier", mult_component)
        result = node(5, 6)
        assert result == 30

        # Test with keyword arguments
        def power(base, exponent=2):
            return base ** exponent

        node = Node("power", power)
        result = node(2, exponent=3)
        assert result == 8

    def test_add_parent(self):
        """
        Test that parent-child relationships are properly established.
        """
        node1 = Node("parent", lambda: None)
        node2 = Node("child", lambda: None)

        # Add parent to child
        node2.add_parent(node1)

        # Check bidirectional relationship
        assert node1 in node2.parents
        assert node2 in node1.children
        assert len(node2.parents) == 1
        assert len(node1.children) == 1

    def test_multiple_parents_children(self):
        """
        Test that a node can have multiple parents and children.
        """
        parent1 = Node("parent1", lambda: None)
        parent2 = Node("parent2", lambda: None)
        child = Node("child", lambda: None)
        grandchild1 = Node("grandchild1", lambda: None)
        grandchild2 = Node("grandchild2", lambda: None)

        # Setup the relationships
        child.add_parent(parent1)
        child.add_parent(parent2)
        grandchild1.add_parent(child)
        grandchild2.add_parent(child)

        # Verify parent-child relationships
        assert parent1 in child.parents
        assert parent2 in child.parents
        assert child in parent1.children
        assert child in parent2.children

        assert child in grandchild1.parents
        assert child in grandchild2.parents
        assert grandchild1 in child.children
        assert grandchild2 in child.children

        # Check counts
        assert len(child.parents) == 2
        assert len(parent1.children) == 1
        assert len(parent2.children) == 1
        assert len(child.children) == 2