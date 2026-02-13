# BACKLOG.md

## 📋 Next 10 Prioritized Microtasks

1. **[JULES] Refactor export logic**
   - Goal: Deduplicate code in `api_export_csv` and `api_export_html`.
   - Priority: Low

2. **[JULES] Fix BUG-004.1: Define clear interface contracts**
   - Goal: Address inconsistent project data model.
   - Priority: High

3. **[JULES] Fix BUG-004.2: Add Pydantic models for validation**
   - Goal: Ensure data integrity.
   - Priority: High

4. **[JULES] Fix BUG-004.3: Create `ProjectDTO` for API responses**
   - Goal: Standardize API outputs.
   - Priority: High

5. **[JULES] Fix BUG-003.1: Research Eventlet migration path**
   - Goal: Prepare for eventlet deprecation.
   - Priority: Medium

6. **[UI] Real-time Progress Bar (Sprint 3.1)**
   - Goal: Integration of WebSockets for live status during scans.
   - Priority: High

7. **[CORE] Calibration Scan (Sprint 3.2)**
   - Goal: System micro-benchmarks to normalize carbon impact modeling.
   - Priority: High

8. **[UI] Remediation Preview (Sprint 3.3)**
   - Goal: Show suggested code diffs directly in the dashboard.
   - Priority: Medium

9. **[QA] Pre-commit Hooks Integration (Sprint 4.1)**
    - Goal: Auto-scan on commit via local hooks.
    - Priority: Medium

## ✅ Completed Tasks

- **[JULES] Project Discovery & Doc Generation** (Status: Done)
   - Goal: specific `docs/vision.md` and `docs/development-standards.md`.
   - Priority: High (Initialization)

---

## 🐛 Known Issues (P0 - Critical)

### BUG-003: Eventlet Deprecation Warning
- **Impact**: Future compatibility risk, deprecated dependency
- **Fix**: Migrate to FastAPI or Quart
- **Effort**: 8h (Future Sprint)

### BUG-004: Inconsistent Project Data Model
- **Impact**: Confusion between dict and object representations
- **Fix**: Implement Repository + DTO pattern
- **Effort**: 6h

---

## 📅 Roadmap Overview

### Phase 2: Carbon Efficiency, Rules, Quality & Scale (In Progress)
- **Sprint 2**: Advanced Rules & Performance [DONE]
- **Sprint 3**: Real-time Dashboard & Metrics [TODO]
- **Sprint 4**: Quality & CI [TODO]

### Phase 3: Cloud & Enterprise (Planned)
- Cloud deployment
- Team collaboration

---

## 📦 Release History
- **v0.6.1**: JavaScript AST Engine
- **v0.6.0**: Performance & New Rules
- **v0.5.0-beta**: Carbon Efficiency & Dynamic Rules
