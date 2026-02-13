# BACKLOG.md
## Green-AI: Active Sprint Backlog

**Status**: 🟢 PASSING (Pending Audits) | **Next Milestone**: v0.6.1-RULES
**Current Version**: v0.6.0 (All Tests Passing)
**Next Phase**: Bug Fixes → Phase 2 Sprint 2  

---

## 🐛 P0 - CRITICAL BUGS (FIX BEFORE ANY FEATURES)

**Status**: 🟢 0/257 Tests Failing
**Audit Date**: 2026-02-08
**Detailed Report**: See `bug_backlog.md` in artifacts

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

---

## 📋 Overview

This file tracks **PENDING engineering tasks**. Completed work has been moved to [release-notes.md](release-notes.md).

---

## 📦 PHASE 2: Carbon Efficiency, Rules, Quality & Scale 

### SPRINT 2: ADVANCED RULES & PERFORMANCE (High Priority)
2.1 **[ENGINE] AST Integration for JavaScript** [DONE]
   - Goal: Replace regex-based detectors with Tree-Sitter for higher precision.
   - Effort: 12h
   - Tag: [JULES]
2.3 **[RULES] Comprehensive Rule Gap Fill** [DONE]
   - Goal: Implement missing rules: Inefficient Dict lookups, Regex in loops, String Concatenation.
   - Effort: 6h
   - Tag: [JULES]

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
---

## 🥇 PRIORITIZED TASKS (Next Immediate Work)

1. **[JULES] Refactor export logic**
   - Goal: Deduplicate code in `api_export_csv` and `api_export_html`.
   - Priority: Low

## ✅ COMPLETED TASKS (Pending Release)
> Moved to release-notes.md

---

## 📅 VERSION HISTORY
- v0.6.0: Performance & New Rules (Current)
- v0.5.0-beta: Carbon Efficiency & Dynamic Rules
- v0.4.0: Multi-Project & UI Dashboard
- v0.3.0: Config System
