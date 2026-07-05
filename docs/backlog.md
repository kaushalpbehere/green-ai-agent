# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

## 1. Bugs & High Priority Analysis (P0 - Immediate)

| ID | Priority | Component | Issue | Status |
|---|---|---|---|---|
| ANALYSIS-001a | HIGH | Analysis | Define architecture for passing AST context to LLMs without exceeding token limits. | FIXED |
| ANALYSIS-001b | HIGH | Analysis | Evaluate LibCST vs raw string replacement for LLM-suggested code fixes. | FIXED |
| ANALYSIS-002a | HIGH | Analysis | Research OSV.dev and GSF API rate limits for dynamic standard syncing. | FIXED |
| ANALYSIS-002b | HIGH | Analysis | Design DB schema for caching external standard definitions locally. | FIXED |
| ANALYSIS-003a | HIGH | Analysis | Design YAML configuration hierarchy (Global > Org > User). | FIXED |
| ANALYSIS-004a | HIGH | Analysis | Determine performance impact of running 'git blame' on every violation during scan. | FIXED |
| IMPL-001 | HIGH | Backend | Database Schema: Create SQLAlchemy models for standard_sources and rules caching. | FIXED |
| IMPL-002 | HIGH | Backend | Alembic Migration: Generate migration script for new rule schema. | FIXED |
| IMPL-003 | HIGH | Backend | Git Blame: Add author, author_email, and commit_date to Violation domain model. | FIXED |
| IMPL-004 | HIGH | Backend | Git Blame: Update worker.py to attach pygit2 blame metadata to violations natively. | FIXED |
| IMPL-005 | HIGH | Backend | Configuration: Update config.py to merge Global, Org, Project, and Local rules hierarchies. | FIXED |
| IMPL-006 | HIGH | LLM | Context Limiting: Add token counting utility for AST snippets in remediation engine. | FIXED |
| IMPL-007 | HIGH | LLM | Fallback Remediation: Implement surgical byte-slice replacement fallback for non-Python nodes. | FIXED |
| IMPL-008 | HIGH | UI | Dashboard Filters: Implement Git author breakdown aggregation endpoint in app_fastapi.py. | FIXED |
| IMPL-009 | HIGH | External API | OSV Client: Create initial stub for downloading OSV.dev vulnerability databases. | FIXED |
| IMPL-010 | HIGH | External API | GSF Rules Client: Create initial stub for authenticating and fetching GSF GitHub rules. | FIXED |
| BUG-007 | HIGH | UI/Server | websockets.legacy deprecation in test output (Upstream uvicorn issue). | FIXED |
| BUG-017a | MEDIUM | Scanner | Ensure proper cleanup of temporary directories in multiprocessing mode. | FIXED |
| BUG-017b | MEDIUM | Scanner | Synchronize scan progress state across worker processes for accurate UI updates. | FIXED |
| BUG-021 | MEDIUM | CLI | CLI help text mismatch in `tests/test_cli_refactored.py`. | FIXED |
| BUG-022 | CRITICAL | Security | Update starlette to 1.0.1 to fix PYSEC-2026-161 (URL spoofing). | FIXED |
| BUG-023 | CRITICAL | Security | Update pytest to 9.0.3 to fix CVE-2025-71176 (DoS). | FIXED |
| BUG-024 | HIGH | Security | Fix Bandit B501 (verify=False) in src/standards/sync_engine.py. | FIXED |
| BUG-025 | HIGH | Security | Fix Bandit B701 (Jinja2 autoescape=False) in PDF/ESG exporters. | FIXED |
| BUG-026 | HIGH | Security | Fix Bandit B324 (MD5 hash) in src/core/detectors/cache.py. | FIXED |

## 2. Feature Completion (P1 - Stability & Parity)

| ID | Epic | Task | Status |
|---|---|---|---|
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

## 3. New Features (P2 - Expansion & Vision Alignment)

| ID | Epic | Task | Status |
|---|---|---|---|
| DASH-001 | UI | Dashboard: Redesign UI to SonarQube-style (Projects grid, Issues drill-down, Debt trends). | TODO |
| DASH-002 | UI | Git: Integrate `git blame` data to show authors in violation details. | TODO |
| DASH-003 | UI | Profiles: Implement "Scanning Profiles" (e.g., 'fast', 'thorough', 'security-only'). | TODO |
| DASH-004 | UI | Interactive: Allow disabling rules directly from the dashboard UI (writing back to config). | FIXED |
| SCA-001 | Security | SCA: Implement dependency graph parser for Python, Node, and Go. | FIXED |
| SCA-002 | Security | SCA: Integrate OSV.dev API for automated CVE lookups of dependencies. | FIXED |
| QUAL-001 | Quality | Metrics: Implement AST-based cyclomatic and cognitive complexity scoring. | FIXED |
| QUAL-002 | Quality | Metrics: Implement Type-1 and Type-2 code duplication detector. | TODO |
| QUAL-003 | Quality | Metrics: Integrate `Vulture` as a library for dead-code identification. | TODO |
| DEBT-001 | Governance | Debt: Define remediation effort (minutes) for every existing rule. | FIXED |
| DEBT-002 | Governance | Debt: Compute aggregate "cleanliness" and "remediation time" scores. | FIXED |
| ESG-001 | Governance | ESG: Define weighted aggregate score algorithm (40% E, 30% S, 30% G). | FIXED |
| RUST-001 | Rust | Lang: Integrate `tree-sitter-rust` and implement `RustASTDetector`. | TODO |

## 4. Technical Debt & Cleanup (P3)

| ID | Task | Status |
|---|---|---|
| ENG-018 | Code Cleanup: Final audit of scrubbed code paths in `src/core/detectors/python_detector.py`. | FIXED |
| ENG-019 | Security: Audit and standardize `Query(...)` validation across all 20+ FastAPI endpoints. | FIXED |
| ENG-020 | Documentation: Implement auto-sync check between `vision.md` and `architecture.md` (CI gate). | FIXED |

| ENG-021 | Code Cleanup: Removed JSONExporter and fixed flake8 errors | FIXED |

## 5. Completed Tasks (v1.0.4 Batch)

| ID | Task | Status |
|---|---|---|
| BASE-001 | Implement `green-ai baseline create` command. | FIXED |
| BASE-002 | Implement baseline comparison filtering in Scanner. | FIXED |
| BASE-003 | Implement `# green-ai: ignore next-line` support. | FIXED |
| BASE-004 | Implement `.green-ai/suppress.yaml` support. | FIXED |
| SBOM-001 | Implement CycloneDX 1.5 JSON generator. | FIXED |
| SBOM-002 | Implement SPDX 2.3 JSON generator. | FIXED |
| SBOM-003 | Implement `green-ai sbom` CLI command. | FIXED |
| SBOM-004 | Implement GSF Software Carbon Intensity (SCI) logic. | FIXED |
| SBOM-006 | Achieve 95%+ coverage on new SBOM/Baseline features. | FIXED |
| VER-001 | Version bump to v1.0.4 and doc consolidation. | FIXED |

---
> Tasks follow the SSOT vision defined in `/docs/vision.md`.

## 6. Vision Alignment & Deep Auditing (P2 - New Dashboard & Quality)

| ID | Epic | Task | Status |
|---|---|---|---|
| QUAL-004 | Quality | Deep Cleaning: Perform a comprehensive codebase audit to remove deprecated/unused legacy code. | TODO |
| QUAL-005 | Quality | UI Auditing: Conduct thorough accessibility and visual consistency audits across all dashboard views. | TODO |
| QUAL-006 | Quality | Code Review: Establish strict PR templates and automated code review workflows (Bug Hunter). | TODO |
| TEST-001 | Test | E2E Testing: Implement comprehensive end-to-end browser tests using Playwright. | TODO |
| TEST-002 | Test | Coverage: Increase overall unit test coverage strictly to >= 90%. | TODO |
