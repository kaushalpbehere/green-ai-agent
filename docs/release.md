# Release Notes

## v1.0.4 - Current
- Completed SBOM-005: Generate ESG compliance summary PDF (E: SCI, S: Secrets, G: Debt) and achieved 100% test coverage for ESGExporter.
- Completed SCA-001: Implement dependency graph parser for Python, Node, and Go.
- Completed SCA-002: Integrate OSV.dev API for automated CVE lookups of dependencies.
- Completed DASH-004: Interactive UI button to disable rules directly from the dashboard, writing back to the config.

## v1.0.5 - CI Integration & Cleanup
- Completed TEST-002: Reached >95% overall unit test coverage by adding missing CI component tests (`CIReporter`, `GitHubClient`, CLI `ci` commands).
- Completed QUAL-004: Cleaned up unused variables and deprecated code (e.g., `PDFExporter`, unused `ScanResultSchema`).
