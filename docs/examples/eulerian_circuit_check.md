# Checking for Eulerian Circuits

This example demonstrates how to check if a CircuitCraft circuit forms an Eulerian 
cycle, which ensures proper data flow from terminal perches through backward movers
and back via forward movers.

## Creating a Circuit with an Eulerian Structure

```python
from circuitcraft import CircuitBoard, Perch

# Create a circuit
circuit = CircuitBoard(name="EulerianCircuit")

# Add perches (nodes)
circuit.add_perch(Perch("perch_A", {"comp": None, "sim": None}))  # Terminal perch
circuit.add_perch(Perch("perch_B", {"comp": None, "sim": None}))  # Intermediate
circuit.add_perch(Perch("perch_C", {"comp": None, "sim": None}))  # Initial perch

# Define computational methods
def backward_op_1(data):
    """Backward operation from B to A"""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp * 2}
    return {}

def backward_op_2(data):
    """Backward operation from C to B"""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp + 5}
    return {}

def forward_op_1(data):
    """Forward operation from A to B"""
    comp = data.get("comp")
    sim = data.get("sim")
    if comp is not None and sim is not None:
        return {"sim": sim + 0.5 * comp}
    return {}

def forward_op_2(data):
    """Forward operation from B to C"""
    comp = data.get("comp")
    sim = data.get("sim")
    if comp is not None and sim is not None:
        return {"sim": sim * 0.8}
    return {}

def forward_op_3(data):
    """Forward operation from C to A (closing the cycle)"""
    comp = data.get("comp")
    sim = data.get("sim")
    if comp is not None and sim is not None:
        return {"sim": sim + comp}
    return {}

# Connect perches with backward movers
circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_A",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

circuit.add_mover(
    source_name="perch_C", 
    target_name="perch_B",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

# Connect perches with forward movers
circuit.add_mover(
    source_name="perch_A", 
    target_name="perch_B",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_C",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

circuit.add_mover(
    source_name="perch_C", 
    target_name="perch_A",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

# Set computational methods
circuit.set_mover_comp("perch_B", "perch_A", "backward", backward_op_1)
circuit.set_mover_comp("perch_C", "perch_B", "backward", backward_op_2)
circuit.set_mover_comp("perch_A", "perch_B", "forward", forward_op_1)
circuit.set_mover_comp("perch_B", "perch_C", "forward", forward_op_2)
circuit.set_mover_comp("perch_C", "perch_A", "forward", forward_op_3)

# Finalize the model
circuit.finalize_model()
```

## Checking for an Eulerian Circuit

Now that we have created our circuit, we can check if it forms an Eulerian circuit:

```python
# Check if the circuit forms an Eulerian cycle
is_eulerian = circuit.is_eulerian_circuit()
print(f"The circuit is Eulerian: {is_eulerian}")  # Should be True

# Find the actual Eulerian path
eulerian_path = circuit.find_eulerian_path()
if eulerian_path:
    print("Eulerian path found:")
    print(" -> ".join(eulerian_path))
else:
    print("No Eulerian path found.")
```

## Visualizing the Eulerian Circuit

We can also visualize the Eulerian circuit:

```python
try:
    # Visualize the Eulerian circuit
    fig = circuit.visualize_eulerian_path()
    
    # Save the visualization
    fig.savefig("eulerian_circuit.png")
    print("Visualization saved to 'eulerian_circuit.png'")
except ImportError:
    print("Matplotlib is required for visualization.")
```

## Creating a Non-Eulerian Circuit

Let's modify our circuit to make it non-Eulerian by removing the edge from C to A:

```python
# Create a non-Eulerian circuit by removing the closing edge
non_eulerian_circuit = CircuitBoard(name="NonEulerianCircuit")

# Add the same perches
for perch_name in ["perch_A", "perch_B", "perch_C"]:
    non_eulerian_circuit.add_perch(Perch(perch_name, {"comp": None, "sim": None}))

# Add the same backward movers
non_eulerian_circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_A",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

non_eulerian_circuit.add_mover(
    source_name="perch_C", 
    target_name="perch_B",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

# Add only two forward movers (missing C to A)
non_eulerian_circuit.add_mover(
    source_name="perch_A", 
    target_name="perch_B",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

non_eulerian_circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_C",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

# Finalize the model
non_eulerian_circuit.finalize_model()

# Check if the circuit is Eulerian
is_eulerian = non_eulerian_circuit.is_eulerian_circuit()
print(f"The non-Eulerian circuit is Eulerian: {is_eulerian}")  # Should be False
```

## Why Eulerian Circuits Matter

In CircuitCraft, an Eulerian circuit ensures that:

1. The circuit has a proper cycle that allows data to flow from terminal perches 
   through backward solving and then back to the same terminal perches via forward 
   simulation.

2. Every perch in the circuit can be reached through the backward solving process 
   and contributes to the forward simulation.

3. The economic model represented by the circuit is structurally sound and can 
   generate meaningful simulations based on optimal policies.

Checking for Eulerian properties helps validate the design of your CircuitCraft 
circuits and ensures they will produce meaningful results when solved. 