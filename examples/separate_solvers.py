"""
CircuitCraft 1.2.0 Example: Separate Backward and Forward Solvers
----------------------------------------------------------
This example demonstrates using the backward and forward solvers separately.
It shows the new terminology in CircuitCraft 1.2.0:
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
    from src.circuitcraft import CircuitBoard, Perch, create_and_solve_backward_circuit, create_and_solve_forward_circuit
except ImportError:
    try:
        # When running from examples directory with src structure
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import CircuitBoard, Perch, create_and_solve_backward_circuit, create_and_solve_forward_circuit
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to your PYTHONPATH"
        )


# Define computational methods

def square(data):
    """Square function for backward operation."""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp**2}
    return {}

def policy_transform(data):
    """Transform comp based on sim values."""
    comp = data.get("comp")
    sim = data.get("sim")
    if comp is not None and sim is not None:
        return {"comp": comp * sim}
    return {}

def state_transition(data):
    """Transition sim based on comp values."""
    sim = data.get("sim")
    comp = data.get("comp")
    if sim is not None and comp is not None:
        return {"sim": sim + 0.1 * comp}
    return {}


def run_manual_example():
    """
    Demonstrates manual control over backward and forward solving.
    """
    print("\nMANUAL BACKWARD AND FORWARD SOLVING")
    print("=" * 60)
    
    # 1. CIRCUIT CREATION
    print("\n1. CIRCUIT CREATION")
    
    # Create a circuit
    circuit = CircuitBoard(name="ManualSolvers")
    
    # Add perches
    circuit.add_perch(Perch("perch_0", {"comp": None, "sim": None}))
    circuit.add_perch(Perch("perch_1", {"comp": None, "sim": None}))
    circuit.add_perch(Perch("perch_2", {"comp": None, "sim": None}))
    
    # Add movers for backward solving
    circuit.add_mover(
        source_name="perch_1", 
        target_name="perch_0",
        source_key="comp", 
        target_key="comp",
        edge_type="backward"
    )
    
    circuit.add_mover(
        source_name="perch_2", 
        target_name="perch_1",
        source_key="comp", 
        target_key="comp",
        edge_type="backward"
    )
    
    # Add movers for forward solving
    circuit.add_mover(
        source_name="perch_0", 
        target_name="perch_1",
        source_keys=["comp", "sim"], 
        target_key="sim",
        edge_type="forward"
    )
    
    circuit.add_mover(
        source_name="perch_1", 
        target_name="perch_2",
        source_keys=["comp", "sim"], 
        target_key="sim",
        edge_type="forward"
    )
    
    print(f"Circuit board created with 3 perches and 4 movers (2 backward, 2 forward)")
    
    # 2. MODEL FINALIZATION
    print("\n2. MODEL FINALIZATION")
    
    # Define maps for movers
    square_map = {
        "operation": "square",
        "parameters": {}
    }
    
    state_transition_map = {
        "operation": "state_transition",
        "parameters": {}
    }
    
    # Set maps and computational methods for all movers
    # For backward movers
    circuit.set_mover_map("perch_1", "perch_0", "backward", square_map)
    circuit.set_mover_map("perch_2", "perch_1", "backward", square_map)
    
    # For forward movers
    circuit.set_mover_map("perch_0", "perch_1", "forward", state_transition_map)
    circuit.set_mover_map("perch_1", "perch_2", "forward", state_transition_map)
    
    # Define a comp factory that will turn maps into computational methods
    def comp_factory(data):
        """Create a computational method from a map."""
        map_data = data.get("map", {})
        operation = map_data.get("operation")
        
        if operation == "square":
            return square
        elif operation == "state_transition":
            return state_transition
        elif operation == "policy_transform":
            return policy_transform
        
        # Default fallback
        return lambda data: {}
    
    # Create computational methods for all movers
    circuit.create_comps_from_maps(comp_factory)
    
    # Finalize the model
    circuit.finalize_model()
    print(f"Circuit model finalized: has_model={circuit.has_model}")
    
    # 3. PORTABILITY
    print("\n3. PORTABILITY")
    print(f"Circuit is portable: {circuit.is_portable}")
    
    # 4. INITIALIZATION
    print("\n4. INITIALIZATION")
    
    # Initialize with terminal perch data
    circuit.set_perch_data("perch_2", {"comp": 5.0})
    circuit.set_perch_data("perch_0", {"sim": 2.0})
    
    # Check lifecycle flags
    print("\nLIFECYCLE FLAGS AFTER INITIALIZATION:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    
    # Checking why the circuit is not solvable
    # We need to verify that terminal perches in the backward graph have comp values
    # and initial perches in the forward graph have sim values
    terminal_backward = [name for name in circuit.backward_graph.nodes() 
                         if circuit.backward_graph.out_degree(name) == 0]
    initial_forward = [name for name in circuit.forward_graph.nodes() 
                       if circuit.forward_graph.in_degree(name) == 0]
    
    print(f"\nTerminal perches in backward graph: {terminal_backward}")
    print(f"Initial perches in forward graph: {initial_forward}")
    
    # Now make sure the circuit is solvable by ensuring these perches have values
    # Get any missing terminal perches that need comp values for backward solving
    missing_comp = [p for p in terminal_backward 
                   if circuit.get_perch_data(p, "comp") is None]
    
    # Get any missing initial perches that need sim values for forward solving
    missing_sim = [p for p in initial_forward 
                  if circuit.get_perch_data(p, "sim") is None]
    
    print(f"\nPerches missing comp values for backward solving: {missing_comp}")
    print(f"Perches missing sim values for forward solving: {missing_sim}")
    
    # Update the missing values to make the circuit solvable
    for p in missing_comp:
        circuit.set_perch_data(p, {"comp": 5.0})  # Set a default comp value
        print(f"Set {p}.comp = 5.0")
        
    for p in missing_sim:
        circuit.set_perch_data(p, {"sim": 2.0})  # Set a default sim value
        print(f"Set {p}.sim = 2.0")
    
    # Check if the circuit is now solvable
    print(f"\nCircuit is now solvable: {circuit.is_solvable}")
    
    # 5. SOLUTION - BACKWARD ONLY
    print("\n5. SOLUTION - BACKWARD ONLY")
    
    # Solve backward only
    circuit.solve(backward_only=True)
    print("Backward solution completed")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    # Print results of backward solving
    perch0_comp = circuit.get_perch_data("perch_0", "comp")
    perch1_comp = circuit.get_perch_data("perch_1", "comp")
    perch2_comp = circuit.get_perch_data("perch_2", "comp")
    
    print("\nBACKWARD SOLUTION RESULTS:")
    print(f"perch_0 comp: {perch0_comp}")  # Should be 5⁴ = 625
    print(f"perch_1 comp: {perch1_comp}")  # Should be 5² = 25
    print(f"perch_2 comp: {perch2_comp}")  # Initial value: 5
    
    # 6. SOLUTION - FORWARD ONLY
    print("\n6. SOLUTION - FORWARD ONLY")
    
    # Solve forward only (works because backward is already solved)
    circuit.solve(forward_only=True)
    print("Forward solution completed")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    # Print results of forward solving
    perch0_sim = circuit.get_perch_data("perch_0", "sim")
    perch1_sim = circuit.get_perch_data("perch_1", "sim")
    perch2_sim = circuit.get_perch_data("perch_2", "sim")
    
    print("\nFORWARD SOLUTION RESULTS:")
    print(f"perch_0 sim: {perch0_sim}")  # Initial value: 2.0
    print(f"perch_1 sim: {perch1_sim}")  # Should be 2.0 + 0.1 * 625 = 2.0 + 62.5 = 64.5
    print(f"perch_2 sim: {perch2_sim}")  # Should be 64.5 + 0.1 * 25 = 64.5 + 2.5 = 67.0
    
    print("\nThis example demonstrates how to solve backward and forward operations separately.")


def run_automated_example():
    """
    Demonstrates using the helper functions for separate backward and forward circuit creation.
    """
    print("\nAUTOMATED BACKWARD AND FORWARD SOLVING")
    print("=" * 60)
    
    def create_solver_circuit():
        """Create a circuit with backward and forward operations."""
        from circuitcraft import create_and_solve_backward_circuit, create_and_solve_forward_circuit
        
        # First, create and solve the backward circuit
        print("\n1. CREATING BACKWARD CIRCUIT")
        backward_circuit = create_and_solve_backward_circuit(
            name="BackwardCircuit",
            nodes=[
                {"id": "perch_0", "data_types": {"comp": None}},
                {"id": "perch_1", "data_types": {"comp": None}},
                {"id": "perch_2", "data_types": {"comp": None}}
            ],
            edges=[
                {"source": "perch_1", "target": "perch_0", "operation": square, "edge_type": "backward"},
                {"source": "perch_2", "target": "perch_1", "operation": square, "edge_type": "backward"}
            ],
            initial_values={
                "perch_0": {"comp": None},
                "perch_1": {"comp": None},
                "perch_2": {"comp": 5.0}  # Terminal condition
            }
        )
        
        # Print backward results
        perch0_comp = backward_circuit.get_perch_data("perch_0", "comp")
        perch1_comp = backward_circuit.get_perch_data("perch_1", "comp")
        perch2_comp = backward_circuit.get_perch_data("perch_2", "comp")
        
        print("\nBACKWARD CIRCUIT RESULTS:")
        print(f"perch_0 comp: {perch0_comp}")  # Should be 5⁴ = 625
        print(f"perch_1 comp: {perch1_comp}")  # Should be 5² = 25
        print(f"perch_2 comp: {perch2_comp}")  # Initial value: 5
        
        # Now, create and solve the forward circuit with the solved comp values
        print("\n2. CREATING FORWARD CIRCUIT")
        forward_circuit = create_and_solve_forward_circuit(
            name="ForwardCircuit",
            nodes=[
                {"id": "perch_0", "data_types": {"comp": None, "sim": None}},
                {"id": "perch_1", "data_types": {"comp": None, "sim": None}},
                {"id": "perch_2", "data_types": {"comp": None, "sim": None}}
            ],
            edges=[
                {"source": "perch_0", "target": "perch_1", "operation": state_transition, 
                 "source_keys": ["comp", "sim"], "target_key": "sim", "edge_type": "forward"},
                {"source": "perch_1", "target": "perch_2", "operation": state_transition,
                 "source_keys": ["comp", "sim"], "target_key": "sim", "edge_type": "forward"}
            ],
            initial_values={
                "perch_0": {"comp": perch0_comp, "sim": 2.0},  # Initial sim and solved comp from backward circuit
                "perch_1": {"comp": perch1_comp, "sim": None},  # Solved comp from backward circuit
                "perch_2": {"comp": perch2_comp, "sim": None}   # Solved comp from backward circuit
            }
        )
        
        # Print forward results
        perch0_sim = forward_circuit.get_perch_data("perch_0", "sim")
        perch1_sim = forward_circuit.get_perch_data("perch_1", "sim")
        perch2_sim = forward_circuit.get_perch_data("perch_2", "sim")
        
        print("\nFORWARD CIRCUIT RESULTS:")
        print(f"perch_0 sim: {perch0_sim}")  # Initial value: 2.0
        print(f"perch_1 sim: {perch1_sim}")  # Should be 2.0 + 0.1 * 625 = 64.5
        print(f"perch_2 sim: {perch2_sim}")  # Should be 64.5 + 0.1 * 25 = 67.0
        
        # Check lifecycle flags
        print("\nBACKWARD CIRCUIT LIFECYCLE FLAGS:")
        print(f"has_model: {backward_circuit.has_model}")
        print(f"is_solved: {backward_circuit.is_solved}")
        
        print("\nFORWARD CIRCUIT LIFECYCLE FLAGS:")
        print(f"has_model: {forward_circuit.has_model}")
        print(f"is_simulated: {forward_circuit.is_simulated}")
        
        return backward_circuit, forward_circuit
    
    # Run the example
    backward_circuit, forward_circuit = create_solver_circuit()
    
    print("\nThis example demonstrates using the helper functions create_and_solve_backward_circuit")
    print("and create_and_solve_forward_circuit to solve the backward and forward components separately.")
    print("This is useful for problems where you need to solve for policy functions first, then")
    print("use those policy functions to simulate distributions or other state variables.")


def main():
    """Run both examples."""
    print("CircuitCraft 1.2.0 Example: Separate Backward and Forward Solvers")
    print("-----------------------------------------------------------")
    
    run_manual_example()
    # The automated example is commented out as it needs more complex updates
    # run_automated_example()
    
    print("\nNote: The automated example using create_and_solve_backward_circuit and")
    print("create_and_solve_forward_circuit has been commented out as it requires")
    print("additional updates for CircuitCraft 1.2.0 compatibility.")


if __name__ == "__main__":
    main() 