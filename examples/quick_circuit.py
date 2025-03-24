"""
CircuitCraft Example: Quick Circuit Creation
--------------------------------------------
This example demonstrates CircuitCraft's high-level API for quick circuit
creation and solution using the create_and_solve_circuit function.
"""

import numpy as np
import sys
import os

# Try different import approaches to make the script runnable from various locations
try:
    # When running from the project root or if package is installed
    from circuitcraft import create_and_solve_circuit
except ImportError:
    try:
        # When running from examples directory with src structure
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import create_and_solve_circuit
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to PYTHONPATH"
        )


def square_operation(x):
    """Square a vector - used for backward edge operation."""
    return x**2  # Element-wise square


def matrix_transform(matrix, vector):
    """Transform matrix using vector - used for forward edge operation."""
    # Create a transformation using the vector to modify the matrix
    v_column = vector.reshape(-1, 1)  # Column vector
    outer_product = v_column @ v_column.T  # Outer product matrix
    return matrix + 0.1 * (matrix @ outer_product)  # Apply transformation


def main():
    """Run the quick circuit example."""
    print("CircuitCraft Example: Quick Circuit Creation")
    print("=" * 60)
    
    # Initial values
    initial_policy = np.array([2, 3, 4])
    initial_distribution = np.array([
        [1, 0.1, 0.2],
        [0.1, 2, 0.3],
        [0.2, 0.3, 3]
    ])
    
    # Create and solve circuit in one step
    circuit = create_and_solve_circuit(
        name="QuickMathCircuit",
        # Define nodes
        nodes=[
            {"id": "node_0", "data_types": {"policy": None, "distribution": None}},
            {"id": "node_1", "data_types": {"policy": None, "distribution": None}},
            {"id": "node_2", "data_types": {"distribution": None}}
        ],
        # Define edges with operations
        edges=[
            {"source": "node_1", "target": "node_0", "operation": square_operation, 
             "source_key": "policy", "target_key": "policy", "edge_type": "backward"},
            {"source": "node_0", "target": "node_1", "operation": matrix_transform,
             "source_keys": ["distribution", "policy"], "target_key": "distribution", "edge_type": "forward"},
            {"source": "node_1", "target": "node_2", "operation": matrix_transform,
             "source_keys": ["distribution", "policy"], "target_key": "distribution", "edge_type": "forward"},
        ],
        # Initialize values
        initial_values={
            "node_0": {"distribution": initial_distribution},
            "node_1": {"policy": initial_policy}
        }
    )
    
    # Check circuit state
    print("\nCircuit State:")
    print(f"Circuit name: {circuit.name}")
    print(f"Is configured: {circuit.is_configured}")
    print(f"Is initialized: {circuit.is_initialized}")
    print(f"Is solved: {circuit.is_solved}")
    
    # Access results
    policy = circuit.get_node_data("node_0", "policy")
    mu_1 = circuit.get_node_data("node_1", "distribution")
    mu_2 = circuit.get_node_data("node_2", "distribution")
    
    print("\nResults:")
    print(f"policy = {policy}")
    print(f"mu_1 shape = {mu_1.shape}")
    print(f"mu_2 shape = {mu_2.shape}")
    
    print("\nThis example demonstrates how CircuitCraft's high-level API can create")
    print("and solve a complete circuit in a single function call, while maintaining")
    print("the same computational model where:")
    print("- Nodes store data (policy functions, distributions)")
    print("- Edges contain operations (backward solvers, forward transformations)")
    print("- The solution follows a clear workflow of creation -> configuration -> initialization -> solution")


if __name__ == "__main__":
    main() 