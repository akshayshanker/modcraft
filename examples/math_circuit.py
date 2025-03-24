"""
CircuitCraft Example: Mathematical Operations Circuit
------------------------------------------------
This example demonstrates the CircuitCraft workflow:
1. Circuit Creation: Create circuit board structure with perches and movers (without maps or computations)
2. Model Finalization: Finalize the model once all components are added
3. Portability: Create computational methods from maps
4. Initialization: Provide initial values for perch data
5. Solution: Execute movers to compute results

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
    from src.circuitcraft import CircuitBoard
    from src.circuitcraft import Perch
except ImportError:
    try:
        # When running from examples directory
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.circuitcraft import CircuitBoard
        from src.circuitcraft import Perch
    except ImportError:
        raise ImportError(
            "Unable to import circuitcraft. Make sure you're either:\n"
            "1. Running from the project root directory\n"
            "2. Have installed the package with 'pip install -e .'\n"
            "3. Have added the project root to PYTHONPATH"
        )

def main():
    print("CircuitCraft 1.2.0 Mathematical Circuit Example")
    print("------------------------------------------")
    
    #--------------------------------------------------
    # 1. CIRCUIT CREATION
    #--------------------------------------------------
    print("\n1. CIRCUIT CREATION")
    
    # Create the circuit board
    circuit = CircuitBoard(name="MathCircuit")
    print(f"Empty circuit board created: {circuit.name}")
    
    # Add perches (formerly nodes)
    circuit.add_perch(Perch("perch_0", {"comp": None, "sim": None, "vector": None, "matrix": None}))
    circuit.add_perch(Perch("perch_1", {"comp": None, "sim": None, "vector": None, "matrix": None}))
    circuit.add_perch(Perch("perch_2", {"comp": None, "sim": None, "vector": None, "matrix": None}))
    print(f"Added 3 perches to the circuit board")
    
    # Add movers without maps or computational methods first
    # Add the perch_1 ↔ perch_0 connection
    circuit.add_mover(
        source_name="perch_1", 
        target_name="perch_0", 
        source_key="vector", 
        target_key="vector",
        edge_type="backward"
    )
    
    # Add the perch_1 ↔ perch_2 connection
    circuit.add_mover(
        source_name="perch_1", 
        target_name="perch_2", 
        source_keys=["matrix", "vector"], 
        target_key="matrix",
        edge_type="forward"
    )
    
    print(f"Added movers connecting all perches (without maps or computational methods)")
    print(f"Circuit board structure creation complete")
    
    #--------------------------------------------------
    # 2. MODEL FINALIZATION
    #--------------------------------------------------
    print("\n2. MODEL FINALIZATION")
    
    # Define maps (mathematical representations)
    backward_map = {
        "operation": "square",
        "parameters": {}
    }
    
    forward_map = {
        "operation": "transform",
        "parameters": {
            "scale_factor": 0.1
        }
    }
    
    # Assign maps to movers
    # For perch_1 ↔ perch_0 connection (backward):
    circuit.set_mover_map("perch_1", "perch_0", "backward", backward_map)
    circuit.set_mover_parameters("perch_1", "perch_0", "backward", {"description": "Squares each element in a vector"})
    circuit.set_mover_numerical_hyperparameters("perch_1", "perch_0", "backward", {"precision": 1e-6})
    
    # For perch_1 ↔ perch_2 connection (forward):
    circuit.set_mover_map("perch_1", "perch_2", "forward", forward_map)
    circuit.set_mover_parameters("perch_1", "perch_2", "forward", {"scale_factor": 0.1, "description": "Matrix transformation using vector"})
    circuit.set_mover_numerical_hyperparameters("perch_1", "perch_2", "forward", {"precision": 1e-6})
    
    # Finalize the model
    circuit.finalize_model()
    print(f"Circuit model finalized: has_model={circuit.has_model}")
    
    #--------------------------------------------------
    # 3. PORTABILITY
    #--------------------------------------------------
    print("\n3. PORTABILITY")
    
    # Define a comp factory to create computational implementations from maps
    def comp_factory(data):
        """Create a comp function from a map"""
        map_data = data.get("map", {})
        parameters = data.get("parameters", {})
        
        operation = map_data.get("operation")
        
        if operation == "square":
            def square_comp(data):
                """Square each element in a vector (backward operation)"""
                vector = data.get("vector")
                if vector is not None:
                    return {"vector": vector**2}
                return {}
            return square_comp
            
        elif operation == "transform":
            scale_factor = parameters.get("scale_factor", 0.1)
            
            def transform_comp(data):
                """Transform a matrix using a vector (forward operation)"""
                matrix = data.get("matrix")
                vector = data.get("vector")
                
                if matrix is not None and vector is not None:
                    # Create a column vector
                    v_column = vector.reshape(-1, 1)
                    # Create an outer product (rank-1 update)
                    outer_product = v_column @ v_column.T
                    # Apply transformation: scale original matrix + rank-1 update
                    result_matrix = matrix + scale_factor * (matrix @ outer_product)
                    return {"matrix": result_matrix}
                return {}
            return transform_comp
            
        # Default case
        return lambda data: {}
    
    # Make the circuit portable by creating computational methods from maps
    circuit.make_portable(comp_factory)
    print(f"Circuit is portable: {circuit.is_portable}")
    
    #--------------------------------------------------
    # 4. INITIALIZATION
    #--------------------------------------------------
    print("\n4. INITIALIZATION")
    
    # Create initial values
    # Initial vector in perch_1 (for backward operation)
    initial_vector = np.array([2.0, 3.0, 4.0])
    
    # Initial matrix in perch_0 (for forward operation)
    initial_matrix = np.array([
        [1.0, 0.1, 0.2],
        [0.1, 2.0, 0.3],
        [0.2, 0.3, 3.0]
    ])
    
    # Set initial values
    circuit.set_perch_data("perch_1", {"vector": initial_vector})
    circuit.set_perch_data("perch_0", {"matrix": initial_matrix, "vector": None})
    # Ensure perch_2 is also initialized
    circuit.set_perch_data("perch_2", {"vector": None, "matrix": None})
    
    # Debug info
    print("\nDEBUG INFO:")
    print(f"Backward graph nodes: {list(circuit.backward_graph.nodes())}")
    print(f"Backward graph edges: {list(circuit.backward_graph.edges())}")
    for perch_name in circuit.backward_graph.nodes():
        perch = circuit.perches[perch_name]
        print(f"Perch {perch_name} initialized keys: {perch.get_initialized_keys()}")
        for key in perch.get_data_keys():
            print(f"Perch {perch_name} {key}: {perch.get_data(key) is not None}")
        
        # Check predecessors in backward graph
        predecessors = list(circuit.backward_graph.predecessors(perch_name))
        print(f"Perch {perch_name} predecessors in backward graph: {predecessors}")
        
        if not predecessors:
            print(f"Perch {perch_name} is a terminal perch in backward graph")
            print(f"Perch {perch_name} is initialized: {perch.is_initialized()}")
    
    # Check lifecycle flags
    print("\nLIFECYCLE FLAGS:")
    print(f"has_empty_perches: {circuit.has_empty_perches}")
    print(f"has_model: {circuit.has_model}")
    print(f"movers_backward_exist: {circuit.movers_backward_exist}")
    print(f"is_portable: {circuit.is_portable}")
    print(f"is_solvable: {circuit.is_solvable}")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    #--------------------------------------------------
    # 5. SOLUTION
    #--------------------------------------------------
    print("\n5. SOLUTION")
    
    # Print backward and forward graphs
    print("\nBACKWARD GRAPH EDGES:")
    for source, target in circuit.backward_graph.edges():
        mover = circuit.backward_graph[source][target]["mover"]
        print(f"Mover {source} -> {target}: source_keys={mover.source_keys}, target_key={mover.target_key}")
        
    print("\nFORWARD GRAPH EDGES:")
    for source, target in circuit.forward_graph.edges():
        mover = circuit.forward_graph[source][target]["mover"]
        print(f"Mover {source} -> {target}: source_keys={mover.source_keys}, target_key={mover.target_key}")
    
    # Solve the circuit
    circuit.solve()
    print(f"Circuit solution complete:")
    print(f"is_solved: {circuit.is_solved}")
    print(f"is_simulated: {circuit.is_simulated}")
    
    # Get the results
    perch0_vector = circuit.get_perch_data("perch_0", "vector")
    perch1_matrix = circuit.get_perch_data("perch_1", "matrix")
    perch2_matrix = circuit.get_perch_data("perch_2", "matrix")
    
    # Display the results
    print("\nRESULTS:")
    print(f"Perch 0 vector: {perch0_vector}")
    print(f"Perch 1 matrix: {perch1_matrix}")
    print(f"Perch 2 matrix: {perch2_matrix}")
    
    # Display matrix shapes if not None
    if perch1_matrix is not None:
        print(f"Perch 1 matrix shape: {perch1_matrix.shape}")
    else:
        print("Perch 1 matrix is None")
        
    if perch2_matrix is not None:
        print(f"Perch 2 matrix shape: {perch2_matrix.shape}")
    else:
        print("Perch 2 matrix is None")
    
    # Show first element of each matrix to verify transformation
    print(f"Perch 0 matrix[0,0]: {initial_matrix[0,0]}")
    if perch1_matrix is not None:
        print(f"Perch 1 matrix[0,0]: {perch1_matrix[0,0]}")
    if perch2_matrix is not None:
        print(f"Perch 2 matrix[0,0]: {perch2_matrix[0,0]}")

if __name__ == "__main__":
    main() 