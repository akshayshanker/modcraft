# CircuitCraft API Reference

This section provides detailed documentation of CircuitCraft's classes, methods, and 
functions.

## Main Classes

- **[CircuitBoard](circuit_board.md)**: Main class representing a circuit-board with 
  perches and movers.
  
- **[Perch](perch.md)**: Class representing a perch (node) in the circuit-board.
  
- **[Mover](mover.md)**: Class representing a mover (edge) connecting perches in the 
  circuit-board.

## High-Level Functions

- **[create_and_solve_circuit](high_level_functions.md#create_and_solve_circuit)**: 
  Creates and solves a circuit in one step.

## Lifecycle Management

- **[Lifecycle Flags](lifecycle_management.md#lifecycle-flags)**: Methods for accessing 
  lifecycle flags.
  
- **[Terminal and Initial Perches](lifecycle_management.md#terminal-and-initial-perches)**: 
  Methods for identifying terminal and initial perches.
  
- **[Save and Load](lifecycle_management.md#save-and-load)**: Methods for saving and 
  loading circuits.

## API Examples

### CircuitBoard Class

```python
# Create a circuit-board
circuit = CircuitBoard(name="MyCircuit")

# Add a perch
circuit.add_perch(Perch("perch_name", {"comp": None, "sim": None}))

# Add a mover (connect perches with operations)
circuit.add_mover(
    source_name="source_perch", 
    target_name="target_perch",
    source_key="comp",           # Key to get from source perch
    target_key="comp",           # Key to update in target perch
    edge_type="backward"         # "backward" or "forward"
)

# Set computational method for a mover
circuit.set_mover_comp(
    source_name="source_perch",
    target_name="target_perch", 
    edge_type="backward",
    operation=my_operation_function
)

# Update perch data
circuit.set_perch_data("perch_name", {"comp": 5.0, "sim": 3.0})

# Finalize the model after all movers are set up
circuit.finalize_model()

# Solve the circuit (backward and forward passes)
circuit.solve()

# Check if circuit is solvable
is_solvable = circuit.is_solvable

# Get values after solving
result = circuit.get_perch_data("perch_name", "comp")
```

### Perch Class

```python
# Create a perch with data attributes
perch = Perch("perch_name", {"comp": None, "sim": None})

# Access perch data
comp_value = perch.data.get("comp")

# Update perch data
perch.update_data({"comp": 5.0})
```

### Mover Methods

```python
def my_operation(data):
    """
    A function that transforms perch data
    
    Args:
        data: A dictionary containing perch data attributes
              (e.g., {"comp": 5.0, "sim": 3.0})
              
    Returns:
        A dictionary with the keys and values to update in the target perch
    """
    comp = data.get("comp")
    if comp is not None:
        # Perform calculation using comp value
        result = comp * 2
        return {"comp": result}
    return {}  # Return empty dict if no updates
``` 