# Circuit Architecture in CircuitCraft

CircuitCraft is built around the concept of a circuit-board, which is a directed graph 
containing two directed acyclic subgraphs (backward and forward). This document 
explains the architecture of CircuitCraft circuits.

## Circuit-Board Structure

A circuit-board in CircuitCraft has the following characteristics:

1. **Directed Graph**: The circuit-board is represented as a directed graph with perches 
   (nodes) and movers (edges).
   
2. **Dual Subgraphs**: The circuit-board contains two directed acyclic subgraphs:
   - **Backward subgraph**: Used for solving policy functions through backward induction
   - **Forward subgraph**: Used for simulating outcomes through forward flow
   
3. **Sequential Constraint**: Each perch can have at most one incoming and one outgoing 
   mover in each direction. This means both the backward and forward paths form simple 
   chains rather than complex networks.
   
4. **Eulerian Circuit**: The complete circuit-board forms an Eulerian circuit when both 
   subgraphs are considered together.

## Perches and Data

Each perch in a circuit-board contains various data attributes:

1. **Comp Attribute**: Used primarily in backward solving
   - Typically stores policy functions, value functions, or other computational results
   - Updated by backward movers during solving
   
2. **Sim Attribute**: Used primarily in forward simulation
   - Typically stores distributions, simulated values, or other results
   - Updated by forward movers during simulation
   
3. **Additional Attributes**: Perches can store other attributes as needed for 
   specific applications

## Movers and Operations

Movers connect perches and perform operations on their data:

1. **Backward Movers**: 
   - Connect from later periods to earlier periods
   - Typically compute policy functions from future values
   - Update the comp attribute of the target perch
   
2. **Forward Movers**:
   - Connect from earlier periods to later periods
   - Typically apply policy functions to transform distributions
   - Update the sim attribute of the target perch
   
3. **Computational Methods**:
   - Each mover contains a computational method (comp)
   - Comps are callable objects that transform data from source to target
   - Created from maps, which are mathematical representations of operators

## Circuit Diagram

A typical circuit-board might look like this:

```
                          ┌───────────────────┐
                          │  Perch_0: {σ,μ₀}  │
                          └───────────────────┘
                               ↑     ↓
                               │     │
       backward solve          │     │      forward push 
        σ = C[σⁿˣᵗ]            │     │       μ₁ = μ₀ ∘ σ⁻¹
                               │     │
                               │     │
                               │     ▼
                          ┌───────────────────┐                     ┌───────────────┐
                          │ Perch_1: {σⁿˣᵗ,μ₁} │────────────────────→│ Perch_2: {,μ₂} │
                          └───────────────────┘                     └───────────────┘
                                                   forward push
                                                   μ₂ = μ₁ ∘ (σⁿˣᵗ)⁻¹
```

In this diagram:
- Perch_0 contains policy function σ and distribution μ₀
- Perch_1 contains next-period policy function σⁿˣᵗ and distribution μ₁
- Perch_2 contains distribution μ₂
- The backward mover computes σ from σⁿˣᵗ using operator C
- The forward movers push distributions forward using policy functions

## Terminal and Initial Perches

A key concept in CircuitCraft is the identification of special perches:

1. **Terminal Perches in Backward Graph**:
   - Perches with no outgoing backward movers
   - Must have comp values set before solving
   - In the diagram above, Perch_0 is a terminal perch in the backward graph
   
2. **Initial Perches in Forward Graph**:
   - Perches with no incoming forward movers
   - Must have sim values set before solving
   - In the diagram above, Perch_0 is also an initial perch in the forward graph

These special perches must be properly initialized for a circuit to be solvable.

## Circuit Instantiation

A circuit-board can be instantiated with only a mathematical representation and 
partially populated perches. The steps are:

1. Create the circuit-board structure with perches and movers
2. Set maps on movers to define the mathematical representation
3. Create comps from maps to make the circuit portable
4. Initialize terminal and initial perches with appropriate values
5. Solve the circuit to compute all values

This architecture allows for flexible creation and solving of computational 
circuits across a wide range of applications. 