# BACKLOG.md
## Green-AI: Active Sprint Backlog

**Status**: 🔴 CRITICAL BUGS DETECTED | **Next Milestone**: v0.5.1-BUGFIX  
**Current Version**: v0.5.0-beta (19 Test Failures)  
**Next Phase**: Bug Fixes → Phase 2 Sprint 2  

---

## 🐛 P0 - CRITICAL BUGS (FIX BEFORE ANY FEATURES)

**Status**: 🔴 19/257 Tests Failing (7.4% failure rate)  
**Audit Date**: 2026-01-30  
**Detailed Report**: See `bug_backlog.md` in artifacts

### BUG-001: Type Mismatch - Tests vs Implementation [DONE]
- **Impact**: 14 test failures in `test_dashboard_projects.py`
- **Root Cause**: Tests mock `Project` as dicts, but `server.py` expects `Project` objects
- **Fix**: Create `ProjectFactory` fixture, update all mocks to use `Project` objects
- **Effort**: 4h
- **Assignee**: Developer
- **Subtasks**:
  - [x] BUG-001.1: Create `ProjectFactory` test fixture
  - [x] BUG-001.2: Update test mocks in `test_dashboard_projects.py`
  - [x] BUG-001.3: Add type hints to `server.py` API functions
  - [x] BUG-001.4: Create integration test for Project serialization
  - [x] BUG-001.5: Add pytest fixture for realistic test data

### BUG-002: Missing `calculate_average_grade` Function [DONE]
- **Impact**: Import error in tests, broken summary metrics
- **Root Cause**: Function named `get_average_grade` but tests import `calculate_average_grade`
- **Fix**: Rename function and move to utility module
- **Effort**: 2h
- **Subtasks**:
  - [x] BUG-002.1: Rename to `calculate_average_grade`
  - [x] BUG-002.2: Move to `src/utils/metrics.py`
  - [x] BUG-002.3: Add comprehensive unit tests
  - [x] BUG-002.4: Document algorithm in docstring

### BUG-003: Eventlet Deprecation Warning
- **Impact**: Future compatibility risk, deprecated dependency
- **Root Cause**: Eventlet is no longer maintained
- **Fix**: Migrate to FastAPI or Quart
- **Effort**: 8h (Future Sprint)
- **Subtasks**:
  - [ ] BUG-003.1: Research migration path
  - [ ] BUG-003.2: Evaluate alternatives (FastAPI, Quart)
  - [ ] BUG-003.3: Create migration plan
  - [ ] BUG-003.4: Implement feature flag
  - [ ] BUG-003.5: Update dependencies

### BUG-004: Inconsistent Project Data Model
- **Impact**: Confusion between dict and object representations
- **Root Cause**: Mixed use of dicts and objects throughout codebase
- **Fix**: Implement Repository + DTO pattern
- **Effort**: 6h
- **Subtasks**:
  - [ ] BUG-004.1: Define clear interface contracts
  - [ ] BUG-004.2: Add Pydantic models for validation
  - [ ] BUG-004.3: Create `ProjectDTO` for API responses
  - [ ] BUG-004.4: Implement adapter pattern
  - [ ] BUG-004.5: Add JSON schema validation

### BUG-005: Missing Violation Metadata in Project Class
- **Impact**: Cannot calculate violation counts from Project objects
- **Root Cause**: `Project` only stores count, not detailed violations
- **Fix**: Add `violations: List[Violation]` field
- **Effort**: 4h
- **Subtasks**:
  - [ ] BUG-005.1: Add violations field to Project
  - [ ] BUG-005.2: Create Violation dataclass
  - [ ] BUG-005.3: Update scan logic
  - [ ] BUG-005.4: Add property methods for counts
  - [ ] BUG-005.5: Data migration script

**Total Bug Fix Effort**: 24 hours  
**Acceptance Criteria**: 0 test failures, no deprecation warnings, 90%+ code coverage

### BUG-006: Test Failures - Rules and Standards
- **Impact**: Tests failing in `test_rules.py` and `test_standards.py`
- **Root Cause**: Tests expect `message` field in rules (missing), and `test_standards.py` uses strict default config
- **Fix**: Update tests to use `description` and dummy config
- **Effort**: 1h
- **Assignee**: Jules

### BUG-007: Missing Test Files
- **Impact**: Tests failing in `test_integration.py` and `test_scanner.py`
- **Root Cause**: `tests/simple_test.py` is missing
- **Fix**: Create `tests/simple_test.py` with sample code
- **Effort**: 0.5h
- **Assignee**: Jules

---

## 📋 Overview

This file tracks **PENDING engineering tasks**. Completed Phase 1 and Phase 2 Sprint 1 work has been moved to [release-notes.md](release-notes.md).

---

## 📦 PHASE 2: Carbon Efficiency, Rules, Quality & Scale 

### SPRINT 2: ADVANCED RULES & PERFORMANCE (High Priority)
2.1 **[ENGINE] AST Integration for JavaScript**
   - Goal: Replace regex-based detectors with Tree-Sitter for higher precision.
   - Effort: 12h
2.2 **[PERF] Multiprocessing Scanner**
   - Goal: Parallelize file analysis to handle large codebases.
   - Effort: 8h
2.3 **[RULES] Comprehensive Rule Gap Fill**
   - Goal: Implement 5+ missing rules: Deep Recursion, Inefficient Dict lookups, Regex in loops.
   - Effort: 6h

### SPRINT 3: REAL-TIME DASHBOARD & METRICS (High Priority)
3.1 **[UI] Real-time Progress Bar**
   - Goal: Integration of WebSockets for live status during scans.
   - Effort: 10h
3.2 **[CORE] Calibration Scan**
   - Goal: System micro-benchmarks to normalize carbon impact modeling.
   - Effort: 6h
3.3 **[UI] Remediation Preview**
   - Goal: Show suggested code diffs directly in the dashboard.
   - Effort: 8h

### SPRINT 4: QUALITY & CI (Medium Priority)
4.1 **[QA] Pre-commit Hooks Integration**
   - Goal: Auto-scan on commit via local hooks.
   - Effort: 4h
4.2 **[DOC] API Documentation**
   - Goal: Autogenerate documentation for core classes and registry.
   - Effort: 4h

---

## 🥇 PRIORITIZED TASKS (Next Immediate Work)

1. **JS AST Engine**: Begin migration from regex to parser-based detection.
2. **Scanner Concurrency**: Implement `ProcessPoolExecutor` in `Scanner.scan`.
3. **New Detection Rules**: Add `deep_recursion` and `inefficient_lookup` for Python.

---

## 📅 VERSION HISTORY
- v0.5.0-beta: Carbon Efficiency & Dynamic Rules (Current)
- v0.4.0: Multi-Project & UI Dashboard (Completed)
- v0.3.0: Config System (Completed)
