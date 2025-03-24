# CircuitCraft Workflow

This section provides a comprehensive guide to the CircuitCraft workflow.

## Workflow Steps

CircuitCraft follows a clear five-step workflow:

1. **[Circuit Creation](creation.md)**: Build the circuit-board structure with perches 
   and movers.
   
2. **[Model Finalization](finalization.md)**: Set up maps and comps on movers, and verify 
   the structure is valid.
   
3. **[Portability](portability.md)**: Ensure the circuit-board is portable, allowing it 
   to be saved and loaded.
   
4. **[Initialization](initialization.md)**: Provide initial values for perch data to 
   prepare the circuit for solving.
   
5. **[Solution](solution.md)**: Execute movers to compute results perch by perch.

Each phase is tracked with lifecycle flags that indicate the circuit's state and 
readiness to proceed to the next step.

## Complete Workflow Example

```python
# Complete workflow example
circuit = CircuitBoard(name="SimpleCircuit")

# 1. Circuit Creation - Create perches and circuit structure
circuit.add_perch(Perch("perch_0", {"comp": None, "sim": None}))
circuit.add_perch(Perch("perch_1", {"comp": None, "sim": None}))
circuit.add_mover(
    source_name="perch_1", 
    target_name="perch_0",
    source_key="comp", 
    target_key="comp",
    edge_type="backward"
)

# 2. Model Finalization - Assign maps and create comps
backward_map = {
    "operation": "square",
    "parameters": {"exponent": 2}
}
circuit.set_mover_map("perch_1", "perch_0", "backward", backward_map)

def comp_factory(data):
    """Create a comp function from a map"""
    map_data = data.get("map", {})
    operation = map_data.get("operation")
    
    if operation == "square":
        def backward_comp(data):
            """Square the input value (backward operation)"""
            comp = data.get("comp")
            if comp is not None:
                return {"comp": comp**2}
            return {}
        return backward_comp
    return lambda data: {}

circuit.create_comps_from_maps(comp_factory)
circuit.finalize_model()  # Sets has_model = True and is_portable = True

# 3. Portability is already handled by finalize_model()
print(f"Circuit is portable: {circuit.is_portable}")  # True

# 4. Initialization - Provide initial values
circuit.set_perch_data("perch_0", {"comp": 4.0})  # Terminal perch in backward graph

# Check if the circuit is solvable
print(f"Circuit is solvable: {circuit.is_solvable}")  # True

# 5. Solution - Execute movers
circuit.solve()  # Executes all movers
print(f"Circuit is solved: {circuit.is_solved}")  # True

# Access results
result = circuit.get_perch_data("perch_1", "comp")  # Should be 16
print(f"perch_1.comp = {result}")
``` 