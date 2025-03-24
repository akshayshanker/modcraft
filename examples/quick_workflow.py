"""
CircuitCraft Example: Quick Workflow with High-Level API
------------------------------------------------------
This example demonstrates the use of CircuitCraft's high-level API
to create and solve a circuit following the 4-step workflow:

1. Circuit Creation: Create the graph structure
2. Configuration: Assign operations to edges
3. Initialization: Provide initial values
4. Solution: Execute operations

The example shows how to use the `create_and_solve_circuit` function, 
which handles all four steps in one convenient call.
"""

import numpy as np
import sys
import os

# Try different import approaches to make the script runnable from various locations
try:
    # When running from the project root or if package is installed
    from src.circuitcraft import create_and_solve_circuit
except ImportError:
    try:
        # When running from examples directory
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import create_and_solve_circuit
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to PYTHONPATH"
        )

def main():
    print("CircuitCraft Quick Workflow Example")
    print("----------------------------------")
    
    # Define operations (simple functions)
    def square(x):
        """Square the input value (backward operation)"""
        return x**2
    
    def add_ten(x):
        """Add 10 to the input (forward operation)"""
        return x + 10
    
    # Create and solve a circuit in one high-level call
    # This handles all four workflow steps internally
    circuit = create_and_solve_circuit(
        name="QuickCircuit",
        
        # Step 1: Circuit Creation - Define nodes
        nodes=[
            {"id": "A", "data_types": {"value": None}},
            {"id": "B", "data_types": {"value": None}},
            {"id": "C", "data_types": {"value": None}}
        ],
        
        # Step 2: Configuration - Define edges with operations
        edges=[
            # Backward edge: B → A
            {"source": "B", "target": "A", 
             "operation": square, 
             "source_key": "value", "target_key": "value",
             "edge_type": "backward"},
            
            # Forward edge: A → B
            {"source": "A", "target": "B", 
             "operation": add_ten,
             "source_key": "value", "target_key": "value", 
             "edge_type": "forward"},
            
            # Forward edge: B → C
            {"source": "B", "target": "C", 
             "operation": add_ten,
             "source_key": "value", "target_key": "value",
             "edge_type": "forward"}
        ],
        
        # Step 3: Initialization - Set initial values
        initial_values={
            "A": {"value": None},  # Initialize node A with None
            "B": {"value": 5},     # Initial value at node B
            "C": {"value": None}   # Initialize node C with None
        }
    )
    
    # Verify circuit is solved
    print(f"\nCircuit solution status:")
    print(f"- Configured: {circuit.is_configured}")
    print(f"- Initialized: {circuit.is_initialized}")
    print(f"- Solved: {circuit.is_solved}")
    
    # Access results
    a_value = circuit.get_node_data("A", "value")
    b_value = circuit.get_node_data("B", "value")
    c_value = circuit.get_node_data("C", "value")
    
    print("\nRESULTS:")
    print(f"Node A value: {a_value}")   # 5² = 25
    print(f"Node B value: {b_value}")   # 25 + 10 = 35
    print(f"Node C value: {c_value}")   # 35 + 10 = 45
    
    print("\nHow it works internally:")
    print("1. Circuit Creation: Creates nodes A, B, C and connects them")
    print("2. Configuration: Assigns square and add_ten operations to edges")
    print("3. Initialization: Sets initial value for node B (value=5)")
    print("4. Solution: Executes operations in order:")
    print("   - Backward: B (5) → A, applying square: 5² = 25")
    print("   - Forward: A (25) → B, applying add_ten: 25 + 10 = 35")
    print("   - Forward: B (35) → C, applying add_ten: 35 + 10 = 45")

if __name__ == "__main__":
    main() 