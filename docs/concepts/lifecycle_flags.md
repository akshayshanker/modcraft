# Lifecycle Flags in CircuitCraft

CircuitCraft 1.2.0 introduces a comprehensive set of lifecycle flags to track the 
state of a circuit throughout its workflow. These flags provide clear indicators of 
the circuit's readiness for each workflow step and help diagnose issues during 
development.

## Flag Overview

| Flag | Description |
|------|-------------|
| `has_empty_perches` | Indicates whether the circuit has perches with no data attributes |
| `has_model` | True when all movers have computational methods set |
| `movers_backward_exist` | True when the circuit has at least one backward mover |
| `is_portable` | True when the circuit is in a state that can be saved and loaded |
| `is_solvable` | True when the circuit is properly initialized for solving<br>(terminal perches have comp values and initial perches have sim values) |
| `is_solved` | True after the circuit has been successfully solved |
| `is_simulated` | True after the forward simulation has been completed |

## Lifecycle Phases

The lifecycle flags track the five phases of the CircuitCraft workflow:

### 1. Creation Phase
- Related flags: `has_empty_perches`, `movers_backward_exist`
- During this phase, the circuit-board structure is created with perches and movers
- The flags indicate whether the circuit has a valid structure

### 2. Model Finalization Phase
- Related flags: `has_model`
- During this phase, maps and comps are set on movers
- The flag indicates whether all necessary computational methods are set

### 3. Portability Phase
- Related flags: `is_portable`
- During this phase, the circuit is made portable for saving and loading
- The flag indicates whether the circuit can be serialized

### 4. Initialization Phase
- Related flags: `is_solvable`
- During this phase, initial values are set for perch data
- The flag indicates whether the circuit has sufficient data to be solved

### 5. Solution Phase
- Related flags: `is_solved`, `is_simulated`
- During this phase, movers are executed to compute results
- The flags indicate whether the circuit has been successfully solved

## Checking Lifecycle Flags

You can check lifecycle flags at any point during the workflow:

```python
# Check if the circuit is ready for solving
if circuit.is_solvable:
    print("Circuit is ready for solving")
else:
    print("Circuit needs more initialization")

# Check all lifecycle flags
print(f"has_empty_perches: {circuit.has_empty_perches}")
print(f"has_model: {circuit.has_model}")
print(f"movers_backward_exist: {circuit.movers_backward_exist}")
print(f"is_portable: {circuit.is_portable}")
print(f"is_solvable: {circuit.is_solvable}")
print(f"is_solved: {circuit.is_solved}")
print(f"is_simulated: {circuit.is_simulated}")
```

## Terminal and Initial Perches

The `is_solvable` flag requires proper initialization of terminal and initial perches. 
You can identify these perches using these methods:

```python
# Get terminal perches in the backward graph
terminal_perches = circuit.get_terminal_perches_backward()
print(f"Terminal perches in backward graph: {terminal_perches}")

# Get initial perches in the forward graph
initial_perches = circuit.get_initial_perches_forward()
print(f"Initial perches in forward graph: {initial_perches}")
```

## Common Lifecycle Issues

### Circuit Not Solvable
If `is_solvable` is False, check:
- Terminal perches in the backward graph have comp values
- Initial perches in the forward graph have sim values
- All required perches and movers are defined

### Model Not Finalized
If `has_model` is False, check:
- All movers have computational methods set
- Comp factory functions are properly defined
- Maps are correctly assigned to movers

### Solving Errors
If solving fails despite `is_solvable` being True, check:
- Computational methods handle all expected input types
- No runtime errors in computational methods
- Data types match between connected perches

Lifecycle flags provide a powerful debugging tool to ensure your circuit is properly 
configured and ready for each workflow phase. 