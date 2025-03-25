# CircuitCraft

CircuitCraft is a graph-based framework for computing functional operations on arbitrary mathematical objects, with a circuit-based architecture that represents both the objects and their transformations. The main focus is on economic modeling, fixed point problems, and distributional analysis.
## Motivation

CircuitCraft addresses a key limitation in existing graph based computational frameworks: they focus on operations as nodes without coherently representing the mathematical objects being transformed. CircuitCraft treats mathematical objects as nodes (perches) and transformations as edges (movers).

This architecture is particularly valuable for problems where:

1. Graph data themselves are "first-class objects" with meaningful interrelationships
    - In economic models, data are objects like value functions, policy functions, distributions, etc.
2. Bidirectional computation is required (backward solving and forward simulation)
3. The connections between mathematical objects form a coherent mathematical model (an optimization problem or general equilibrium model)
4. Results from one operation serve as inputs to subsequent operation

## Operator context

Consider a standard dynamic programming problem where we compute a policy function σ using the Coleman operator 𝕮 on a next-period policy function σᴺᵉˣᵗ:

$$\sigma = \mathbb{C}[\sigma^{\text{next}}]$$

After solving for σ, economists typically need to simulate distributional effects:

$$\mu_{1} = \mu_{0} \circ \sigma^{-1}$$
$$\mu_{2} = \mu_{1} \circ (\sigma^{\text{next}})^{-1}$$

This creates a natural circuit structure that can be represented as follows:

```
                          ┌───────────────────┐
                          │  Node_0: {σ,μ₀}   │
                          └───────────────────┘
                               ↑     ↓
                               │     │
       backward solve          │     │      forward push 
        σ = C[σⁿˣᵗ]            │     │       μ₁ = μ₀ ∘ σ⁻¹
                               │     │
                               │     │
                               │     ▼
                          ┌───────────────────┐                     ┌───────────────┐
                          │ Node_1: {σⁿˣᵗ,μ₁} │────────────────────→│ Node_2: {,μ₂} │
                          └───────────────────┘                     └───────────────┘
                                                   forward push
                                                   μ₂ = μ₁ ∘ (σⁿˣᵗ)⁻¹
```

In CircuitCraft, this corresponds to a circuit with:
- Perches (nodes) storing either computational values (`up`) or simulation values (`down`)
- Movers (edges) representing transformations like the Coleman operator or distribution push-forward

## Core Architecture

CircuitCraft structures computational workflows as a circuit board with:

1. **Perches**: Store mathematical objects (functions, distributions, etc.)
   - `up`: Upstream computational value (e.g., policy function) - formerly 'comp'
   - `down`: Downstream simulation value (e.g., distribution) - formerly 'sim'

2. **Movers**: Transform values between perches
   - Backward movers: For fixed-point iteration, dynamic programming, etc.
   - Forward movers: For distributional analysis, simulation, etc.

3. **Circuit Board**: A unified structure combining two directed acyclic graphs (DAGs):
   - **Backward DAG**: Connects perches via backward movers, enabling policy iteration and value function computation
   - **Forward DAG**: Connects perches via forward movers, enabling distribution evolution and simulation
   - When combined, these DAGs form a complete circuit for solving and simulating economic models
   - The circuit tracks its state through lifecycle flags

## Circuit Structure

The dual DAG structure is fundamental to CircuitCraft's design:

1. **Backward DAG**: A directed acyclic graph where:
   - Edges represent functional operators (like the Coleman operator)
   - Information flows from "future" to "present" perches
   - Used to compute policy functions, value functions, and fixed points
   - Terminal perches provide boundary conditions for computation

2. **Forward DAG**: A directed acyclic graph where:
   - Edges represent distributional transforms (like push-forward operations)
   - Information flows from "present" to "future" perches 
   - Uses results from the backward solution to simulate distributions
   - Initial perches provide starting conditions for simulation

3. **Complete Circuit**: When backward and forward DAGs are combined, they form a complete circuit that:
   - Provides a consistent mathematical representation of the entire economic model
   - Ensures computational outputs from one phase become inputs to the next
   - Represents the economic model's full solution and simulation cycle
   - Allows both phases to be solved sequentially in a unified framework

This dual structure mirrors how economists think about economic problems: solve for policy functions first, then simulate distributional effects.

## Usage Workflow

CircuitCraft implements a five-step workflow:

1. **Circuit Creation**: Define perches and movers
2. **Model Finalization**: Complete the specification of all computational components
3. **Portability**: Ensure the circuit can be serialized if needed
4. **Initialization**: Set initial values for terminal perches
5. **Solution**: Execute the circuit to populate all perches

## Example

```python
from src.circuitcraft import CircuitBoard, Perch, create_and_solve_circuit

# Define computational methods
def backward_op(data):
    """Coleman operator for policy iteration"""
    if isinstance(data, dict):
        policy_next = data.get("up")
    else:
        policy_next = data
    
    if policy_next is not None:
        # Implement Coleman operator logic here
        return {"up": policy_function}
    return {}

def forward_op(data):
    """Push-forward for distribution"""
    if isinstance(data, dict):
        policy = data.get("up")
        distribution = data.get("down")
    else:
        return {}
    
    if policy is not None and distribution is not None:
        # Implement push-forward logic here
        return {"down": new_distribution}
    return {}

# Create and solve the circuit
circuit = create_and_solve_circuit(
    name="ModelCircuit",
    nodes=[
        {"id": "current", "data_types": {"up": None, "down": None}},
        {"id": "next", "data_types": {"up": None, "down": None}},
        {"id": "future", "data_types": {"up": None, "down": None}}
    ],
    edges=[
        # Backward: Policy iteration from next to current period
        {"source": "next", "target": "current", 
         "operation": backward_op, 
         "edge_type": "backward"},
        
        # Forward: Distribution from current to next period
        {"source": "current", "target": "next", 
         "operation": forward_op,
         "edge_type": "forward"},
         
        # Forward: Distribution from next to future period
        {"source": "next", "target": "future", 
         "operation": forward_op, 
         "edge_type": "forward"}
    ],
    initial_values={
        "current": {"down": initial_distribution},
        "next": {"up": initial_policy}
    }
)

# Access results
current_policy = circuit.get_perch_data("current", "up")
next_distribution = circuit.get_perch_data("next", "down")
future_distribution = circuit.get_perch_data("future", "down")
```

## Installation

```bash
pip install -e .
```

## Documentation

For more detailed documentation, see:
- [Concept Guide](docs/concepts/index.md): Core concepts and economic foundations
- [Workflow Guide](docs/workflow/index.md): Step-by-step usage instructions
- [Examples](docs/examples/index.md): Applied economic examples
- [API Reference](docs/api/index.md): Full API documentation

## Version

Current version: 1.3.1

## License

MIT 