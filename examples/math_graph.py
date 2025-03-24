"""
CircuitCraft 1.2.0 Example: Mathematical Circuit with Matrix Operations
----------------------------------------------------------------------
This example demonstrates the CircuitCraft concept where:
- Perches represent data (inputs and outputs)
- Movers represent operations between perches

The example includes both backward and forward operations:
1. Backward operations: Add and Power
2. Forward operations: MatrixMultiply
"""

import pprint
import sys
import os
import numpy as np

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

def main():
    print("CircuitCraft 1.2.0 Math Circuit Example")
    print("-------------------------------")

    # Define computational methods
    def add(data):
        """Add two arrays"""
        a = data.get("a")
        b = data.get("b")
        if a is not None and b is not None:
            return {"comp": a + b}
        return {}

    def power(data):
        """Raise array to a power"""
        comp_value = data.get("comp")
        if comp_value is not None:
            return {"comp": comp_value ** 3}
        return {}

    def matrix_multiply(data):
        """Multiply matrices"""
        matrix_a = data.get("matrix_a")
        matrix_c = data.get("matrix_c")
        if matrix_a is not None and matrix_c is not None:
            return {"sim": np.matmul(matrix_a, matrix_c)}
        return {}

    # Create our NumPy arrays to be operated on
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.array([[2, 4, 6], [8, 10, 12]])
    c = np.array([[1, 0], [0, 1], [2, 1]])  # A 3x2 matrix for the forward operation

    # 1. CIRCUIT CREATION
    print("\n1. CIRCUIT CREATION")
    
    # Create a circuit
    circuit = CircuitBoard(name="MathCircuit")
    
    # Add perches with appropriate data keys
    circuit.add_perch(Perch("add_result", {"comp": None, "sim": None, "a": None, "b": None}))
    # Make sure power_result has both 'comp' and 'matrix_c' keys
    circuit.add_perch(Perch("power_result", {"comp": None, "sim": None, "matrix_a": None, "matrix_c": None}))
    circuit.add_perch(Perch("transformed_matrix", {"comp": None, "sim": None}))
    
    # Add movers
    # Backward mover
    circuit.add_mover(
        source_name="add_result", 
        target_name="power_result",
        source_key="comp", 
        target_key="comp",
        edge_type="backward"
    )
    
    # Forward mover
    circuit.add_mover(
        source_name="power_result", 
        target_name="transformed_matrix",
        source_keys=["matrix_a", "matrix_c"], 
        target_key="sim",
        edge_type="forward"
    )
    
    print(f"Circuit board created with 3 perches and 2 movers")
    
    # 2. MODEL FINALIZATION
    print("\n2. MODEL FINALIZATION")
    
    # Define maps for movers
    power_map = {
        "operation": "power",
        "parameters": {"exponent": 3}
    }
    
    matrix_multiply_map = {
        "operation": "matrix_multiply",
        "parameters": {}
    }
    
    # Assign maps to movers
    circuit.set_mover_map("add_result", "power_result", "backward", power_map)
    circuit.set_mover_map("power_result", "transformed_matrix", "forward", matrix_multiply_map)
    
    # Define computational methods for movers
    # Set comp functions directly
    circuit.set_mover_comp("add_result", "power_result", "backward", power)
    circuit.set_mover_comp("power_result", "transformed_matrix", "forward", matrix_multiply)
    
    # Finalize the model
    circuit.finalize_model()
    print(f"Circuit model finalized: has_model={circuit.has_model}")
    
    # 3. PORTABILITY
    print("\n3. PORTABILITY")
    
    # Make the circuit portable
    circuit.make_portable()
    print(f"Circuit is now portable: {circuit.is_portable}")
    
    # 4. INITIALIZATION
    print("\n4. INITIALIZATION")
    
    # Initialize with values
    circuit.set_perch_data("add_result", {"comp": a + b, "a": a, "b": b})  # Pre-compute addition for simplicity
    
    # Initialize power_result with both required values
    sum_ab_cubed = ((a + b) ** 3)  # Pre-compute the value for clarity
    circuit.set_perch_data("power_result", {
        "comp": sum_ab_cubed,  # Set comp for forward operations
        "matrix_a": sum_ab_cubed, # Also set as matrix_a for the matrix multiplication
        "matrix_c": c           # Set matrix_c for forward operations
    })
    
    # Also initialize transformed_matrix perch
    circuit.set_perch_data("transformed_matrix", {"comp": None, "sim": None})
    
    # Check lifecycle flags
    print("\nLIFECYCLE FLAGS:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    # Debug information
    print("\nDEBUG INFO:")
    for perch_name in circuit.backward_graph.nodes():
        perch = circuit.perches[perch_name]
        print(f"Perch {perch_name} initialized keys: {perch.get_initialized_keys()}")
        
        # Check predecessors in backward graph
        predecessors = list(circuit.backward_graph.predecessors(perch_name))
        print(f"Perch {perch_name} predecessors in backward graph: {predecessors}")
        
        if not predecessors:
            print(f"Perch {perch_name} is a terminal perch in backward graph")
    
    # 5. SOLUTION
    print("\n5. SOLUTION")
    
    # Solve the circuit
    if circuit.is_solvable:
        print("Solving circuit...")
        circuit.solve()
        
        # Print the results
        print("\nCircuit execution results:")
        print(f"Lifecycle flags after solving:")
        print(f"is_solved: {circuit.is_solved}")
        print(f"is_simulated: {circuit.is_simulated}")
        
        power_result = circuit.get_perch_data("power_result", "comp")
        transformed_matrix = circuit.get_perch_data("transformed_matrix", "sim")
        
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
