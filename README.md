# CircuitCraft (v1.2.1)

CircuitCraft is a Python library for computing recursive functional operations 
commonly found in infinite dimensional decision making problems and economic models
with uncertainty and heterogeneous agents.

## Key Features

- **Bidirectional Data Flow**: Backward solving and forward simulation in the same circuit
- **Lifecycle Flags**: Track circuit state throughout the workflow
- **Functional Operators**: Maps and comps for representing mathematical operations
- **Individual Mover Execution**: Granular control over computational steps
- **Extended Perch Attributes**: Store arbitrary data in perches
- **Portability**: Save and load circuits for later use

## Installation

```bash
pip install circuitcraft
```

## Quick Start

```python
from circuitcraft import CircuitBoard, Perch

# Create a circuit
circuit = CircuitBoard(name="SimpleCircuit")

# Add perches (nodes)
circuit.add_perch(Perch("perch_A", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_B", {"comp": None, "sim": None}))

# Define computational methods
def square(data):
    """Square the comp value (backward operation)"""
    comp = data.get("comp")
    if comp is not None:
        return {"comp": comp**2}
    return {}

def add_half(data):
    """Add half the comp to sim (forward operation)"""
    comp = data.get("comp")
    sim = data.get("sim") 
    if comp is not None and sim is not None:
        return {"sim": sim + 0.5 * comp}
    return {}

# Connect perches with movers (edges)
circuit.add_mover(
    source_name="perch_B", 
    target_name="perch_A",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

circuit.add_mover(
    source_name="perch_A", 
    target_name="perch_B",
    source_keys=["comp", "sim"], 
    target_key="sim",
    edge_type="forward"
)

# Set computational methods
circuit.set_mover_comp("perch_B", "perch_A", "backward", square)
circuit.set_mover_comp("perch_A", "perch_B", "forward", add_half)

# Finalize model
circuit.finalize_model()

# Initialize with values
circuit.set_perch_data("perch_B", {"comp": 4.0})  # For backward solving
circuit.set_perch_data("perch_A", {"sim": 3.0})   # For forward simulation

# Solve the circuit
circuit.solve()

# Access results
comp_A = circuit.get_perch_data("perch_A", "comp")  # Should be 16 (4² = 16)
sim_B = circuit.get_perch_data("perch_B", "sim")    # Should be 3 + 0.5*16 = 11

print(f"perch_A.comp = {comp_A}")
print(f"perch_B.sim = {sim_B}")
```

## Key Concepts

- **Circuit-Board**: A directed multi-graph representing a computational circuit
- **Perch**: A node in the circuit-board that stores data attributes (`comp` and `sim`)
- **Mover**: A directional connection between perches that performs operations on data
- **Computational Methods**: Functions that transform data as it flows between perches
- **Backward Solving**: Computation from terminal perches backward to initial perches
- **Forward Simulation**: Computation from initial perches forward to terminal perches
- **Lifecycle Flags**: Indicators of circuit state throughout the workflow

## Documentation

For detailed documentation, please see the [docs](docs) directory:

- [Concepts](docs/concepts/index.md): Core concepts and architecture
- [Workflow](docs/workflow/index.md): The five-step workflow
- [Examples](docs/examples/index.md): Implementation examples
- [API Reference](docs/api/index.md): Detailed API documentation

## When to Use CircuitCraft

CircuitCraft is particularly well-suited for:

- **Computational Economics**: Model dynamic economic systems with backward-solving 
  policies and forward-flowing simulations
- **Dynamic Programming**: Solve sequential decision problems with recursive 
  structures
- **Machine Learning Pipelines**: Create custom data processing workflows with 
  multiple transformations
- **Financial Modeling**: Design models with complex interdependencies and 
  bidirectional calculations

The library excels when your problem involves bidirectional data flow, custom 
transformation logic, and sequential dependencies.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 