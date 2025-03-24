# Eulerian Circuits in CircuitCraft

In CircuitCraft, a circuit can be analyzed to determine if it forms an Eulerian cycle, which
provides insights into its computational structure and data flow patterns.

## What is an Eulerian Circuit?

An Eulerian circuit (or Eulerian cycle) is a path in a graph that traverses every edge
exactly once while starting and ending at the same vertex. For a directed graph to
contain an Eulerian circuit:

1. Every vertex must have equal in-degree and out-degree
2. The graph must be strongly connected (there is a path from each vertex to every other vertex)

## Eulerian Circuits in the Context of CircuitCraft

In CircuitCraft, we're particularly interested in a specific type of Eulerian circuit:
one that starts at a terminal perch, traverses through all backward movers to reach
initial perches, and then returns to the same terminal perch via forward movers.

This pattern is especially significant because:

1. It represents a complete computational cycle
2. It ensures that data can flow from terminal conditions backward to initial conditions and then forward again
3. It guarantees that the circuit is properly structured for both backward solving and forward simulation

## Graph Structure in CircuitCraft

CircuitCraft maintains two separate directed graphs:

1. **Backward Graph**: Stores all the backward movers (used for backward solving)
2. **Forward Graph**: Stores all the forward movers (used for forward simulation)

For Eulerian circuit analysis, these two graphs are combined into a single directed graph
that contains all perches and both types of movers. This combined graph is then analyzed
to determine if it forms an Eulerian circuit.

## Example Circuit Structure

Consider this simple circuit with three perches:

```
Terminal Perch (A) ← Intermediate Perch (B) ← Initial Perch (C)
       ↑                     ↑                      |
       |                     |                      |
       └─────────────────────┴──────────────────────┘
                        Forward Flow
```

In this circuit:
1. The backward path goes from A ← B ← C
2. The forward path goes from C → B → A
3. Together they form an Eulerian cycle

## Checking for Eulerian Circuits

CircuitCraft uses NetworkX's built-in graph analysis capabilities to check for Eulerian circuits:

```python
from circuitcraft import CircuitBoard, Perch

# Create circuit
circuit = CircuitBoard(name="TestCircuit")

# Add perches and movers
# ...

# Check if it forms an Eulerian circuit
if circuit.is_eulerian_circuit():
    print("The circuit forms an Eulerian cycle!")
else:
    print("The circuit does not form an Eulerian cycle.")
```

### How the Check Works

The Eulerian circuit check in CircuitCraft follows these steps:

1. Creates a combined graph with both backward and forward movers
2. Verifies that every perch has equal in-degree and out-degree (a necessary condition for Eulerian circuits)
3. Confirms that the graph is strongly connected using `nx.is_strongly_connected()`
4. For each terminal perch, checks if there exists a path that:
   - Starts at the terminal perch
   - Traverses through backward movers to reach an initial perch
   - Returns to the terminal perch via forward movers

## Why Eulerian Circuits Matter

Eulerian circuits are important in CircuitCraft for several reasons:

1. **Computational Completeness**: An Eulerian circuit ensures that the computation can be
   fully executed from terminal conditions back to terminal conditions.

2. **Data Flow Integrity**: It guarantees that data can flow through the entire circuit
   without getting stuck at any perch.

3. **Solution Verification**: If a circuit forms an Eulerian cycle, it suggests that the
   backward problem and forward problem are properly paired.

4. **Circuit Design Validation**: When designing economic models, an Eulerian circuit check
   helps validate that the model structure is complete and well-formed.

## Relationship to Economic Models

In economic modeling, an Eulerian circuit often represents a complete economic cycle:

1. The backward path represents the value function iteration or policy function computation
   (working backward from terminal conditions)

2. The forward path represents the simulation of economic agents following the computed
   policies (working forward from initial conditions)

When the circuit forms an Eulerian cycle, it confirms that the economic model is
structurally sound and can generate meaningful simulations based on optimal policies.

## Visualizing Eulerian Cycles

CircuitCraft provides a visualization function to help understand the circuit structure:

```python
# Visualize the Eulerian path in the circuit
fig = circuit.visualize_eulerian_path()
fig.savefig("eulerian_cycle.png")
```

This creates a diagram showing the perches and movers, with backward movers in blue,
forward movers in red, and the Eulerian path highlighted.

For detailed implementation, see the [CircuitBoard API documentation](../api/circuit_board.md). 