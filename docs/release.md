# Release Notes

## v1.0.4 - Current
- Completed SBOM-005: Generate ESG compliance summary PDF (E: SCI, S: Secrets, G: Debt) and achieved 100% test coverage for ESGExporter.
- Completed SCA-001: Implement dependency graph parser for Python, Node, and Go.
- Completed SCA-002: Integrate OSV.dev API for automated CVE lookups of dependencies.
- Completed DASH-004: Interactive UI button to disable rules directly from the dashboard, writing back to the config.

## v1.0.5 - CI Integration & Cleanup
- Completed TEST-002: Reached >95% overall unit test coverage by adding missing CI component tests (`CIReporter`, `GitHubClient`, CLI `ci` commands).
- Completed QUAL-004: Cleaned up unused variables and deprecated code (e.g., `PDFExporter`, unused `ScanResultSchema`).
- Completed QUAL-007: Fixed Bandit B324 (MD5 hash) in src/core/quality/metrics.py by adding `usedforsecurity=False`.
- Completed SEC-004: Resolved Bandit B405 by adding nosec comment and importing defusedxml where applicable for xml_exporter.
- Completed QUAL-008: Removed silent try...except...pass blocks across the codebase and replaced with explicit logging.

- Completed SEC-002: Audit: Address Bandit B404/B603 (subprocess execution risk) in `data_collector.py`, `scaphandre_integration.py`, and `benchmark.py`.
- Completed SEC-003: Audit: Address Bandit B607/B603 (partial path subprocess execution risk) in `git_operations.py`.
- Completed SEC-005: Audit: Address Bandit B404/B603 in `src/agents/runtime_monitor/data_collector.py`.
- Completed SEC-006: Audit: Address Bandit B404/B603 in `src/agents/runtime_monitor/scaphandre_integration.py`.
- Completed SEC-007: Audit: Address Bandit B404/B603 in `src/benchmarks/benchmark.py`.
- Completed SEC-008: Audit: Address Bandit B404/B607/B603 in `src/core/git_operations.py`.
- Completed SEC-009: Audit: Address Bandit B102 in `src/agents/runtime_monitor/data_collector.py`.
