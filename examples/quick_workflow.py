"""
CircuitCraft Example: Quick Workflow with High-Level API
------------------------------------------------------
This example demonstrates the use of CircuitCraft's high-level API
to create and solve a circuit following the workflow:

1. Circuit Creation: Create the circuit board structure with perches and movers
2. Model Finalization: Finalize the model once all components are added
3. Portability Check: Make the circuit portable for serialization
4. Initialization: Provide initial values
5. Solution: Execute operations

The example shows how to use the `create_and_solve_circuit` function, 
which handles all workflow steps in one convenient call.
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
    print("CircuitCraft 1.2.0 Quick Workflow Example")
    print("----------------------------------")
    
    # Define operations (simple functions)
    def square(data):
        """Square the comp value (backward operation)"""
        comp_value = data.get("comp")
        if comp_value is not None:
            return {"comp": comp_value**2}
        return {}
    
    def add_ten(data):
        """Add 10 to the sim value (forward operation)"""
        sim_value = data.get("sim")
        if sim_value is not None:
            return {"sim": sim_value + 10}
        return {}
    
    # Create and solve a circuit in one high-level call
    # This handles all workflow steps internally
    circuit = create_and_solve_circuit(
        name="QuickCircuit",
        
        # Circuit Creation - Define perches (formerly nodes)
        nodes=[
            {"id": "A", "data_types": {"comp": None, "sim": None}},
            {"id": "B", "data_types": {"comp": None, "sim": None}},
            {"id": "C", "data_types": {"comp": None, "sim": None}}
        ],
        
        # Configuration - Define movers (formerly edges) with operations
        edges=[
            # Backward mover: B → A
            {"source": "B", "target": "A", 
             "operation": square, 
             "source_key": "comp", "target_key": "comp",
             "edge_type": "backward"},
            
            # Forward mover: A → B
            {"source": "A", "target": "B", 
             "operation": add_ten,
             "source_key": "sim", "target_key": "sim", 
             "edge_type": "forward"},
            
            # Forward mover: B → C
            {"source": "B", "target": "C", 
             "operation": add_ten,
             "source_key": "sim", "target_key": "sim",
             "edge_type": "forward"}
        ],
        
        # Initialization - Set initial values
        initial_values={
            "A": {"comp": None, "sim": None},  # Initialize perch A with None
            "B": {"comp": 5, "sim": None},     # Initial comp value at perch B
            "C": {"comp": None, "sim": None}   # Initialize perch C with None
        }
    )
    
    # Verify circuit lifecycle flags
    print(f"\nCircuit board lifecycle status:")
    print(f"- has_model: {circuit.has_model}")
    print(f"- is_portable: {circuit.is_portable}")
    print(f"- is_solvable: {circuit.is_solvable}")
    print(f"- is_solved: {circuit.is_solved}")
    print(f"- is_simulated: {circuit.is_simulated}")
    
    # Access results (using get_perch_data instead of get_node_data)
    a_comp = circuit.get_perch_data("A", "comp")
    a_sim = circuit.get_perch_data("A", "sim")
    b_comp = circuit.get_perch_data("B", "comp")
    b_sim = circuit.get_perch_data("B", "sim")
    c_comp = circuit.get_perch_data("C", "comp")
    c_sim = circuit.get_perch_data("C", "sim")
    
    print("\nRESULTS:")
    print(f"Perch A - comp: {a_comp}, sim: {a_sim}")   # comp: 5² = 25, sim: None initially
    print(f"Perch B - comp: {b_comp}, sim: {b_sim}")   # comp: 5, sim: A's sim + 10 = None + 10
    print(f"Perch C - comp: {c_comp}, sim: {c_sim}")   # comp: None, sim: B's sim + 10
    
    print("\nHow it works internally:")
    print("1. Circuit Creation: Creates perches A, B, C and connects them with movers")
    print("2. Model Finalization: Finalizes the circuit board model")
    print("3. Portability: Makes the circuit portable for serialization")
    print("4. Initialization: Sets initial value for perch B (comp=5)")
    print("5. Solution: Executes operations in order:")
    print("   - Backward: B (comp=5) → A, applying square: 5² = 25")
    print("   - Forward: A (sim=None) → B, applying add_ten (if sim were not None)")
    print("   - Forward: B (sim=None) → C, applying add_ten (if sim were not None)")

if __name__ == "__main__":
    main() 