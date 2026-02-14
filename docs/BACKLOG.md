# BACKLOG.md

## 📋 Next 10 Prioritized Microtasks

1. **[CORE] Refactor Project Model (BUG-004.1)**
   - Goal: Replace weak `Dict` types with strict Pydantic `ViolationDetails` model in `Project`.
   - Priority: High

2. **[UI] Calibration UI Integration (Sprint 3.2)**
   - Goal: Expose system calibration via Dashboard UI and API.
   - Priority: High

3. **[QA] Fix Pre-commit Hook**
   - Goal: Update `.git_hooks_pre-commit.sh` to allow required documentation files.
   - Priority: Medium

4. **[JULES] Fix BUG-003.1: Research Eventlet migration path**
   - Goal: Prepare for eventlet deprecation.
   - Priority: Medium

5. **[QA] Pre-commit Hooks Integration (Sprint 4.1)**
    - Goal: Auto-scan on commit via local hooks (improve DX/install script).
    - Priority: Medium

## ✅ Completed Tasks

- **[JULES] Refactor export logic** (Status: Done)
   - Goal: Deduplicate code in `api_export_csv` and `api_export_html`.
   - Priority: Low

- **[UI] Real-time Progress Bar (Sprint 3.1)** (Status: Done)
   - Goal: Integration of WebSockets for live status during scans.
   - Priority: High

- **[UI] Remediation Preview (Sprint 3.3)** (Status: Done)
   - Goal: Show suggested code diffs directly in the dashboard.
   - Priority: Medium

- **[JULES] Fix BUG-004.2: Add Pydantic models for validation** (Status: Done)
   - Goal: Ensure data integrity.
   - Priority: High

- **[JULES] Fix BUG-004.3: Create `ProjectDTO` for API responses** (Status: Done)
   - Goal: Standardize API outputs.
   - Priority: High

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
- **Sprint 3**: Real-time Dashboard & Metrics [IN PROGRESS]
- **Sprint 4**: Quality & CI [TODO]

### Phase 3: Cloud & Enterprise (Planned)
- Cloud deployment
- Team collaboration

---

## 📦 Release History
- **v0.6.1**: JavaScript AST Engine
- **v0.6.0**: Performance & New Rules
- **v0.5.0-beta**: Carbon Efficiency & Dynamic Rules
