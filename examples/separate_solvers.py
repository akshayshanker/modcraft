"""
CircuitCraft Example: Separate Backward and Forward Solvers
----------------------------------------------------------
This example demonstrates using the backward and forward solvers separately.
"""

import numpy as np
import sys
import os

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


# Define operations as plain functions
def square(x):
    """Square each element of the input array."""
    if x is None:
        return None
    return x**2


def policy_transform(policy, state):
    """Compute a new policy based on a state, used in forward step."""
    # Simplified policy update - add state to policy
    if policy is None or state is None:
        return None
    return policy + 0.1 * state


def state_transition(state, policy):
    """State transition function, used in forward step."""
    # Simplified state transition - multiply by policy
    if state is None or policy is None:
        return None
    return state * policy


def run_manual_example():
    """Run an example with manual circuit creation and separate solvers."""
    print("\n1. MANUAL CIRCUIT CREATION AND SEPARATE SOLVING")
    print("-" * 50)
    
    # 1. Create circuit and nodes
    circuit = Graph(name="SeparateSolvers")
    
    circuit.add_node(Node("state", {"value": None}))
    circuit.add_node(Node("policy", {"value": None}))
    circuit.add_node(Node("next_state", {"value": None}))
    circuit.add_node(Node("next_policy", {"value": None}))
    
    # 2. Add structure (edge without operations)
    # Add backward edges - policy depends on state
    circuit.add_edge("policy", "state", edge_type="backward")
    
    # Add forward edges - next_state depends on state and policy
    circuit.add_edge("state", "next_state", edge_type="forward")
    circuit.add_edge("policy", "next_policy", edge_type="forward")
    
    # Add operations to edges
    # Backward operations
    circuit.set_edge_operation("policy", "state", square,
                              source_key="value", target_key="value",
                              edge_type="backward")
    
    # Forward operations
    circuit.set_edge_operation("state", "next_state", state_transition,
                              source_keys=["value", "value"], target_key="value",
                              edge_type="forward")
    
    circuit.set_edge_operation("policy", "next_policy", policy_transform,
                              source_keys=["value", "value"], target_key="value",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()
    print("Circuit configured successfully")
    
    # 3. Initialize the circuit
    initial_state = np.array([1.0, 2.0, 3.0])
    
    # Set initial values
    circuit.set_node_data("state", {"value": initial_state})
    
    # Debug: Print backward graph structure
    print("\nBackward graph edges:")
    for edge in circuit.backward_graph.edges():
        print(f"  {edge[0]} → {edge[1]}")
    
    # Debug: Print initialization status of each node
    print("\nNode initialization status:")
    for node_name, node in circuit.nodes.items():
        print(f"  {node_name}:")
        for key in node.get_data_keys():
            print(f"    {key}: {node.is_initialized(key)}")
    
    # Debug: Check if individual nodes are terminal in backward graph
    print("\nTerminal nodes in backward graph:")
    for node_name in circuit.nodes:
        predecessors = list(circuit.backward_graph.predecessors(node_name))
        print(f"  {node_name}: terminal={len(predecessors) == 0}, predecessors={predecessors}")
    
    # Fix: Initialize ALL terminal nodes in the backward graph (state, next_state, next_policy)
    # Make sure we're providing actual values, not None, to nodes that will be used as sources
    print("\nInitializing all terminal nodes in backward graph...")
    # State is already initialized with actual values
    dummy_array = np.zeros((1,))  # Dummy value for initialization
    circuit.set_node_data("next_state", {"value": dummy_array})  
    circuit.set_node_data("next_policy", {"value": dummy_array})  
    circuit.set_node_data("policy", {"value": dummy_array})  # This will be overwritten in backward step
    
    print("\nNode initialization status after fix:")
    for node_name, node in circuit.nodes.items():
        print(f"  {node_name}:")
        for key in node.get_data_keys():
            print(f"    {key}: {node.is_initialized(key)}")
    
    # Optional initialization check
    circuit.is_initialized = True
    print(f"Circuit initialized: {circuit.is_initialized}")
    print(f"Circuit is solvable: {circuit.is_solvable}")
    
    # 4. Solve backward first
    print("\nSolving backward...")
    circuit.solve_backward()
    
    # Check results of backward solve
    policy_result = circuit.get_node_data("policy", "value")
    print(f"Policy after backward solve: {policy_result}")
    print(f"Verification (state squared): {initial_state**2}")
    
    # 5. Solve forward
    print("\nSolving forward...")
    circuit.solve_forward()
    
    # Check results of forward solve
    next_state_result = circuit.get_node_data("next_state", "value")
    next_policy_result = circuit.get_node_data("next_policy", "value")
    
    print(f"Next state: {next_state_result}")
    print(f"Next policy: {next_policy_result}")
    
    print("\nVerifying next_state calculation:")
    print(f"Manual calculation (state * policy): {initial_state * policy_result}")
    
    print("\nVerifying next_policy calculation:")
    print(f"Manual calculation (policy + 0.1*state): {policy_result + 0.1 * initial_state}")


def run_alternative_api_example():
    """Run an example using the alternative API with explicit solve calls."""
    print("\n2. ALTERNATIVE API EXAMPLE")
    print("-" * 50)
    
    # Create circuit using the alternative API with the 4-step workflow
    circuit = Graph(name="SeparateSolversAlt")
    
    # 1. Circuit Creation: Add nodes and edges without operations
    circuit.add_node(Node("state", {"value": None}))
    circuit.add_node(Node("policy", {"value": None}))
    circuit.add_node(Node("next_state", {"value": None}))
    circuit.add_node(Node("next_policy", {"value": None}))
    
    # Add edges without operations
    circuit.add_edge("policy", "state", edge_type="backward")
    circuit.add_edge("state", "next_state", edge_type="forward")
    circuit.add_edge("policy", "next_policy", edge_type="forward")
    
    print("Circuit structure created")
    
    # 2. Configuration: Assign operations to edges
    circuit.set_edge_operation("policy", "state", square,
                              source_key="value", target_key="value",
                              edge_type="backward")
    
    circuit.set_edge_operation("state", "next_state", state_transition,
                              source_keys=["value", "value"], target_key="value",
                              edge_type="forward")
    
    circuit.set_edge_operation("policy", "next_policy", policy_transform,
                              source_keys=["value", "value"], target_key="value",
                              edge_type="forward")
    
    # Configure the circuit
    circuit.configure()
    print(f"Circuit configured: {circuit.is_configured}")
    
    # Debug: Print backward graph structure
    print("\nBackward graph edges:")
    for edge in circuit.backward_graph.edges():
        print(f"  {edge[0]} → {edge[1]}")
    
    # Debug: Check if individual nodes are terminal in backward graph
    print("\nTerminal nodes in backward graph:")
    for node_name in circuit.nodes:
        predecessors = list(circuit.backward_graph.predecessors(node_name))
        print(f"  {node_name}: terminal={len(predecessors) == 0}, predecessors={predecessors}")
    
    # 3. Initialization: Set initial values AND initialize all terminal nodes
    initial_state = np.array([4.0, 5.0, 6.0])
    dummy_array = np.zeros((1,))  # Dummy value for initialization
    
    circuit.set_node_data("state", {"value": initial_state})
    circuit.set_node_data("policy", {"value": dummy_array})  # Will be computed
    circuit.set_node_data("next_state", {"value": dummy_array})  
    circuit.set_node_data("next_policy", {"value": dummy_array})  
    
    # Mark as initialized
    circuit.is_initialized = True
    
    # Debug: Print node initialization status
    print("\nNode initialization status:")
    for node_name, node in circuit.nodes.items():
        print(f"  {node_name}:")
        for key in node.get_data_keys():
            print(f"    {key}: {node.is_initialized(key)}")
    
    print(f"Circuit initialized: {circuit.is_initialized}")
    print(f"Circuit is solvable: {circuit.is_solvable}")
    
    # 4a. Solve backward
    print("\nSolving backward...")
    circuit.solve_backward()
    
    # Check results of backward solve
    policy_result = circuit.get_node_data("policy", "value")
    print(f"Policy after backward solve: {policy_result}")
    print(f"Verification (state squared): {initial_state**2}")
    
    # 4b. Solve forward
    print("\nSolving forward...")
    circuit.solve_forward()
    
    # Check results
    next_state_result = circuit.get_node_data("next_state", "value")
    next_policy_result = circuit.get_node_data("next_policy", "value")
    
    print(f"Next state: {next_state_result}")
    print(f"Next policy: {next_policy_result}")
    
    print("\nVerifying next_state calculation:")
    print(f"Manual calculation (state * policy): {initial_state * policy_result}")
    
    print("\nVerifying next_policy calculation:")
    print(f"Manual calculation (policy + 0.1*state): {policy_result + 0.1 * initial_state}")


def main():
    """Run the examples for separate backward and forward solvers."""
    print("CircuitCraft Example: Separate Backward and Forward Solvers")
    print("=" * 60)
    
    # Run the example with manual circuit creation and separate solves
    run_manual_example()
    
    # Run the example with the alternative 4-step API
    run_alternative_api_example()
    
    print("\nSUMMARY")
    print("-" * 50)
    print("This example demonstrated:")
    print("1. Using backward solver to compute policy from state")
    print("2. Using forward solver to compute next state and policy")
    print("3. Verifying calculations through manual verification")
    print("4. Using both the manual approach and the 4-step workflow API")


if __name__ == "__main__":
    main() 