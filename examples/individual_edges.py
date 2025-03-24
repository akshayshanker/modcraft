"""
CircuitCraft Example: Individual Edge Execution
----------------------------------------------
This example demonstrates how to execute individual edges in a circuit
and work directly with functions as operations.
"""

import numpy as np
import sys
import os

# Try different import approaches to make the script runnable from various locations
try:
    # When running from the project root or if package is installed
    from circuitcraft.graph import Graph
    from circuitcraft.node import Node
except ImportError:
    try:
        # When running from examples directory with src structure
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft.graph import Graph
        from src.circuitcraft.node import Node
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to your PYTHONPATH"
        )


def matrix_transform(matrix, vector):
    """Transform a matrix using a vector through rank-1 updates."""
    v_column = vector.reshape(-1, 1)  # Column vector
    outer_product = v_column @ v_column.T  # Outer product
    return matrix + 0.1 * (matrix @ outer_product)  # Apply transformation


def main():
    """Demonstrate individual edge execution in a circuit."""
    print("CircuitCraft Example: Individual Edge Execution")
    print("=" * 60)
    
    # Create a circuit
    circuit = Graph(name="IndividualOperations")
    
    # Add nodes
    circuit.add_node(Node("node_0", {"vector": None, "matrix": None}))
    circuit.add_node(Node("node_1", {"vector": None, "matrix": None}))
    
    # Following the updated 4-step workflow
    
    # 1. Circuit Creation - Create the structure without operations
    # Only create a forward edge since that seems to work correctly
    circuit.add_edge("node_0", "node_1", edge_type="forward")
    
    print("\n1. CIRCUIT CREATION")
    print("Created circuit with 2 nodes and 1 edge (no operations yet)")
    
    # 2. Configuration - Assign operations to edges
    # Configure the forward edge operation
    circuit.set_edge_operation("node_0", "node_1", matrix_transform,
                              source_keys=["matrix", "vector"], target_key="matrix",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()
    
    print("\n2. CONFIGURATION")
    print(f"Circuit configured: {circuit.is_configured}")
    
    # 3. Initialization - Set initial values
    # Create initial data
    initial_vector = np.array([2.0, 3.0, 4.0])
    initial_matrix = np.array([
        [1.0, 0.1, 0.2],
        [0.1, 2.0, 0.3],
        [0.2, 0.3, 3.0]
    ])
    
    # Initialize nodes with data
    circuit.set_node_data("node_1", {"vector": initial_vector})
    circuit.set_node_data("node_0", {"matrix": initial_matrix, "vector": initial_vector})
    
    # Mark as initialized
    circuit.is_initialized = True
    
    print("\n3. INITIALIZATION")
    print(f"Circuit initialized: {circuit.is_initialized}")
    print(f"Circuit is solvable: {circuit.is_solvable}")
    
    # For debugging, print the graph structures
    print("\nForward graph edges:")
    for edge in circuit.forward_graph.edges():
        print(f"  {edge[0]} → {edge[1]}")
    
    # 4. Individual Edge Execution
    print("\n4. INDIVIDUAL EDGE EXECUTION")
    
    # Execute forward edge: node_0 → node_1
    print("\nExecuting forward edge: node_0 → node_1")
    result_forward = circuit.execute_edge("node_0", "node_1", "forward")
    
    print(f"Matrix shape in node_0: {initial_matrix.shape}")
    print(f"Result matrix shape in node_1: {result_forward.shape}")
    print(f"First element of original matrix: {initial_matrix[0,0]}")
    print(f"First element of transformed matrix: {result_forward[0,0]}")
    
    print("\n5. VERIFY ALL NODES CONTAIN RESULTS")
    # Get current state of all nodes
    node0_vector = circuit.get_node_data("node_0", "vector")
    node0_matrix = circuit.get_node_data("node_0", "matrix")
    node1_vector = circuit.get_node_data("node_1", "vector")
    node1_matrix = circuit.get_node_data("node_1", "matrix")
    
    print(f"node_0 vector shape: {node0_vector.shape}")
    print(f"node_0 matrix shape: {node0_matrix.shape}")
    print(f"node_1 vector shape: {node1_vector.shape}")
    print(f"node_1 matrix shape: {node1_matrix.shape}")
    
    print("\nCOMPARISON WITH FULL SOLVE")
    print("Individual edge execution allows fine-grained control over")
    print("which operations to run and when to run them.")
    print("The same result could be achieved with:")
    print("1. circuit.solve_forward() for forward edges")
    print("\nThis is useful for:")
    print("- Debugging specific operations")
    print("- Stepwise model solution")
    print("- Custom execution sequences")
    print("- Partial graph updates")


if __name__ == "__main__":
    main()