# CircuitCraft Examples

This section contains examples demonstrating various aspects of CircuitCraft.

## Basic Examples

- [Minimal Circuit](minimal_circuit.md): A simple example showing the basic CircuitCraft workflow
- [Mathematical Operations](math_operations.md): How to implement mathematical operations in a circuit
- [Simplified Interface](simplified_interface.md): Using the high-level functions for circuit creation and solving

## Advanced Examples

- [Economic Model](economic_model.md): A more complex example showing how to model an economic system
- [Eulerian Circuit Check](eulerian_circuit_check.md): How to check if a circuit forms an Eulerian cycle

## Example Structure

Each example follows a consistent structure:

1. **Problem Setup**: Description of the problem to be solved
2. **Circuit Creation**: How to create the circuit with perches and movers
3. **Circuit Configuration**: How to configure the computational methods
4. **Circuit Initialization**: How to initialize the circuit with initial values
5. **Circuit Solution**: How to solve the circuit
6. **Result Analysis**: How to interpret the results

Choose an example that most closely matches your use case to get started with CircuitCraft.

## Example Snippets

### Minimal Circuit

```python
from src.circuitcraft import CircuitBoard, Perch

# Create a basic circuit
circuit = CircuitBoard(name="SimpleCircuit")

# Add perches
circuit.add_perch(Perch("perch_0", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_1", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_2", {"comp": None, "sim": None}))

# Define computational methods
def square(data):
    """Square the comp value (backward operation)"""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp**2}
    return {}

def add_half(data):
    """Add half the comp value to the sim value (forward operation)"""
    comp = data.get("comp")
    sim = data.get("sim") 
    if comp is not None and sim is not None:
        return {"sim": sim + 0.5 * comp}
    return {}

# Connect perches with movers
circuit.add_mover(
    source_name="perch_1", 
    target_name="perch_0",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

# Initialize with values
circuit.set_perch_data("perch_1", {"comp": 4.0})    # For backward solving
circuit.set_perch_data("perch_0", {"sim": 3.0})     # For forward simulation

# Solve the circuit
circuit.solve()

# Access results
comp0 = circuit.get_perch_data("perch_0", "comp")  # Should be 16 (4² = 16)
print(f"perch_0.comp = {comp0}")
```

### Using the Simplified Interface

```python
from circuitcraft import create_and_solve_circuit

# Create and solve a circuit in one step
math_circuit = create_and_solve_circuit(
    name="QuickMathCircuit",
    # Define component layout
    nodes=[
        {"id": "node_0", "data_types": ["policy", "distribution"]},
        {"id": "node_1", "data_types": ["policy", "distribution"]},
        {"id": "node_2", "data_types": ["distribution"]}
    ],
    # Define connection topology
    edges=[
        {"source": "node_1", "target": "node_0", "operation": Square(), 
         "source_key": "policy", "target_key": "policy", "edge_type": "backward"},
        {"source": "node_0", "target": "node_1", "operation": MatrixOperation(),
         "source_keys": ["distribution", "policy"], "target_key": "distribution",
         "edge_type": "forward"},
    ],
    # Initialize values
    initial_values={
        "node_0": {"distribution": initial_distribution},
        "node_1": {"policy": initial_policy}
    }
) 