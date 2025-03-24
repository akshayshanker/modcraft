"""
CircuitCraft Example: Mathematical Operations Circuit
------------------------------------------------
This example demonstrates the CircuitCraft workflow:
1. Circuit Creation: Create graph structure with nodes and edges (without operations)
2. Configuration: Assign operations to edges
3. Initialization: Provide initial values for node data
4. Solution: Execute operations to compute results

The example shows a simple mathematical circuit with:
- Backward operations that square vectors
- Forward operations that transform matrices
"""

import numpy as np
import sys
import os

# Try different import approaches to make the script runnable from various locations
try:
    # When running from the project root or if package is installed
    from src.circuitcraft.graph import Graph
    from src.circuitcraft.node import Node
except ImportError:
    try:
        # When running from examples directory
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft.graph import Graph
        from src.circuitcraft.node import Node
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to PYTHONPATH"
        )

def main():
    print("CircuitCraft Mathematical Circuit Example")
    print("------------------------------------------")
    
    #--------------------------------------------------
    # 1. CIRCUIT CREATION
    #--------------------------------------------------
    print("\n1. CIRCUIT CREATION")
    
    # Create the circuit
    circuit = Graph(name="MathCircuit")
    print(f"Empty circuit created: {circuit.name}")
    
    # Add nodes
    circuit.add_node(Node("node_0", {"vector": None, "matrix": None}))
    circuit.add_node(Node("node_1", {"vector": None, "matrix": None}))
    circuit.add_node(Node("node_2", {"vector": None, "matrix": None}))
    print(f"Added 3 nodes to the circuit")
    
    # Add edges without operations first
    # BACKWARD EDGE: node_1 → node_0
    circuit.add_edge("node_1", "node_0", edge_type="backward")
    
    # FORWARD EDGE: node_0 → node_1
    circuit.add_edge("node_0", "node_1", edge_type="forward")
    
    # FORWARD EDGE: node_1 → node_2
    circuit.add_edge("node_1", "node_2", edge_type="forward")
    
    print(f"Added edges connecting all nodes (without operations)")
    print(f"Circuit structure creation complete")
    
    #--------------------------------------------------
    # 2. CONFIGURATION
    #--------------------------------------------------
    print("\n2. CONFIGURATION")
    
    # Define operations
    def square_vector(vector):
        """Square each element in a vector (backward operation)"""
        return vector**2
    
    def transform_matrix(matrix, vector):
        """Transform a matrix using a vector (forward operation)"""
        # Create a column vector
        v_column = vector.reshape(-1, 1)
        # Create an outer product (rank-1 update)
        outer_product = v_column @ v_column.T
        # Apply transformation: scale original matrix + rank-1 update
        return matrix + 0.1 * (matrix @ outer_product)
    
    # Assign operations to edges
    # BACKWARD EDGE: node_1 → node_0
    circuit.set_edge_operation("node_1", "node_0", square_vector,
                               source_key="vector", target_key="vector",
                               edge_type="backward")
    
    # FORWARD EDGE: node_0 → node_1
    circuit.set_edge_operation("node_0", "node_1", transform_matrix,
                              source_keys=["matrix", "vector"], target_key="matrix",
                              edge_type="forward")
    
    # FORWARD EDGE: node_1 → node_2
    circuit.set_edge_operation("node_1", "node_2", transform_matrix,
                              source_keys=["matrix", "vector"], target_key="matrix",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()  # Validates the circuit structure
    print(f"Circuit is configured: {circuit.is_configured}")
    
    # Verify edge types
    print(f"Circuit has backward edges: {circuit.has_backward_edges}")
    print(f"Circuit has forward edges: {circuit.has_forward_edges}")
    
    #--------------------------------------------------
    # 3. INITIALIZATION
    #--------------------------------------------------
    print("\n3. INITIALIZATION")
    
    # Create initial values
    # Initial vector in node_1 (for backward operation)
    initial_vector = np.array([2.0, 3.0, 4.0])
    
    # Initial matrix in node_0 (for forward operation)
    initial_matrix = np.array([
        [1.0, 0.1, 0.2],
        [0.1, 2.0, 0.3],
        [0.2, 0.3, 3.0]
    ])
    
    # Set initial values
    circuit.set_node_data("node_1", {"vector": initial_vector})
    circuit.set_node_data("node_0", {"matrix": initial_matrix, "vector": None})
    # Ensure node_2 is also initialized
    circuit.set_node_data("node_2", {"vector": None, "matrix": None})
    
    # Mark as initialized
    circuit.is_initialized = True
    print(f"Circuit is initialized: {circuit.is_initialized}")
    print(f"Circuit is solvable: {circuit.is_solvable}")
    
    # Debug info
    print("\nDEBUG INFO:")
    print(f"Backward graph nodes: {list(circuit.backward_graph.nodes())}")
    print(f"Backward graph edges: {list(circuit.backward_graph.edges())}")
    for node_name in circuit.backward_graph.nodes():
        node = circuit.nodes[node_name]
        print(f"Node {node_name} is initialized: {node.is_initialized()}")
        for key in node.get_data_keys():
            print(f"Node {node_name} {key}: {node.get_data(key)}")
        
        # Check predecessors in backward graph
        predecessors = list(circuit.backward_graph.predecessors(node_name))
        print(f"Node {node_name} predecessors in backward graph: {predecessors}")
        
        if not predecessors:
            print(f"Node {node_name} is a terminal node in backward graph")
            print(f"Node {node_name} all values initialized: {node.is_initialized()}")
    
    #--------------------------------------------------
    # 4. SOLUTION
    #--------------------------------------------------
    print("\n4. SOLUTION")
    
    # Solve the circuit
    results = circuit.solve()
    print(f"Circuit solution complete: {circuit.is_solved}")
    
    # Get the results
    node0_vector = circuit.get_node_data("node_0", "vector")
    node1_matrix = circuit.get_node_data("node_1", "matrix")
    node2_matrix = circuit.get_node_data("node_2", "matrix")
    
    # Display the results
    print("\nRESULTS:")
    print(f"Node 0 vector: {node0_vector}")  # Should be [4.0, 9.0, 16.0]
    print(f"Node 1 matrix shape: {node1_matrix.shape}")
    print(f"Node 2 matrix shape: {node2_matrix.shape}")
    
    # Show first element of each matrix to verify transformation
    print(f"Node 0 matrix[0,0]: {initial_matrix[0,0]}")
    print(f"Node 1 matrix[0,0]: {node1_matrix[0,0]}")
    print(f"Node 2 matrix[0,0]: {node2_matrix[0,0]}")

if __name__ == "__main__":
    main() 