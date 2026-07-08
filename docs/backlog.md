# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

## 1. Environmental (E)
| ID | Priority | Task | Status |
|---|---|---|---|
| DASH-001 | P2 | Dashboard: Redesign UI to SonarQube-style (Projects grid, Issues drill-down, Debt trends). | TODO |
| DASH-003 | P2 | Profiles: Implement "Scanning Profiles" (e.g., 'fast', 'thorough', 'security-only'). | TODO |

## 2. Security (S)
| ID | Priority | Task | Status |
|---|---|---|---|
| SEC-002 | P0 | Audit: Address Bandit B404/B603 (subprocess execution risk) in `data_collector.py`, `scaphandre_integration.py`, and `benchmark.py`. | TODO |
| SEC-003 | P0 | Audit: Address Bandit B607/B603 (partial path subprocess execution risk) in `git_operations.py`. | TODO |
| SEC-005 | P0 | Audit: Address Bandit B404/B603 in `src/agents/runtime_monitor/data_collector.py`. | TODO |
| SEC-006 | P0 | Audit: Address Bandit B404/B603 in `src/agents/runtime_monitor/scaphandre_integration.py`. | TODO |
| SEC-007 | P0 | Audit: Address Bandit B404/B603 in `src/benchmarks/benchmark.py`. | TODO |
| SEC-008 | P0 | Audit: Address Bandit B404/B607/B603 in `src/core/git_operations.py`. | TODO |
| SEC-009 | P0 | Audit: Address Bandit B102 in `src/agents/runtime_monitor/data_collector.py`. | TODO |

## 3. Governance (G)
| ID | Priority | Task | Status |
|---|---|---|---|
| QUAL-003 | P2 | Metrics: Integrate `Vulture` as a library for dead-code identification. | TODO |
| QUAL-005 | P2 | UI Auditing: Conduct thorough accessibility and visual consistency audits across all dashboard views. | TODO |
| QUAL-006 | P2 | Code Review: Establish strict PR templates and automated code review workflows (Bug Hunter). | TODO |
| DASH-002 | P2 | Git: Integrate `git blame` data to show authors in violation details. | TODO |
| RUST-001 | P2 | Lang: Integrate `tree-sitter-rust` and implement `RustASTDetector`. | TODO |
| TEST-001 | P2 | E2E Testing: Implement comprehensive end-to-end browser tests using Playwright. | TODO |

## 4. Completed / Release Log
| ID | Component | Task | Status |
|---|---|---|---|
| ANALYSIS-001a | Analysis | Define architecture for passing AST context to LLMs without exceeding token limits. | FIXED |
| ANALYSIS-001b | Analysis | Evaluate LibCST vs raw string replacement for LLM-suggested code fixes. | FIXED |
| ANALYSIS-002a | Analysis | Research OSV.dev and GSF API rate limits for dynamic standard syncing. | FIXED |
| ANALYSIS-002b | Analysis | Design DB schema for caching external standard definitions locally. | FIXED |
| ANALYSIS-003a | Analysis | Design YAML configuration hierarchy (Global > Org > User). | FIXED |
| ANALYSIS-004a | Analysis | Determine performance impact of running 'git blame' on every violation during scan. | FIXED |
| IMPL-001 | Backend | Database Schema: Create SQLAlchemy models for standard_sources and rules caching. | FIXED |
| IMPL-002 | Backend | Alembic Migration: Generate migration script for new rule schema. | FIXED |
| IMPL-003 | Backend | Git Blame: Add author, author_email, and commit_date to Violation domain model. | FIXED |
| IMPL-004 | Backend | Git Blame: Update worker.py to attach pygit2 blame metadata to violations natively. | FIXED |
| IMPL-005 | Backend | Configuration: Update config.py to merge Global, Org, Project, and Local rules hierarchies. | FIXED |
| IMPL-006 | LLM | Context Limiting: Add token counting utility for AST snippets in remediation engine. | FIXED |
| IMPL-007 | LLM | Fallback Remediation: Implement surgical byte-slice replacement fallback for non-Python nodes. | FIXED |
| IMPL-008 | UI | Dashboard Filters: Implement Git author breakdown aggregation endpoint in app_fastapi.py. | FIXED |
| IMPL-009 | External API | OSV Client: Create initial stub for downloading OSV.dev vulnerability databases. | FIXED |
| IMPL-010 | External API | GSF Rules Client: Create initial stub for authenticating and fetching GSF GitHub rules. | FIXED |
| BUG-007 | UI/Server | websockets.legacy deprecation in test output (Upstream uvicorn issue). | FIXED |
| BUG-017a | Scanner | Ensure proper cleanup of temporary directories in multiprocessing mode. | FIXED |
| BUG-017b | Scanner | Synchronize scan progress state across worker processes for accurate UI updates. | FIXED |
| BUG-021 | CLI | CLI help text mismatch in `tests/test_cli_refactored.py`. | FIXED |
| BUG-022 | Security | Update starlette to 1.0.1 to fix PYSEC-2026-161 (URL spoofing). | FIXED |
| BUG-023 | Security | Update pytest to 9.0.3 to fix CVE-2025-71176 (DoS). | FIXED |
| BUG-024 | Security | Fix Bandit B501 (verify=False) in src/standards/sync_engine.py. | FIXED |
| BUG-025 | Security | Fix Bandit B701 (Jinja2 autoescape=False) in PDF/ESG exporters. | FIXED |
| BUG-026 | Security | Fix Bandit B324 (MD5 hash) in src/core/detectors/cache.py. | FIXED |
| IDE-001a | IDE | VS Code extension: Initialize scaffold with `yo code` and configure extension manifests. | FIXED |
| IDE-001b | IDE | VS Code extension: Implement settings provider for `.green-ai.yaml` editing. | FIXED |
| IDE-002a | IDE | LSP: Implement base server handshake and workspace synchronization. | FIXED |
| IDE-002b | IDE | LSP: Port Python/JS AST detectors to run in-process for LSP diagnostics. | FIXED |
| AUDIT-003 | Audit | Security: Create automated XSS payload tests for all dashboard fields. | FIXED |
| AUDIT-005 | Audit | Security: Implement unit tests for path traversal in `/api/remediation/preview`. | FIXED |
| TEAM-001a | Team | Database: Setup SQLAlchemy Core and migration environment (Alembic). | FIXED |
| TEAM-001b | Team | Database: Implement User, Project, and Team relational models. | FIXED |
| TEAM-002 | Team | API: Create REST endpoints for team creation and membership management. | FIXED |
| SEC-001 | Security | SAST: Port 40+ remaining OWASP Top 10 rules to YAML engine. | FIXED |
| SBOM-005 | SBOM | Report: Generate ESG compliance summary PDF (E: SCI, S: Secrets, G: Debt). | FIXED |
| DASH-004 | UI | Interactive: Allow disabling rules directly from the dashboard UI (writing back to config). | FIXED |
| SCA-001 | Security | SCA: Implement dependency graph parser for Python, Node, and Go. | FIXED |
| SCA-002 | Security | SCA: Integrate OSV.dev API for automated CVE lookups of dependencies. | FIXED |
| QUAL-001 | Quality | Metrics: Implement AST-based cyclomatic and cognitive complexity scoring. | FIXED |
| QUAL-002 | Quality | Metrics: Implement Type-1 and Type-2 code duplication detector. | FIXED |
| DEBT-001 | Governance | Debt: Define remediation effort (minutes) for every existing rule. | FIXED |
| DEBT-002 | Governance | Debt: Compute aggregate "cleanliness" and "remediation time" scores. | FIXED |
| ESG-001 | Governance | ESG: Define weighted aggregate score algorithm (40% E, 30% S, 30% G). | FIXED |
| ENG-018 | Code Cleanup | Final audit of scrubbed code paths in `src/core/detectors/python_detector.py`. | FIXED |
| ENG-019 | Security | Audit and standardize `Query(...)` validation across all 20+ FastAPI endpoints. | FIXED |
| ENG-020 | Documentation | Implement auto-sync check between `vision.md` and `architecture.md` (CI gate). | FIXED |
| ENG-021 | Code Cleanup | Removed JSONExporter and fixed flake8 errors | FIXED |
| BASE-001 | CLI | Implement `green-ai baseline create` command. | FIXED |
| BASE-002 | Scanner | Implement baseline comparison filtering in Scanner. | FIXED |
| BASE-003 | Scanner | Implement `# green-ai: ignore next-line` support. | FIXED |
| BASE-004 | Scanner | Implement `.green-ai/suppress.yaml` support. | FIXED |
| SBOM-001 | SBOM | Implement CycloneDX 1.5 JSON generator. | FIXED |
| SBOM-002 | SBOM | Implement SPDX 2.3 JSON generator. | FIXED |
| SBOM-003 | CLI | Implement `green-ai sbom` CLI command. | FIXED |
| SBOM-004 | SBOM | Implement GSF Software Carbon Intensity (SCI) logic. | FIXED |
| SBOM-006 | Quality | Achieve 95%+ coverage on new SBOM/Baseline features. | FIXED |
| VER-001 | Core | Version bump to v1.0.4 and doc consolidation. | FIXED |
| QUAL-004 | Quality | Deep Cleaning: Perform a comprehensive codebase audit to remove deprecated/unused legacy code. | FIXED |
| QUAL-007 | Security | Fix Bandit B324 in metrics.py | FIXED |
| TEST-002 | Test | Coverage: Increase overall unit test coverage strictly to >= 90%. | FIXED |
| SEC-004 | Security | Audit: Address Bandit B405 (defusedxml substitution) in `xml_exporter.py`. | FIXED |
| QUAL-008 | Quality | Code Quality: Remove silent `try...except...pass` (B110) blocks in `config.py`, `domain.py`, `export/__init__.py`, `worker.py`, and `lsp/server.py`. | FIXED |
