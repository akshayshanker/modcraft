# Changelog

All notable changes to CircuitCraft will be documented in this file.

## [1.0.0] - 2023-03-23

### Added
- Sequential circuit design: Each node can have at most one incoming and one outgoing edge in each direction
- Clear explanation of sequential structure in the README
- `__version__` attribute in the package
- This CHANGELOG file

### Changed
- Updated documentation to emphasize the sequential nature of circuits
- Enhanced README with clearer explanations of circuit constraints
- Renamed prompt document to reflect version 1.0.0

### Fixed
- Examples have been updated to ensure compatibility with the sequential constraint
- Fixed initialization issues in example files

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
