# CircuitCraft Examples

This directory contains example scripts that demonstrate various features and usage patterns of the CircuitCraft framework.

## Running the Examples

You can run the examples in several ways:

### 1. From the examples directory

You can run the examples directly from the examples directory:

```bash
cd examples
python3 quick_workflow.py
python3 math_circuit.py
python3 workflow_steps.py
```

### 2. From the project root directory

You can also run the examples from the project root directory by specifying the full path:

```bash
cd /path/to/modcraft
python3 examples/quick_workflow.py
python3 examples/math_circuit.py
python3 examples/workflow_steps.py
```

### 3. Install the package in development mode

For a more permanent solution, install the package in development mode:

```bash
cd /path/to/modcraft
python3 -m pip install -e .
```

After installing, you can run the examples from any directory.

## Examples Overview

### 1. `quick_workflow.py`

Demonstrates the high-level API to create and solve a circuit in one function call, following the 4-step workflow:
1. Circuit Creation
2. Configuration
3. Initialization
4. Solution

Uses simple mathematical operations (square and add_ten) to create a basic computational circuit.

### 2. `workflow_steps.py`

Shows the detailed step-by-step approach to the 4-step workflow:
1. Circuit Creation - Creating the graph structure with nodes and edges
2. Configuration - Assigning operations to edges
3. Initialization - Setting initial values
4. Solution - Executing operations to compute results

This example provides more insight into the internal workings of CircuitCraft.

### 3. `math_circuit.py`

Demonstrates a more complex circuit with matrix and vector operations:
- Backward operations that square vectors
- Forward operations that transform matrices using vector outer products

This example shows how CircuitCraft can be used for more sophisticated mathematical operations.

### 4. `quick_circuit.py`

Shows how to use the high-level API to create and solve a circuit in one step, similar to `quick_workflow.py` but with more complex matrix operations.

### 5. `math_graph.py`

Demonstrates a mathematical graph with matrix operations, showing how to create a computational graph with multiple operations.

### 6. `individual_edges.py`

Shows how to execute individual edge operations in a circuit for fine-grained control.

### 7. `separate_solvers.py`

Demonstrates how to use separate solvers for backward and forward operations, which is useful for economic modeling.

## Troubleshooting

If you encounter import errors when running the examples, it's likely due to Python not being able to find the `circuitcraft` package. You have a few options:

1. Run the examples from the project root directory
2. Install the package in development mode (`python3 -m pip install -e .`)
3. Add the project root to your PYTHONPATH environment variable

The examples include proper import handling to assist with the most common scenarios. 