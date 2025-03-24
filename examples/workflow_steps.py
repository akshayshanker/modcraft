"""
CircuitCraft 1.2.0 Example: Five-Step Workflow
----------------------------------------
This example demonstrates the updated 5-step CircuitCraft workflow:

1. Circuit Creation: Create circuit structure with perches and movers (without maps)
2. Model Finalization: Assign computational methods to movers and finalize the model
3. Portability: Create portable circuit board
4. Initialization: Provide initial values for perch data
5. Solution: Execute movers to compute results

This workflow separates mathematical representations (maps) from computational implementations (methods).
It also demonstrates the new terminology in CircuitCraft 1.2.0:
- Perch (formerly Node)
- CircuitBoard (formerly Graph)
- Mover (formerly Edge)
- comp (formerly function or policy)
- sim (formerly distribution or state)
"""

import numpy as np
import sys
import os

# Try different import approaches to make the script runnable from various locations
try:
    # When running from the project root or if package is installed
    from src.circuitcraft import CircuitBoard, Perch
except ImportError:
    try:
        # When running from examples directory
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import CircuitBoard, Perch
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to your PYTHONPATH"
        )


# Define computational methods
def square(data):
    """Square the comp value."""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp**2}
    return {}

def add_one(data):
    """Add 1 to the comp value."""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp + 1}
    return {}

def transform_sim(data):
    """Transform the sim value using the comp value."""
    comp = data.get("comp")
    sim = data.get("sim")
    if comp is not None and sim is not None:
        return {"sim": sim + 0.1 * comp}
    return {}


def main():
    print("CircuitCraft 1.2.0 Five-Step Workflow Example")
    print("-------------------------------------------")
    
    #--------------------------------------------------
    # 1. CIRCUIT CREATION - Structure only
    #--------------------------------------------------
    print("\n1. CIRCUIT CREATION (Structure only)")
    
    # Create the circuit
    circuit = CircuitBoard(name="FiveStepCircuit")
    
    # Add perches
    circuit.add_perch(Perch("X", {"comp": None, "sim": None}))
    circuit.add_perch(Perch("Y", {"comp": None, "sim": None}))
    circuit.add_perch(Perch("Z", {"comp": None, "sim": None}))
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER PERCH CREATION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    
    # Add movers without maps or computational methods
    # Backward mover: Y depends on X (X is the terminal perch)
    circuit.add_mover(
        source_name="Y", 
        target_name="X",
        source_key="comp", 
        target_key="comp",
        edge_type="backward"
    )
    
    # Forward mover: X goes to Z (X is the initial perch)
    circuit.add_mover(
        source_name="X", 
        target_name="Z",
        source_keys=["comp", "sim"], 
        target_key="sim",
        edge_type="forward"
    )
    
    print(f"Created circuit board with 3 perches and 2 movers (no maps or computational methods yet)")
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER MOVER CREATION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    
    # Debug: Print all movers
    print("\nDEBUG - Forward movers:")
    for source, target in circuit.forward_graph.edges():
        print(f"  {source} → {target}")
    
    print("\nDEBUG - Backward movers:")
    for source, target in circuit.backward_graph.edges():
        print(f"  {source} → {target}")
    
    #--------------------------------------------------
    # 2. MODEL FINALIZATION - Define computational methods
    #--------------------------------------------------
    print("\n2. MODEL FINALIZATION (Define computational methods)")
    
    # Create maps for movers
    square_map = {
        "operation": "square",
        "parameters": {}
    }
    
    transform_map = {
        "operation": "transform",
        "parameters": {}
    }
    
    # Set maps for movers
    # For Y → X connection (backward mover):
    circuit.set_mover_map("Y", "X", "backward", square_map)
    
    # For X → Z connection (forward mover):
    circuit.set_mover_map("X", "Z", "forward", transform_map)
    
    # Debug: Print movers with maps
    print("\nDEBUG - Movers with maps:")
    for source, target, data in circuit.backward_graph.edges(data=True):
        has_map = "map" in data and data["map"] is not None
        print(f"  {source} → {target} (backward): has map = {has_map}")

    for source, target, data in circuit.forward_graph.edges(data=True):
        has_map = "map" in data and data["map"] is not None
        print(f"  {source} → {target} (forward): has map = {has_map}")

    # Define a comp factory that will turn maps into computational methods
    def comp_factory(data):
        """Create a computational method from a map."""
        map_data = data.get("map", {})
        operation = map_data.get("operation")
        
        if operation == "square":
            return square
        elif operation == "add_one":
            return add_one
        elif operation == "transform":
            return transform_sim
        
        # Default fallback
        return lambda data: {}
    
    # Create computational methods for all movers
    circuit.create_comps_from_maps(comp_factory)
    
    # Finalize the model
    circuit.finalize_model()
    print(f"Circuit model finalized: has_model={circuit.has_model}")
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER MODEL FINALIZATION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    
    #--------------------------------------------------
    # 3. PORTABILITY - Make circuit portable
    #--------------------------------------------------
    print("\n3. PORTABILITY (Make circuit portable)")
    
    # The circuit is already portable after finalize_model()
    print(f"Circuit is portable: {circuit.is_portable}")
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER PORTABILITY CHECK:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    
    #--------------------------------------------------
    # 4. INITIALIZATION (Set perch data)
    #--------------------------------------------------
    print("\n4. INITIALIZATION (Set perch data)")
    
    # Initialize perch values for a valid backward solve:
    # X is the terminal perch in the backward graph, so it needs a comp value
    circuit.set_perch_data("X", {"comp": 5.0, "sim": 2.0})
    
    print(f"Circuit is now populated with initial values")
    print(f"Perch values after loading: X={circuit.get_perch_data('X', 'comp')}, "
          f"Y={circuit.get_perch_data('Y', 'comp')}, Z={circuit.get_perch_data('Z', 'comp')}")
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER INITIALIZATION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")

    #--------------------------------------------------
    # 5. SOLUTION (Execute the circuit)
    #--------------------------------------------------
    print("\n5. SOLUTION (Execute the circuit)")
    
    # Option 1: Execute individual movers manually
    print("\nOption 1: Manual mover execution")
    
    # Execute the backward mover from Y to X (which will compute Y's value)
    print("Executing mover from Y to X (backward)...")
    circuit.execute_mover("Y", "X", "backward")
    print(f"Y's value after backward mover execution: {circuit.get_perch_data('Y', 'comp')}")
    
    # Execute the forward mover from X to Z (which will compute Z's value)
    print("Executing mover from X to Z (forward)...")
    circuit.execute_mover("X", "Z", "forward") 
    print(f"Z's value after forward mover execution: {circuit.get_perch_data('Z', 'sim')}")
    
    print("\nManual execution results:")
    print(f"X: comp={circuit.get_perch_data('X', 'comp')}, sim={circuit.get_perch_data('X', 'sim')}")
    print(f"Y: comp={circuit.get_perch_data('Y', 'comp')}, sim={circuit.get_perch_data('Y', 'sim')}")
    print(f"Z: comp={circuit.get_perch_data('Z', 'comp')}, sim={circuit.get_perch_data('Z', 'sim')}")
    
    # Option 2: Use the solve method
    print("\nOption 2: Automatic solve")
    
    # Reset perch values
    circuit.set_perch_data("X", {"comp": 5.0, "sim": 2.0})
    circuit.set_perch_data("Y", {"comp": None, "sim": None})
    circuit.set_perch_data("Z", {"comp": None, "sim": None})
    
    print(f"Initial perch values: X={circuit.get_perch_data('X', 'comp')}, "
          f"Y={circuit.get_perch_data('Y', 'comp')}, Z={circuit.get_perch_data('Z', 'comp')}")
    
    # Call the solve method
    circuit.solve()
    
    print(f"Circuit state: is_solved={circuit.is_solved}, is_simulated={circuit.is_simulated}")
    
    print("\nAutomatic solve results:")
    print(f"X: comp={circuit.get_perch_data('X', 'comp')}, sim={circuit.get_perch_data('X', 'sim')}")
    print(f"Y: comp={circuit.get_perch_data('Y', 'comp')}, sim={circuit.get_perch_data('Y', 'sim')}")
    print(f"Z: comp={circuit.get_perch_data('Z', 'comp')}, sim={circuit.get_perch_data('Z', 'sim')}")
    
    # Print lifecycle flags
    print(f"\nLIFECYCLE FLAGS AFTER SOLUTION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    print("\nFive-step workflow complete!")


if __name__ == "__main__":
    main() 