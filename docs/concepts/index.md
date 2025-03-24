# CircuitCraft Concepts

This section provides detailed explanations of CircuitCraft's core concepts.

## Core Concepts

- **[Circuit Architecture](circuit_architecture.md)**: Detailed explanation of the 
  CircuitCraft circuit-board structure, including the directed graph containing backward 
  and forward paths.
  
- **[Perches and Movers](perches_and_movers.md)**: Detailed documentation of perches 
  (nodes) and movers (edges) in CircuitCraft, including their attributes and behavior.
  
- **[Maps and Comps](maps_and_comps.md)**: Information about maps (mathematical 
  representations) and comps (computational implementations) in CircuitCraft.
  
- **[Lifecycle Flags](lifecycle_flags.md)**: Comprehensive guide to CircuitCraft's 
  lifecycle flags, which track the state of a circuit throughout its workflow.
  
- **[Economic Motivation](economic_motivation.md)**: Background on the economic and 
  mathematical theory behind CircuitCraft.

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
- **Scientific Computing**: Implement numerical methods with sequential dependencies
- **Sensitivity Analysis**: Create circuits where the effects of parameter changes 
  propagate through the system

The library excels when your problem involves:

1. **Bidirectional Data Flow**: Problems requiring both backward computation and 
   forward simulation
2. **Custom Transformation Logic**: Need for specialized operations between 
   components
3. **Sequential Dependencies**: Problems with clearly defined stages or time periods
4. **Reusable Components**: Scenarios where the same operations are applied at 
   multiple points

CircuitCraft's lifecycle management system makes it easy to track the state of your 
computation, ensuring that your circuit is properly initialized and ready for solving 
at each step of the workflow. 