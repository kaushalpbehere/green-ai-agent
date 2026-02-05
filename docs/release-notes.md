# Release Notes

## [v0.5.0-beta] - 2026-01-29
### Added
- **Dynamic YAML Rule System**: Rules are now loaded from YAML files, enabling easier updates without code changes.
- **Advanced AST Detection**: Implemented sophisticated detection for redundant computations in loops (e.g., `len()`, `range()` in Python).
- **Standardized Logging**: Centralized logging system now records all tool operations to `output/logs/app.log`.

### Fixed
- **Scanner Performance**: Optimized file discovery to respect configuration ignore patterns (skipping `.venv`, `node_modules`, etc.).
- **Self-Scan Bottleneck**: Reduced self-scan execution time by ~85%.

---

## [v0.4.0] - 2026-01-28
### Added
- **Multi-Project Support**: Ability to register and scan multiple projects.
- **Export Capabilities**: Added CSV and HTML reporting formats.
- **Git Integration**: Direct scanning of repositories via Git URL.
- **Web Dashboard**: New UI for visualizing scan results across projects.

---

## [v0.3.0] - 2026-01-26
### Added
- **Configuration System**: Added `.green-ai.yaml` for custom scan settings.
- **Rule Customization**: Enable/disable specific rules via config or CLI.
- **Initial CLI**: Core `scan` command for Python and JavaScript.

---

## [v0.1.0] - 2026-01-20
### Added
- **Core Engine**: Initial AST-based scanner for basic Python and JavaScript violations.
- **Emissions Modeling**: Basic CO2 impact estimation based on static analysis.
