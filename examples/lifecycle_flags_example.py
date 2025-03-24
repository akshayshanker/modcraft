"""
CircuitCraft 1.2.0 Example: Lifecycle Flags and New Terminology
-------------------------------------------------------
This example demonstrates the new CircuitCraft 1.2.0 features:
1. New terminology: Perch (formerly Node), CircuitBoard (formerly Graph), Mover (formerly Edge)
2. Renamed attributes: comp (formerly function), sim (formerly distribution)
3. Lifecycle flags to track circuit board state through the workflow
4. Extended Mover with parameters and numerical_hyperparameters
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
        # When running from examples directory with src structure
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import CircuitBoard, Perch
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to your PYTHONPATH"
        )

# Define computational methods for our movers
def backward_operation(data):
    """Square the comp value (backward operation)"""
    x = data.get("comp")
    if x is not None:
        # Return dictionary with the transformed comp value
        return {"comp": x**2}
    return {}

def forward_operation(data):
    """Transform sim based on comp (forward operation)"""
    comp = data.get("comp")
    sim = data.get("sim") 
    if comp is not None and sim is not None:
        # Multiply the sim value by the parameter value and add comp
        scale = data.get("parameters", {}).get("scale", 0.5)
        return {"sim": sim + scale * comp}
    return {}

# Create a circuit board
print("\n1. Create a circuit board")
circuit = CircuitBoard(name="LifecycleDemo")
print(f"Circuit created: {circuit}")
print(f"Lifecycle flags:")
print(f"  has_empty_perches: {circuit.has_empty_perches}")
print(f"  has_model: {circuit.has_model}")
print(f"  movers_backward_exist: {circuit.movers_backward_exist}")
print(f"  is_portable: {circuit.is_portable}")
print(f"  is_solvable: {circuit.is_solvable}")
print(f"  is_solved: {circuit.is_solved}")
print(f"  is_simulated: {circuit.is_simulated}")

# Add perches (formerly nodes)
print("\n2. Add perches to the circuit board")
perch_0 = Perch("perch_0", {"comp": None, "sim": None})
perch_1 = Perch("perch_1", {"comp": None, "sim": None})
perch_2 = Perch("perch_2", {"comp": None, "sim": None})

circuit.add_perch(perch_0)
circuit.add_perch(perch_1)
circuit.add_perch(perch_2)
print(f"Perches added: {circuit}")

# Add movers (formerly edges)
print("\n3. Add movers to the circuit board")

# Backward mover from perch_1 to perch_0
circuit.add_mover(
    source_name="perch_1", 
    target_name="perch_0", 
    map_data={"operation": "square"},
    parameters={"description": "Squares the input value"},
    numerical_hyperparameters={"precision": 1e-6},
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

# Forward mover from perch_0 to perch_1
circuit.add_mover(
    source_name="perch_0", 
    target_name="perch_1", 
    map_data={"operation": "linear_transform"},
    parameters={"scale": 0.7, "description": "Scale and add"},
    numerical_hyperparameters={"precision": 1e-6},
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

# Forward mover from perch_1 to perch_2
circuit.add_mover(
    source_name="perch_1", 
    target_name="perch_2", 
    map_data={"operation": "linear_transform"},
    parameters={"scale": 0.3, "description": "Scale and add"},
    numerical_hyperparameters={"precision": 1e-6},
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

print(f"Movers added to circuit")
print(f"Lifecycle flags:")
print(f"  has_empty_perches: {circuit.has_empty_perches}")
print(f"  has_model: {circuit.has_model}")
print(f"  movers_backward_exist: {circuit.movers_backward_exist}")

# Finalize the model
print("\n4. Finalize the model")
circuit.finalize_model()
print(f"Model finalized")
print(f"Lifecycle flags:")
print(f"  has_model: {circuit.has_model}")
print(f"  is_solvable: {circuit.is_solvable}")

# Make the circuit portable
print("\n5. Make the circuit portable")

def comp_factory(data):
    """Create a comp function from the mover's map, parameters, and hyperparameters"""
    map_data = data.get("map", {})
    parameters = data.get("parameters", {})
    
    operation = map_data.get("operation")
    if operation == "square":
        return backward_operation
    elif operation == "linear_transform":
        # Capture parameters in closure for use in forward_operation
        def custom_forward_op(data_dict):
            # Add parameters to data dict for forward_operation to use
            data_dict["parameters"] = parameters
            return forward_operation(data_dict)
        return custom_forward_op
    else:
        # Default identity function
        return lambda x: x

circuit.make_portable(comp_factory)
print(f"Circuit is now portable")
print(f"Lifecycle flags:")
print(f"  is_portable: {circuit.is_portable}")

# Initialize with values
print("\n6. Initialize perches with values")
circuit.set_perch_data("perch_1", {"comp": 4.0})  # Initial comp value for backward solve
circuit.set_perch_data("perch_0", {"sim": 3.0})   # Initial sim value for forward simulation

print(f"Initial values set")
print(f"Lifecycle flags:")
print(f"  has_empty_perches: {circuit.has_empty_perches}")
print(f"  is_solvable: {circuit.is_solvable}")

# Execute movers one by one to show the process
print("\n7. Execute individual movers")

# Execute backward mover from perch_1 to perch_0
print("  Executing backward mover (perch_1 -> perch_0)...")
result = circuit.execute_mover("perch_1", "perch_0", edge_type="backward")
print(f"  Result: {result}")
print(f"  perch_0.comp = {circuit.get_perch_data('perch_0', 'comp')}")

# Now execute forward movers
print("  Executing forward mover (perch_0 -> perch_1)...")
result = circuit.execute_mover("perch_0", "perch_1", edge_type="forward")
print(f"  Result: {result}")
print(f"  perch_1.sim = {circuit.get_perch_data('perch_1', 'sim')}")

print("  Executing forward mover (perch_1 -> perch_2)...")
result = circuit.execute_mover("perch_1", "perch_2", edge_type="forward")
print(f"  Result: {result}")
print(f"  perch_2.sim = {circuit.get_perch_data('perch_2', 'sim')}")

# Print flag status
print(f"  Lifecycle flags:")
print(f"  is_solved: {circuit.is_solved}")
print(f"  is_simulated: {circuit.is_simulated}")

# Solve the entire circuit
print("\n8. Solve the entire circuit automatically")
circuit.solve()
print(f"Circuit solved")
print(f"Lifecycle flags:")
print(f"  is_solved: {circuit.is_solved}")
print(f"  is_simulated: {circuit.is_simulated}")

# Final results
print("\n9. Final results:")
print(f"perch_0.comp = {circuit.get_perch_data('perch_0', 'comp')}")  # Should be 16.0 (4² = 16)
print(f"perch_0.sim = {circuit.get_perch_data('perch_0', 'sim')}")    # Should be 3.0
print(f"perch_1.comp = {circuit.get_perch_data('perch_1', 'comp')}")  # Should be 4.0
print(f"perch_1.sim = {circuit.get_perch_data('perch_1', 'sim')}")    # Should be 3.0 + 0.7*16 = 14.2
print(f"perch_2.comp = {circuit.get_perch_data('perch_2', 'comp')}")  # Should be None
print(f"perch_2.sim = {circuit.get_perch_data('perch_2', 'sim')}")    # Should be 14.2 + 0.3*4 = 15.4

print("\nCircuit board final state:")
print(circuit) 