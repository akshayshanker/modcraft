# Economic Motivation for CircuitCraft

CircuitCraft's structure is deeply aligned with economic modeling principles, 
particularly for solving recursive problems with heterogeneous agents.

## Sequential Structure with Directional Movers

- **Strictly sequential**: Each perch has at most one incoming and one outgoing mover 
  in each direction
- **Backward movers**: Computing policy functions through backward induction, where 
  each step depends on the next period's solution
- **Forward movers**: Applying policies to transform distributions forward through 
  time in a sequential chain
- This sequential structure naturally maps to time-indexed economic variables and 
  state transitions

## Functional Operators on Movers

- Operations live on movers rather than perches
- This separates data (perches) from transformations (movers)
- Mirrors mathematical operators in economic theory
- Allows for clear distinction between policy functions and distributions

## Circuit Lifecycle

- **Unsolved circuits**: Circuit structure exists but hasn't been fully solved
- **Solved circuits**: All computations have been completed
- Corresponds to the distinction between model specification and model solution
- Enables clear tracking of model state throughout the solution process

## Backward-Forward Workflow

- First solve backward for policies (like policy functions in economic models)
- Then solve forward for outcomes (like simulation in economic models)
- Natural alignment with how recursive economic problems are solved

## Mathematical Representation

For example, let $\mathbb{C}$ be the Coleman operator acting on a next period policy 
function $\sigma^{\text{nxt}}$ to yield a policy function $\sigma$

$$
\sigma = \mathbb{C}[\sigma^{\text{nxt}}], \qquad \sigma^{\text{nxt}} \in V, 
$$

where $V$ is some Polish space -- on the computer, $V$ is a space of "callables of 
some type". We refer to this as the 'backward operation'.

Starting with an instance of the object $\sigma^{\text{nxt}} \in V$, once 
we compute $\sigma^{\text{nxt}}$, we are not done. We may want to call on $\sigma$ 
and then $\sigma^{\text{nxt}}$ to simulate a model or push-forward a measure as 
follows:

$$
\mu_{1} = \mu_{0} \circ \sigma^{-1},
$$

and then 

$$
\mu_{2} = \mu_{1} \circ \sigma^{\text{nxt},-1}.
$$

For the push-forward operations, $\sigma$ and $\sigma^{\text{nxt}}$ are
equally "important" to be stored as nodes in a graph; for general equilibrium 
computations, the measures in turn also become important to be stored as nodes
in a graph.

Before we compute the problem, suppose we know $\sigma$ and $\mu_{0}$, and we 
know the operator $\mathbb{C}$ is well-defined. We then have a mathematical 
graph where the nodes are ${\mu_{2}}$, $\{\sigma^{\text{nxt}}, \mu_{1}\}$ and 
$\{\sigma, \mu_{0}\}$. The backward operation can be represented by an edge from 
$\sigma^{\text{nxt}}$ to $\sigma$ -- the idea here is to make the leap and say 
the edge is the pair ${\sigma^{\text{nxt}}, \mathbb{C}}$. Practically this means 
simply attaching property $\mathbb{C}$ to the edge from $\sigma^{\text{nxt}}$ to 
$\sigma$.

Even before we solve for $\sigma$, the graph above has a representation implicitly
as soon as we specify the initial policy function $\sigma^{\text{nxt}}$, the initial 
distribution $\mu_{0}$, and the operator $\mathbb{C}$. We can then attach
the computer representation of $\sigma^{\text{nxt}}$ to the node $\sigma^{\text{nxt}}$, 
the computer representation of the policies and distributions to their respective 
nodes once we solve or populate the graph.

## Circuit Representation

Given an initial values $\sigma$ and $\mu_{0}$, we can represent a circuit-board for 
the above problem as follows:

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

This circuit-board representation aligns perfectly with the structure of many economic 
models, particularly those involving dynamic programming and heterogeneous agent 
distributions. The circuitcraft library provides the computational framework to 
implement and solve such models efficiently. 