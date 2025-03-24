"""
CircuitCraft Example: Four-Step Workflow
----------------------------------------
This example demonstrates the updated 4-step CircuitCraft workflow:

1. Circuit Creation: Create graph structure with nodes and edges (without operations)
2. Configuration: Assign operations to edges
3. Initialization: Provide initial values for node data
4. Solution: Execute operations to compute results

This updated workflow separates the graph structure creation from the assignment of operations.
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
    print("CircuitCraft Four-Step Workflow Example")
    print("--------------------------------------")
    
    #--------------------------------------------------
    # 1. CIRCUIT CREATION - Graph structure only
    #--------------------------------------------------
    print("\n1. CIRCUIT CREATION (Graph structure only)")
    
    # Create the circuit
    circuit = Graph(name="FourStepCircuit")
    
    # Add nodes
    circuit.add_node(Node("A", {"value": None}))
    circuit.add_node(Node("B", {"value": None}))
    circuit.add_node(Node("C", {"value": None}))
    
    # Add edges without operations
    circuit.add_edge("B", "A", edge_type="backward")
    circuit.add_edge("A", "B", edge_type="forward")
    circuit.add_edge("B", "C", edge_type="forward")
    
    print(f"Created circuit with 3 nodes and 3 edges (no operations yet)")
    
    #--------------------------------------------------
    # 2. CONFIGURATION - Assign operations to edges
    #--------------------------------------------------
    print("\n2. CONFIGURATION (Assign operations)")
    
    # Define operations
    def square(x):
        """Square the input value (backward operation)"""
        return x**2
    
    def add_value(x):
        """Add 10 to the input value (forward operation)"""
        return x + 10
    
    # Assign operations to edges
    circuit.set_edge_operation("B", "A", square,
                              source_key="value", target_key="value",
                              edge_type="backward")
    
    circuit.set_edge_operation("A", "B", add_value,
                              source_key="value", target_key="value",
                              edge_type="forward")
    
    circuit.set_edge_operation("B", "C", add_value,
                              source_key="value", target_key="value",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()
    print(f"Operations assigned and circuit configured: {circuit.is_configured}")
    
    #--------------------------------------------------
    # 3. INITIALIZATION - Provide initial values
    #--------------------------------------------------
    print("\n3. INITIALIZATION (Set initial values)")
    
    # Set initial values
    circuit.set_node_data("B", {"value": 5})
    # Initialize all nodes
    circuit.set_node_data("A", {"value": None})
    circuit.set_node_data("C", {"value": None})
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
        print(f"Node {node_name} data: {node.get_data('value')}")
        
        # Check predecessors in backward graph
        predecessors = list(circuit.backward_graph.predecessors(node_name))
        print(f"Node {node_name} predecessors in backward graph: {predecessors}")
        
        if not predecessors:
            print(f"Node {node_name} is a terminal node in backward graph")
            print(f"Node {node_name} all values initialized: {node.is_initialized()}")
    
    #--------------------------------------------------
    # 4. SOLUTION - Execute operations
    #--------------------------------------------------
    print("\n4. SOLUTION (Execute operations)")
    
    # Solve the circuit
    results = circuit.solve()
    print(f"Circuit solution complete: {circuit.is_solved}")
    
    # Display results
    a_value = circuit.get_node_data("A", "value")
    b_value = circuit.get_node_data("B", "value")  
    c_value = circuit.get_node_data("C", "value")
    
    print("\nRESULTS:")
    print(f"Node A value: {a_value}")   # 5² = 25
    print(f"Node B value: {b_value}")   # 25 + 10 = 35
    print(f"Node C value: {c_value}")   # 35 + 10 = 45
    
    print("\nExecution flow:")
    print("1. Backward: B (5) → A, applying square operation: 5² = 25")
    print("2. Forward: A (25) → B, applying add_value: 25 + 10 = 35")
    print("3. Forward: B (35) → C, applying add_value: 35 + 10 = 45")

if __name__ == "__main__":
    main() 