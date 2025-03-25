# Change Log

All notable changes to CircuitCraft will be documented in this file.

## [1.3.1] - 2023-03-25

### Changed
- Renamed `perch.comp` attribute to `perch.up` (upstream data)
- Renamed `perch.sim` attribute to `perch.down` (downstream data)
- Added backward compatibility properties to support older code using the previous attribute names
- Updated all examples and documentation to use the new attribute names

## [1.3.0] - 2023-03-24

### Added
- Robust type handling in all computational functions to support both dictionary and direct scalar inputs
- Improved error handling for circuit solving with informative messages
- Fixed import paths in examples to work with the new src directory structure

### Changed
- Restructured repository with src directory layout
- Updated API for separate backward and forward solvers (solve_backward() and solve_forward() methods)
- Improved example handling of terminal values for better circuit solvability
- Simplified file structure by consolidating similar examples

### Fixed
- Fixed import issues in all example files
- Resolved errors in computational functions that expected dictionary inputs but received scalar values
- Added appropriate error handling for circuits that cannot be fully solved
- Improved robustness of eulerian_example.py when moved to a different directory

## [1.2.4] - 2023-11-15

### Added
- Eulerian circuit checking functionality
- Default edge attribute usage for backward and forward movers
- Clearer terminal and initial perch terminology
- Warning when a circuit is not Eulerian

### Changed
- Updated solution approach to follow an Eulerian cycle model
- Enhanced add_mover method with default source/target key configurations
- Improved circuit initialization and solution process
- Updated documentation to reflect the Eulerian nature of combined sub-graphs
- Added graph structure sections to README

### Fixed
- Improved handling of terminal and initial perches in the solution process
- Clearer error messages for missing data in terminal or initial perches

## [1.2.1] - 2023-11-01

### Added
- Comprehensive documentation structure with dedicated `docs/` folder
- Detailed conceptual documentation for core components
- Workflow guides with step-by-step examples
- API reference documentation
- Economic motivation and theoretical background

### Changed
- Simplified main README.md with links to detailed documentation
- Improved code examples with clearer explanations
- Better organization of documentation by topic areas

## [1.2.0] - 2023-10-15

### Added
- New terminology: `Perch` (formerly Node), `Mover` (formerly Edge)
- New data attributes: `comp` (computational value) and `sim` (simulation value)
- Lifecycle flags to track circuit state (`has_empty_perches`, `has_model`, etc.)
- Support for terminal and initial perch identification
- Improved workflow with clear five-step process

### Changed
- Renamed `Node` to `Perch` throughout the codebase
- Renamed `function` attribute to `comp`
- Renamed `distribution` attribute to `sim`
- Renamed `Graph` to `CircuitBoard`
- Improved error messages with clearer guidance

### Fixed
- Various bugs in the graph traversal algorithm
- Issues with serialization of complex objects
- Problems with backward solving in certain graph configurations

## [1.1.0] - 2023-08-30

### Added
- Initial release with basic graph structure
- Support for backward and forward edges
- Basic solving capabilities
- Simple examples for mathematical operations

## Version 1.2.0 (2023-10-25)

### Major Changes
- Renamed `Node` to `Perch` for better terminology
- Renamed `function` attribute to `comp` in perches
- Renamed `distribution` attribute to `sim` in perches
- Renamed `Graph` to `CircuitBoard` for clearer representation
- Renamed `Edge` to `Mover` to better reflect functionality
- Added lifecycle flags to track circuit board state

### Added
- New lifecycle flags system to track circuit state:
  - `has_empty_perches`: True if the circuit has placeholder perches with no data
  - `has_model`: True if all needed perches and movers have been created and connected
  - `movers_backward_exist`: True if the graph contains at least one backward mover
  - `is_portable`: True if the circuit can be serialized (no embedded references)
  - `is_solvable`: True if the circuit has enough data to run the solve procedure
  - `is_solved`: True if the backward solution phase has been completed
  - `is_simulated`: True if the forward distribution pass has been completed
- Extended `Mover` class with additional attributes:
  - `parameters`: Generic, problem-specific values
  - `numerical_hyperparameters`: Tuning values for computational methods
- Added new methods for handling mover parameters and hyperparameters
- Added backward compatibility imports for previous version users

### Improvements
- Simplified circuit creation and solution workflow
- Improved portability checking with explicit flag
- Added better solvability checking based on perch data
- Clarified solving steps with backward_only and forward_only options
- Updated helper functions to use the new class names and flags
- Improved documentation and examples to match new terminology

## Version 1.1.0 (2023-10-10)

### Improvements
- Significantly improved edge handling in circuit creation helper functions
- Fixed issues with companion edge creation and configuration
- Enhanced source_keys and target_key validation and inheritance
- Modified circuit creation to ensure only explicitly defined edges have maps set
- Added better error handling for edge configuration issues
- Improved handling of cycles in graph during solving process
- Updated backward and forward circuit creation functions to match the central function
- Enhanced the execute_edge method to better handle different result dictionary structures
- Fixed issues where target key mismatches could cause incorrect data attribution

### Bug Fixes
- Fixed an issue where companion edges could have incompatible source_keys and target_key
- Resolved a problem with the setting of target values when result dictionary keys don't match target_key
- Fixed cycle detection and handling in both forward and backward solving methods

## Version 1.0.0 (2023-09-15)

### Major Features
- Initial stable release as CircuitCraft (evolution from GraphCraft)
- Function-based design where operations are direct Python functions
- Sequential circuit design with at most one incoming and one outgoing edge per node in each direction
- Clear workflow: Circuit Creation → Configuration → Initialization → Solution
- Consistent terminology and package reorganization
- Comprehensive documentation with economic modeling examples
- Helper functions for common circuit creation and solving patterns

## [0.2.0] - 2023-03-15

### Added
- Function-based operations approach
- Individual edge execution capability
- High-level convenience functions
- Examples directory with multiple usage patterns
- Documentation with economic modeling examples

### Changed
- Renamed from GraphCraft/modcraft to CircuitCraft/circuitcraft
- Shifted from class-based to function-based design
- Focused terminology on economic modeling concepts
- Streamlined API for adding edges with functions

### Deprecated
- Class-based Component and Operation classes (marked as deprecated)

## [0.1.0] - 2023-02-28

### Added
- Initial release of GraphCraft (as modcraft)
- Basic computational graph functionality
- Class-based design with Component and Operation classes
- Directed graph with backward and forward operations
- Basic example demonstrating workflow
