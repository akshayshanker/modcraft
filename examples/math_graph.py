import pprint
import sys
import os
import numpy as np

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

def main():
    """
    This example demonstrates the CircuitCraft concept where:
    - Nodes represent data (inputs and outputs)
    - Edges represent operations

    We have two types of operations:
    1. Backward operations: Add and Power
    2. Forward operations: MatrixMultiply
    """
    print("CircuitCraft Math Graph Example")
    print("-------------------------------")

    # Define operations as functions
    def add(a, b):
        return a + b

    def power(x, exponent=2):
        return x ** exponent

    def matrix_multiply(a, b):
        return np.matmul(a, b)

    # Create our NumPy arrays to be operated on
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.array([[2, 4, 6], [8, 10, 12]])
    c = np.array([[1, 0], [0, 1], [2, 1]])  # A 3x2 matrix for the forward operation

    # Create a circuit
    circuit = Graph(name="MathGraph")
    
    # Add nodes with appropriate data keys
    circuit.add_node(Node("add_result", {"value": None}))
    # Make sure power_result has both 'value' and 'matrix_c' keys
    circuit.add_node(Node("power_result", {"value": None, "matrix_c": None}))
    circuit.add_node(Node("transformed_matrix", {"value": None}))
    
    # Add edges
    # Backward operations
    circuit.add_edge("add_result", "power_result", edge_type="backward")
    
    # Forward operations
    circuit.add_edge("power_result", "transformed_matrix", edge_type="forward")
    
    # Configure the operations
    # Define a custom operation to raise to a power
    def power_operation(x):
        return x ** 3
    
    # Define a custom operation for matrix multiplication
    def matrix_multiply_operation(matrix_a, matrix_c):
        return np.matmul(matrix_a, matrix_c)
    
    # Assign operations to edges
    circuit.set_edge_operation("add_result", "power_result", power_operation,
                              source_key="value", target_key="value",
                              edge_type="backward")
    
    circuit.set_edge_operation("power_result", "transformed_matrix", matrix_multiply_operation,
                              source_keys=["value", "matrix_c"], target_key="value",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()
    print(f"Circuit configured: {circuit.is_configured}")
    
    # Initialize with values
    circuit.set_node_data("add_result", {"value": a + b})  # Pre-compute addition for simplicity
    
    # Initialize power_result with both required values
    # For proper initialization, set both value and matrix_c
    sum_ab_cubed = ((a + b) ** 3)  # Pre-compute the value for clarity
    circuit.set_node_data("power_result", {
        "value": sum_ab_cubed,  # Set value for forward operations
        "matrix_c": c           # Set matrix_c for forward operations
    })
    
    # Also initialize transformed_matrix node
    circuit.set_node_data("transformed_matrix", {"value": None})
    
    # Mark as initialized
    circuit.is_initialized = True
    
    # Debug information
    print("\nDEBUG INFO:")
    print(f"Circuit is initialized: {circuit.is_initialized}")
    print(f"Circuit is solvable: {circuit.is_solvable}")
    print(f"Backward graph nodes: {list(circuit.backward_graph.nodes())}")
    print(f"Backward graph edges: {list(circuit.backward_graph.edges())}")
    
    for node_name in circuit.backward_graph.nodes():
        node = circuit.nodes[node_name]
        print(f"Node {node_name} is initialized: {node.is_initialized()}")
        for key in node.get_data_keys():
            print(f"Node {node_name} {key}: {node.get_data(key) is not None}")
        
        # Check predecessors in backward graph
        predecessors = list(circuit.backward_graph.predecessors(node_name))
        print(f"Node {node_name} predecessors in backward graph: {predecessors}")
        
        if not predecessors:
            print(f"Node {node_name} is a terminal node in backward graph")
            print(f"Node {node_name} all values initialized: {node.is_initialized()}")
    
    # Verify node initialization
    print("\nVerifying node initialization...")
    for node_name, node in circuit.nodes.items():
        print(f"Node {node_name}: {node.is_initialized()}")
    
    # Solve the circuit
    if circuit.is_solvable:
        print("\nSolving circuit...")
        results = circuit.solve()
        
        # Print the results
        print("\nCircuit execution results:")
        power_result = circuit.get_node_data("power_result", "value")
        transformed_matrix = circuit.get_node_data("transformed_matrix", "value")
        
        print(f"Add result: {a + b}")
        print(f"Power result shape: {power_result.shape}")
        print(f"Transformed matrix shape: {transformed_matrix.shape}")
        
        # Show sample values
        print(f"\nSample power result[0,0]: {power_result[0,0]}")
        print(f"Sample transformed matrix[0,0]: {transformed_matrix[0,0]}")
        
        # Interpretation of results
        print("\nInterpretation:")
        print("1. Backward Operations:")
        print("   - Add operation (pre-computed): a + b")
        print("   - Power operation: (a + b) ^ 3")
        print("2. Forward Operation:")
        print("   - Matrix multiplication: [(a + b) ^ 3] × c")
        print("\nIn economic terms, this would be like:")
        print("   - Computing a policy function (backward operations)")
        print("   - Using that policy to transform a distribution (forward operation)")
    else:
        print("\nCircuit is not solvable. Check the debug information above.")

if __name__ == "__main__":
    main()
