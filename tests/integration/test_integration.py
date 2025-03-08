import numpy as np
import pytest

from graphcraft.graph import Graph
from graphcraft.node import Node


class TestIntegration:
    """
    Integration tests for the GraphCraft library.
    """

    def test_math_graph_example(self):
        """
        Test the math_graph.py example from the examples directory.
        """
        # Recreate the example from the documentation
        class Add:
            def __call__(self, a, b):
                return a + b

        class Power:
            def __call__(self, a, exponent=2):
                return a ** exponent

        # Instantiate callable functions
        add = Add()
        power = Power()

        # Create NumPy arrays
        a = np.array([[1, 2, 3], [4, 5, 6]])
        b = np.array([[2, 4, 6], [8, 10, 12]])

        # Set up the graph
        graph = Graph()
        graph.add_node(Node("add", add))
        graph.add_node(Node("power", power))
        graph.add_dependency("add", "power")

        # Define inputs and execute
        inputs = {
            "add": {"a": a, "b": b},
            "power": {"exponent": 3}
        }
        results = graph(inputs)

        # Verify results match expected outputs
        expected_add_result = np.array([[3, 6, 9], [12, 15, 18]])
        expected_power_result = np.array([[27, 216, 729], [1728, 3375, 5832]])

        np.testing.assert_array_equal(results["add"], expected_add_result)
        np.testing.assert_array_equal(results["power"], expected_power_result)

    def test_multiple_input_sources(self):
        """
        Test a graph with nodes that receive inputs from
        multiple parents and direct inputs.
        """
        # Define test functions
        class Concatenate:
            def __call__(self, *args):
                return np.concatenate(args, axis=0)

        class Scale:
            def __call__(self, arr, factor=1.0):
                return arr * factor

        class Sum:
            def __call__(self, arr):
                return np.sum(arr)

        # Create arrays
        arr1 = np.array([[1, 2], [3, 4]])
        arr2 = np.array([[5, 6], [7, 8]])

        # Set up graph
        graph = Graph()
        graph.add_node(Node("scale1", Scale()))
        graph.add_node(Node("scale2", Scale()))
        graph.add_node(Node("concat", Concatenate()))
        graph.add_node(Node("sum", Sum()))

        # Dependencies: scale1 -> concat <- scale2
        #                            |
        #                            v
        #                           sum
        graph.add_dependency("scale1", "concat")
        graph.add_dependency("scale2", "concat")
        graph.add_dependency("concat", "sum")

        # Execute with inputs
        inputs = {
            "scale1": {"arr": arr1, "factor": 2.0},
            "scale2": {"arr": arr2, "factor": 0.5}
        }
        results = graph(inputs)

        # Expected results
        expected_scale1 = arr1 * 2.0  # [[2, 4], [6, 8]]
        expected_scale2 = arr2 * 0.5  # [[2.5, 3], [3.5, 4]]
        expected_concat = np.concatenate([expected_scale1, expected_scale2], axis=0)
        expected_sum = np.sum(expected_concat)

        # Verify results
        np.testing.assert_array_equal(results["scale1"], expected_scale1)
        np.testing.assert_array_equal(results["scale2"], expected_scale2)
        np.testing.assert_array_equal(results["concat"], expected_concat)
        assert results["sum"] == expected_sum

    def test_complex_graph_with_branching(self):
        """
        Test a more complex graph with branching paths.
        """
        # Define test functions
        def add_one(x):
            return x + 1

        def multiply_by_two(x):
            return x * 2

        def subtract_three(x):
            return x - 3

        def sum_inputs(*args):
            return sum(args)

        # Create graph with branching structure:
        #            multiply_by_two --> subtract_three
        #           /                                  \
        # start --> add_one                             --> sum_inputs
        #           \                                  /
        #            \---------------------------------
        graph = Graph()
        graph.add_node(Node("start", lambda x: x))
        graph.add_node(Node("add_one", add_one))
        graph.add_node(Node("multiply_by_two", multiply_by_two))
        graph.add_node(Node("subtract_three", subtract_three))
        graph.add_node(Node("sum_inputs", sum_inputs))

        # Define dependencies
        graph.add_dependency("start", "add_one")
        graph.add_dependency("add_one", "multiply_by_two")
        graph.add_dependency("multiply_by_two", "subtract_three")
        graph.add_dependency("subtract_three", "sum_inputs")
        graph.add_dependency("add_one", "sum_inputs")

        # Execute with input 5
        results = graph(inputs={"start": {"x": 5}})

        # Expected flow:
        # start: 5
        # add_one: 5 + 1 = 6
        # multiply_by_two: 6 * 2 = 12
        # subtract_three: 12 - 3 = 9
        # sum_inputs: 6 + 9 = 15
        assert results["start"] == 5
        assert results["add_one"] == 6
        assert results["multiply_by_two"] == 12
        assert results["subtract_three"] == 9
        assert results["sum_inputs"] == 15

    def test_error_handling_during_execution(self):
        """
        Test that errors in node execution are properly propagated.
        """
        def faulty_function(x):
            raise ValueError("Intentional error for testing")

        def normal_function(x):
            return x * 2

        # Create graph
        graph = Graph()
        graph.add_node(Node("normal", normal_function))
        graph.add_node(Node("faulty", faulty_function))
        graph.add_dependency("normal", "faulty")

        # Execute with input - should raise the ValueError from faulty_function
        with pytest.raises(ValueError) as excinfo:
            graph(inputs={"normal": {"x": 5}})

        assert "Intentional error for testing" in str(excinfo.value)