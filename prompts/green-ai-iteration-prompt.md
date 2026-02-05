# GREEN-AI AGENT - DEVELOPMENT ITERATION PROMPT

You are a coding agent working in the green-ai-agent repository at `green-ai-agent/`. Your goal is to complete EXACTLY ONE iteration: one microtask (smallest shippable slice) and stop, while keeping the codebase green, tested, and optimized.

---

## 📚 CANONICAL SOURCES

**Requirements (canonical)**: `docs/BACKLOG.md`  
**Bug Tracking (canonical)**: `.gemini/antigravity/brain/*/bug_backlog.md`  
**UI Testing (canonical)**: `.gemini/antigravity/brain/*/ui_testing_report.md`  
**Work History (canonical)**: `.gemini/antigravity/brain/*/walkthrough.md`  
**Development Standards (canonical)**: `docs/development-standards.md` (if exists)  
**Testing Standards (canonical)**: `pytest.ini`, `tests/conftest.py`  
**Code Quality Standards (canonical)**: `.gitignore`, `requirements.txt`

---

## 🚫 NON-NEGOTIABLE INVARIANTS

### Code Quality
1. **Always Green**: Do not leave tests failing. All 257 tests must pass before completing iteration.
2. **Test Coverage**: Maintain ≥90% code coverage for modified modules.
3. **No Deprecation Warnings**: Fix or suppress all deprecation warnings.
4. **Type Safety**: Add type hints to all new functions and classes.
5. **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.

### Codebase Hygiene
6. **Delete Dead Code**: Remove unused files, functions, and imports.
7. **No Duplicate Code**: Extract common logic into utilities.
8. **Consistent Naming**: Use snake_case for functions/variables, PascalCase for classes.
9. **File Size Limit**: Keep files under 500 lines. Split larger files into modules.
10. **Dependency Management**: Use exact versions in `requirements.txt` (no ^ or ~).

### Testing Standards
11. **Test-First Development**: Write tests before implementation.
12. **Test Isolation**: Each test must be independent and idempotent.
13. **Test Naming**: Use descriptive names: `test_<function>_<scenario>_<expected_result>`
14. **Test Coverage**: Unit tests + Integration tests + Edge case tests for each feature.
15. **Mock External Dependencies**: Use `unittest.mock` or `pytest-mock` for external calls.

### Audit & Quality Assurance (NEW - CRITICAL)
16. **Pre-Implementation Audit**: Run full audit BEFORE starting any work to establish baseline.
17. **Post-Implementation Audit**: Run full audit AFTER completing work to detect regressions.
18. **Browser UI Testing**: Test ALL interactive elements (buttons, forms, modals) with browser automation.
19. **Regression Prevention**: Every bug fix MUST include regression test to prevent recurrence.
20. **Backlog Synchronization**: Update backlog IMMEDIATELY when bugs/tasks discovered during audit.

### Backlog Management (NEW - CRITICAL)
21. **Real-Time Updates**: Update `docs/BACKLOG.md` as soon as bugs/tasks are identified.
22. **Bug Prioritization**: All bugs must be categorized as P0 (Critical), P1 (High), P2 (Medium), P3 (Low).
23. **Task Granularity**: Break large tasks into microtasks (≤4 hours each).
24. **Status Tracking**: Use `[ ]` Todo, `[/]` In-Progress, `[x]` Complete, `[!]` Blocked.
25. **Audit Trail**: Document what was tested, what broke, what was fixed in backlog.

### Documentation
26. **Update Backlog**: Mark tasks as `[/]` in-progress, `[x]` complete in `docs/BACKLOG.md`.
27. **Docstrings**: All public functions/classes must have Google-style docstrings.
28. **No Ad-hoc Docs**: Only update existing docs in `docs/` folder.
29. **Changelog**: Update walkthrough.md with changes made.

### Git Workflow (Optional - Works Without Git)
30. **Local Development**: Can work entirely locally without git commits.
31. **Version Control**: If using git: Small commits with descriptive messages.
32. **Conventional Commits**: If using git: Use format: `type(scope): description`
33. **Single-Task Focus**: Do not start next microtask in same run.

---

## 📋 INPUTS YOU MUST PRODUCE BEFORE CODING

Before writing any code, you MUST identify and document:

1. **Selected Microtask**:
   - ID: `BUG-XXX` or `FEATURE-XXX`
   - Title: Brief description
   - Priority: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
   - Estimated Effort: Hours
   - Files to Touch: List of files to modify/create/delete

2. **Acceptance Criteria**:
   - List specific, testable conditions for completion
   - Define "Definition of Done"

3. **Verification Commands**:
   - **Fast**: `python -m pytest tests/test_specific.py -v`
   - **Gate**: `python -m pytest tests/ -v --cov=src --cov-report=term-missing`
   - **Lint**: `python -m flake8 src/ tests/` (if applicable)

4. **Rollback Plan**:
   - How to revert changes if something breaks
   - Which files to restore

---

## 🔄 ITERATION PROCEDURE (Execute in Order)

### 1. PRE-IMPLEMENTATION AUDIT (CRITICAL - NEW)

**Purpose**: Establish baseline quality metrics BEFORE making any changes.

**A. Run Full Test Suite**:
```bash
# Capture current test status
python -m pytest tests/ -v --tb=short > audit_pre_implementation.txt 2>&1

# Check for failures
python -m pytest tests/ -v --tb=no -q 2>&1 | Select-String -Pattern "passed|failed"
```

**B. Document Baseline**:
```
Pre-Implementation Audit Results:
- Total Tests: 257
- Passing: 241
- Failing: 16
- Coverage: 93.8%
- Warnings: 8 deprecation warnings
```

**C. Browser UI Testing** (if UI changes planned):
```bash
# Start server
python src/ui/server.py &

# Run browser tests (manual or automated)
# Test ALL buttons, forms, modals, navigation
# Document any existing UI bugs
```

**D. Update Backlog with Discovered Issues**:
```markdown
# docs/BACKLOG.md
## 🐛 BUGS DISCOVERED DURING AUDIT

- [ ] **BUG-AUDIT-001**: Delete button shows 403 error without user feedback (P1)
- [ ] **BUG-AUDIT-002**: Rescan button calls non-existent API endpoint (P0)
- [ ] **BUG-AUDIT-003**: 16 failing tests in test_dashboard_projects.py (P0)
```

**E. Create Audit Report Artifact**:
```markdown
# .gemini/antigravity/brain/*/audit_report_<timestamp>.md

## Pre-Implementation Audit
**Date**: 2026-01-30T11:20:00Z
**Task**: BUG-001.1

### Test Status
- 241/257 tests passing (93.8%)
- 16 failing tests (all in test_dashboard_projects.py)

### UI Status
- Landing page: 3 broken buttons identified
- Dashboard: All features functional
- Modals: All working correctly

### Code Quality
- 12 unused imports found
- 3 files >500 lines
- 2 duplicate code blocks

### Backlog Updates
- Added 3 new bugs to backlog
- Prioritized as P0/P1
```

---

### 2. SYNC & SELECT

**If Using Git**:
```bash
# Pull latest changes
git pull origin main
```

**If Working Locally** (No Git):
```bash
# Just review current state
ls -la
```

**Review Backlog**:
```bash
cat docs/BACKLOG.md
```

**Actions**:
- Select ONE next task from `docs/BACKLOG.md` (highest priority, `[ ]` Todo, unblocked)
- Confirm task has clear acceptance criteria
- If not ready, update backlog and STOP

**Output**:
```
Selected Task: BUG-001.1 - Create ProjectFactory test fixture
Priority: P0
Effort: 1h
Files: tests/conftest.py (NEW)
Baseline: 241/257 tests passing
```

---

### 3. MARK IN-PROGRESS & UPDATE BACKLOG

Update `docs/BACKLOG.md`:
```markdown
- [/] **BUG-001.1**: Create `ProjectFactory` test fixture
```

Create execution notes in walkthrough or task artifact:
```markdown
## BUG-001.1 - ProjectFactory Fixture
**Started**: 2026-01-30T11:13:00Z
**Scope**: Create reusable Project object factory for tests
**Verification**: pytest tests/test_dashboard_projects.py -v
```

---

### 3. ANALYZE CODEBASE (Compression & Cleanup)

Before implementing, analyze for optimization opportunities:

**A. Identify Dead Code**:
```bash
# Find unused imports
python -m vulture src/ --min-confidence 80

# Find duplicate code
python -m pylint src/ --disable=all --enable=duplicate-code
```

**B. Check File Sizes**:
```bash
# Find large files (>500 lines)
find src/ -name "*.py" -exec wc -l {} \; | sort -rn | head -10
```

**C. Analyze Dependencies**:
```bash
# Check for unused packages
pip install pipreqs
pipreqs src/ --force
diff requirements.txt src/requirements.txt
```

**D. Identify Refactoring Opportunities**:
- Functions >50 lines → Extract helper functions
- Classes >300 lines → Split into multiple classes
- Duplicate logic → Create utility module
- Magic numbers → Define constants

**Output**:
```
Compression Opportunities:
- landing.html: 897 lines → Split into components (600 lines saved)
- server.py: 690 lines → Extract services layer (200 lines saved)
- Unused imports: 12 found in src/core/
- Duplicate code: 3 blocks in tests/
```

---

### 4. TIGHT RED/GREEN LOOP

**A. Write Tests First** (TDD):
```python
# tests/test_conftest.py
def test_project_factory_creates_valid_project(project_factory):
    """Test that project_factory creates Project with all required fields."""
    project = project_factory(name="TestProject")
    
    assert isinstance(project, Project)
    assert project.name == "TestProject"
    assert project.repo_url is not None
    assert project.id is not None
```

**B. Run Tests (Expect Failure)**:
```bash
python -m pytest tests/test_conftest.py::test_project_factory_creates_valid_project -v
# Expected: FAILED (fixture not found)
```

**C. Implement Minimum Code**:
```python
# tests/conftest.py
import pytest
from src.core.project_manager import Project

@pytest.fixture
def project_factory():
    def _create_project(name="TestProject", **kwargs):
        return Project(name=name, repo_url="https://github.com/test/repo", **kwargs)
    return _create_project
```

**D. Run Tests (Expect Pass)**:
```bash
python -m pytest tests/test_conftest.py::test_project_factory_creates_valid_project -v
# Expected: PASSED
```

**E. Refactor** (if needed):
- Extract magic strings to constants
- Add type hints
- Improve naming
- Add docstrings

**F. Run Full Test Suite**:
```bash
python -m pytest tests/ -v
# Must: All tests pass
```

---

### 5. CODE CLEANUP & COMPRESSION

After implementing feature, clean up:

**A. Remove Dead Code**:
```python
# ❌ DELETE: Unused functions
def old_function_not_used():
    pass

# ❌ DELETE: Commented code
# def legacy_implementation():
#     pass

# ❌ DELETE: Unused imports
import sys  # Not used anywhere
```

**B. Extract Duplicates**:
```python
# ❌ BEFORE: Duplicate error handling
try:
    response = await fetch(...)
    if not response.ok: throw new Error(...)
except Exception as e:
    alert(f"Failed: {e.message}")

# ✅ AFTER: Utility function
async def api_call_with_error_handling(url, method='GET', **kwargs):
    """Reusable API call wrapper with error handling."""
    try:
        response = await fetch(url, method=method, **kwargs)
        if not response.ok:
            raise APIError(response.status, await response.json())
        return await response.json()
    except Exception as e:
        show_error_alert(f"API call failed: {e}")
        raise
```

**C. Split Large Files**:
```python
# ❌ BEFORE: server.py (690 lines)
# All API endpoints, business logic, utilities in one file

# ✅ AFTER: Modular structure
# src/ui/server.py (200 lines) - Flask app setup, routes
# src/ui/services.py (150 lines) - Business logic
# src/ui/dto.py (100 lines) - Data transfer objects
# src/ui/utils.py (80 lines) - Helper functions
```

**D. Verify Compression**:
```bash
# Count lines before/after
wc -l src/ui/server.py
# Before: 690 lines
# After: 200 lines (71% reduction)
```

---

### 6. COMPREHENSIVE TESTING

**A. Unit Tests** (Test individual functions):
```python
def test_project_factory_default_values(project_factory):
    """Test factory uses sensible defaults."""
    project = project_factory()
    assert project.name == "TestProject"
    assert project.branch == "main"
    assert project.is_system == False
```

**B. Integration Tests** (Test API endpoints):
```python
def test_api_projects_list_with_factory(client, project_factory):
    """Test /api/projects endpoint with Project objects."""
    projects = [project_factory(name=f"Project{i}") for i in range(3)]
    with patch.object(project_manager, 'list_projects', return_value=projects):
        response = client.get('/api/projects')
        assert response.status_code == 200
        assert len(response.json()['projects']) == 3
```

**C. Edge Case Tests**:
```python
def test_project_factory_with_special_characters(project_factory):
    """Test factory handles special characters in names."""
    project = project_factory(name="Test-Project_2024.v1")
    assert project.name == "Test-Project_2024.v1"

def test_project_factory_with_empty_name(project_factory):
    """Test factory rejects empty names."""
    with pytest.raises(ValueError):
        project_factory(name="")
```

**D. Regression Tests** (Prevent bug recurrence):
```python
def test_bug_001_project_objects_not_dicts(project_factory):
    """Regression test: Ensure Project objects used, not dicts."""
    project = project_factory()
    assert hasattr(project, 'id')  # Object attribute access
    assert not isinstance(project, dict)  # Not a dictionary
```

**E. Run Full Test Suite**:
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=90
```

**Expected Output**:
```
======================== 257 passed in 7.44s =========================
Coverage: 93% (target: 90%)
```

---

### 7. COMMIT DISCIPLINE

**A. Stage Changes**:
```bash
git add tests/conftest.py
git add tests/test_dashboard_projects.py
```

**B. Commit with Conventional Format**:
```bash
git commit -m "test(fixtures): add ProjectFactory for test data generation

- Created project_factory fixture in conftest.py
- Replaced dictionary mocks with Project objects
- Added comprehensive tests for factory
- Fixes BUG-001.1

BREAKING CHANGE: Tests now require Project objects, not dicts
"
```

**C. Verify Branch is Green**:
```bash
python -m pytest tests/ -v
# All tests must pass before pushing
```

---

### 9. BROWSER UI TESTING (CRITICAL - NEW)

**Purpose**: Verify NO UI regressions introduced by changes.

**A. Start Server**:
```bash
# Start UI server in background
python src/ui/server.py &
SERVER_PID=$!

# Wait for server to start
sleep 5
```

**B. Manual Browser Testing Checklist**:

Navigate to `http://127.0.0.1:5000` and test:

**Landing Page**:
- [ ] Page loads without errors
- [ ] "+ New Scan" button opens modal
- [ ] "+ Add Project" button opens modal
- [ ] "⚙️ Settings" button opens modal
- [ ] "🌙" theme toggle switches dark/light mode
- [ ] Recent Projects section displays correctly
- [ ] Project cards are clickable
- [ ] "🔄 Rescan" button works (check console for errors)
- [ ] "👁️ View" button navigates correctly
- [ ] "🗑️ Delete" button shows confirmation
- [ ] Delete button handles 403 errors gracefully (for system projects)

**Modals**:
- [ ] New Scan Modal: All fields functional
- [ ] New Scan Modal: Validation works
- [ ] New Scan Modal: Submit triggers API call
- [ ] New Scan Modal: Cancel closes modal
- [ ] Add Project Modal: All fields functional
- [ ] Settings Modal: All settings save correctly
- [ ] Click outside modal closes it
- [ ] X button closes modal

**Dashboard** (if exists):
- [ ] Dashboard loads
- [ ] All tabs switch correctly
- [ ] Charts render
- [ ] Project list displays
- [ ] Filters work
- [ ] Comparison features work

**C. Automated Browser Testing** (if browser automation available):
```python
# Use browser_subagent or similar tool
browser_subagent(
    task="Test all interactive elements on landing page",
    recording_name="ui_regression_test"
)
```

**D. API Testing**:
```bash
# Test critical API endpoints
curl -s http://127.0.0.1:5000/api/projects | jq .
curl -s http://127.0.0.1:5000/api/projects/green-ai-agent | jq .

# Check for errors
curl -s http://127.0.0.1:5000/ | grep -i "error\|undefined\|null"
```

**E. Console Error Check**:
```
Open Browser DevTools (F12)
Check Console tab for:
- JavaScript errors
- Failed API calls (404, 500)
- Deprecation warnings
- Missing resources
```

**F. Document UI Test Results**:
```markdown
## Browser UI Testing Results

### Tested Features
✅ Landing page loads
✅ All modals open/close
✅ Theme toggle works
✅ New Scan form validation
❌ Delete button: No user feedback for 403 errors (REGRESSION)
❌ Rescan button: 404 error on API call (EXISTING BUG)

### Console Errors
- 0 JavaScript errors
- 2 API errors (404 on /api/projects/{name}/rescan)
- 1 deprecation warning (Eventlet)

### Action Items
- Add to backlog: BUG-UI-REGRESSION-001 (Delete button feedback)
- Verify BUG-UI-002 still in backlog (Rescan endpoint)
```

**G. Update Backlog with UI Bugs**:
```markdown
# docs/BACKLOG.md

## 🐛 UI REGRESSIONS DISCOVERED

- [ ] **BUG-UI-REGRESSION-001**: Delete button no longer shows specific error for 403 (P1)
  - **Introduced by**: BUG-001.1 implementation
  - **Impact**: Poor UX for system project deletion
  - **Fix**: Add 403 error handling in deleteProject() function
```

**H. Stop Server**:
```bash
kill $SERVER_PID
```

---

### 10. POST-IMPLEMENTATION AUDIT (CRITICAL - NEW)

**Purpose**: Verify NO regressions introduced and quality improved.

**A. Run Full Test Suite**:
```bash
# Capture post-implementation test status
python -m pytest tests/ -v --tb=short > audit_post_implementation.txt 2>&1

# Check for failures
python -m pytest tests/ -v --tb=no -q 2>&1 | Select-String -Pattern "passed|failed"
```

**B. Compare with Baseline**:
```
Post-Implementation Audit Results:
- Total Tests: 257
- Passing: 257 (was 241) ✅ +16 FIXED
- Failing: 0 (was 16) ✅ ALL FIXED
- Coverage: 94% (was 93.8%) ✅ +0.2%
- Warnings: 8 (was 8) ⚠️ NO CHANGE
```

**C. Regression Check**:
```bash
# Compare test results
diff audit_pre_implementation.txt audit_post_implementation.txt

# Verify no NEW failures
# Verify no NEW warnings
# Verify coverage did not decrease
```

**D. Code Quality Metrics**:
```bash
# Count total lines
find src/ -name "*.py" -exec wc -l {} \; | awk '{sum+=$1} END {print sum " total lines"}'

# Before: 2,500 lines
# After: 2,440 lines (-60 lines) ✅ CODE COMPRESSED

# Find large files
find src/ -name "*.py" -exec wc -l {} \; | sort -rn | head -5

# Verify no files >500 lines
```

**E. Update Audit Report**:
```markdown
# .gemini/antigravity/brain/*/audit_report_<timestamp>.md

## Post-Implementation Audit
**Date**: 2026-01-30T12:00:00Z
**Task**: BUG-001.1

### Test Status
- ✅ 257/257 tests passing (100%) - IMPROVED from 93.8%
- ✅ 0 failing tests - FIXED 16 failures
- ✅ Coverage: 94% - IMPROVED from 93.8%

### UI Status
- ✅ Landing page: All features functional
- ⚠️ 1 UI regression discovered (BUG-UI-REGRESSION-001)
- ✅ Dashboard: All features functional
- ✅ Modals: All working correctly

### Code Quality
- ✅ Removed 12 unused imports
- ✅ Reduced codebase by 60 lines
- ✅ All files <500 lines
- ✅ No duplicate code

### Regressions Detected
- BUG-UI-REGRESSION-001: Delete button error handling (P1)
  - Added to backlog
  - Will fix in next iteration

### Backlog Updates
- Completed: BUG-001.1
- Added: 1 new UI regression bug
- Status: 257/257 tests passing
```

**F. Verify Backlog is Up-to-Date**:
```markdown
# docs/BACKLOG.md

## ✅ COMPLETED
- [x] **BUG-001.1**: Create `ProjectFactory` test fixture
  - All 257 tests passing
  - Coverage: 94%
  - Code compressed: -60 lines

## 🐛 NEW BUGS (Discovered During Audit)
- [ ] **BUG-UI-REGRESSION-001**: Delete button error handling (P1)

## 📊 METRICS
- Test Pass Rate: 100% (was 93.8%)
- Code Coverage: 94% (was 93.8%)
- Total Lines: 2,440 (was 2,500)
- Failing Tests: 0 (was 16)
```

---

### 11. DOCUMENTATION UPDATE

**A. Update Backlog**:
```markdown
# docs/BACKLOG.md
- [x] **BUG-001.1**: Create `ProjectFactory` test fixture ✅ COMPLETED
  - Created tests/conftest.py with project_factory
  - Added 5 comprehensive tests
  - All tests passing (257/257)
```

**B. Update Walkthrough**:
```markdown
# walkthrough.md
## BUG-001.1 - ProjectFactory Fixture ✅

**Completed**: 2026-01-30T12:00:00Z
**Duration**: 45 minutes

### Changes Made
- Created `tests/conftest.py` with `project_factory` fixture
- Replaced dictionary-based mocks in `test_dashboard_projects.py`
- Added 5 unit tests for factory validation

### Tests Added
- `test_project_factory_creates_valid_project`
- `test_project_factory_default_values`
- `test_project_factory_with_special_characters`
- `test_project_factory_with_empty_name`
- `test_bug_001_project_objects_not_dicts` (regression)

### Verification
```bash
$ python -m pytest tests/test_conftest.py -v
======================== 5 passed in 0.12s =========================

$ python -m pytest tests/ -v
======================== 257 passed in 7.44s =========================
```

### Code Compression
- Removed 60 lines of duplicate test data
- Centralized fixtures in conftest.py
- Net reduction: 30 lines
```

**C. Add Docstrings**:
```python
@pytest.fixture
def project_factory():
    """
    Factory fixture for creating Project objects with test data.
    
    Provides a function that creates Project instances with customizable
    attributes. This ensures tests use actual Project objects instead of
    dictionaries, maintaining type consistency with production code.
    
    Args:
        name (str): Project name. Defaults to "TestProject".
        repo_url (str): Repository URL. Defaults to test URL.
        **kwargs: Additional Project attributes.
    
    Returns:
        Callable: Function that creates Project instances.
    
    Example:
        >>> project = project_factory(name="MyApp", language="Python")
        >>> assert project.name == "MyApp"
        >>> assert isinstance(project, Project)
    """
    def _create_project(name="TestProject", **kwargs):
        return Project(name=name, repo_url="https://github.com/test/repo", **kwargs)
    return _create_project
```

---

### 12. FINAL VERIFICATION (GATE CHECKS)

**A. Run Full Test Suite**:
```bash
python -m pytest tests/ -v --cov=src --cov-report=html --cov-fail-under=90
```

**B. Verify Audit Improvements**:
```
✅ Pre-Implementation:  241/257 tests passing (93.8%)
✅ Post-Implementation: 257/257 tests passing (100%)
✅ Improvement: +16 tests fixed, +0.2% coverage
```

**C. Check Code Quality**:
```bash
# Linting (if configured)
python -m flake8 src/ tests/ --max-line-length=100

# Type checking (if configured)
python -m mypy src/

# Security scan
python -m bandit -r src/
```

**D. Verify No Deprecation Warnings**:
```bash
python -m pytest tests/ -v -W error::DeprecationWarning
# Should pass without warnings
```

**E. Performance Check**:
```bash
# Ensure tests run in reasonable time
time python -m pytest tests/
# Target: < 10 seconds for full suite
```

**F. Codebase Size Check**:
```bash
# Verify code compression
find src/ -name "*.py" -exec wc -l {} \; | awk '{sum+=$1} END {print sum " total lines"}'
# Target: Reduced from baseline
```

**G. Verify Backlog is Current**:
```bash
# Ensure all discovered bugs are in backlog
cat docs/BACKLOG.md | grep -E "\[ \]|\[/\]|\[x\]|\[!\]"

# Verify task marked complete
# Verify new bugs added
# Verify priorities assigned
```

---

### 13. STOP & REPORT

**DO NOT** start the next backlog item. Output the following:

```
✅ ITERATION COMPLETE: BUG-001.1

📋 Task Details:
- ID: BUG-001.1
- Title: Create ProjectFactory test fixture
- Priority: P0
- Effort: 45 minutes (estimated: 1h)

📁 Files Changed:
- tests/conftest.py (NEW, 120 lines)
- tests/test_dashboard_projects.py (MODIFIED, -60 lines)

🧪 Test Results:
- Total Tests: 257
- Passed: 257 (100%) ✅ +16 from baseline
- Failed: 0 (was 16) ✅ ALL FIXED
- Coverage: 94% (was 93.8%) ✅ +0.2%
- Duration: 7.44s

🖥️ UI Testing Results:
- Landing Page: ✅ All features functional
- Modals: ✅ All working correctly
- Dashboard: ✅ All features functional
- Regressions: ⚠️ 1 discovered (BUG-UI-REGRESSION-001)
- Console Errors: 0 JavaScript errors
- API Errors: 2 existing bugs (already in backlog)

📊 Code Compression:
- Lines Removed: 60 (duplicate test data)
- Lines Added: 120 (centralized fixtures)
- Net Change: +60 lines (but improved maintainability)
- Total Codebase: 2,440 lines (was 2,500) ✅ -60 lines

📋 Audit Summary:
PRE-IMPLEMENTATION:
- Tests: 241/257 passing (93.8%)
- UI Bugs: 3 identified
- Code Quality: 12 unused imports, 3 large files

POST-IMPLEMENTATION:
- Tests: 257/257 passing (100%) ✅ IMPROVED
- UI Bugs: 1 new regression (added to backlog)
- Code Quality: All issues resolved ✅

✅ Acceptance Criteria Met:
- [x] ProjectFactory fixture created
- [x] All tests use Project objects (not dicts)
- [x] 5 comprehensive tests added
- [x] All 257 tests passing
- [x] No deprecation warnings
- [x] Code coverage ≥90%
- [x] Docstrings added
- [x] Backlog updated with new bugs
- [x] Pre/Post audits completed
- [x] UI regression testing done

📝 Documentation Updated:
- [x] docs/BACKLOG.md - Marked BUG-001.1 as complete
- [x] docs/BACKLOG.md - Added BUG-UI-REGRESSION-001
- [x] walkthrough.md - Added implementation details
- [x] conftest.py - Added comprehensive docstrings
- [x] audit_report.md - Created pre/post audit reports

🐛 New Bugs Discovered & Added to Backlog:
- BUG-UI-REGRESSION-001: Delete button error handling (P1)

🔄 Next Task (DO NOT START):
- BUG-001.2: Update test mocks in test_dashboard_projects.py
```

---

## 🎯 QUALITY CHECKLIST

Before marking iteration complete, verify ALL items:

### Code Quality
- [ ] All tests pass (257/257)
- [ ] No failing tests
- [ ] No deprecation warnings
- [ ] Code coverage ≥90%
- [ ] No linting errors
- [ ] Type hints added to new code
- [ ] Docstrings added to public functions/classes

### Codebase Hygiene
- [ ] Dead code removed (unused imports, functions, files)
- [ ] Duplicate code extracted to utilities
- [ ] Large files split (<500 lines per file)
- [ ] Consistent naming conventions
- [ ] No magic numbers (use constants)
- [ ] No commented-out code

### Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Edge case tests added
- [ ] Regression tests added (if fixing bug)
- [ ] Tests are isolated and idempotent
- [ ] Mock external dependencies

### Documentation
- [ ] Backlog updated (task marked complete)
- [ ] Walkthrough updated with changes
- [ ] Docstrings added/updated
- [ ] README updated (if public API changed)
- [ ] No ad-hoc documentation files created

### Git
- [ ] Commits follow Conventional Commits format
- [ ] Commit messages are descriptive
- [ ] Small, logical commits (not one giant commit)
- [ ] Branch is green before completing

---

## 🚀 OPTIMIZATION GUIDELINES

### File Size Targets
- **Python files**: <500 lines
- **HTML templates**: <800 lines (consider splitting into components)
- **JavaScript**: <400 lines (extract to separate files)
- **Test files**: <600 lines (split by test class)

### Code Compression Strategies
1. **Extract Utilities**: Common logic → `src/utils/`
2. **Service Layer**: Business logic → `src/core/services.py`
3. **DTO Pattern**: API responses → `src/core/dto.py`
4. **Component Split**: Large templates → `templates/components/`
5. **Test Fixtures**: Shared test data → `tests/conftest.py`

### Deletion Candidates
- Unused imports
- Commented-out code
- Debug print statements
- Duplicate functions
- Obsolete test files
- Temporary files
- Old migration scripts (if completed)

---

## 📚 STANDARDS REFERENCE

### Python Style
- PEP 8 compliance
- Google-style docstrings
- Type hints for function signatures
- snake_case for functions/variables
- PascalCase for classes
- UPPER_CASE for constants

### Testing Style
- Arrange-Act-Assert pattern
- One assertion per test (when possible)
- Descriptive test names
- Use fixtures for setup
- Mock external dependencies
- Test edge cases

### Git Commit Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore  
**Example**: `fix(server): handle 403 errors for system projects`

---

## 🎓 EXAMPLES

### Example 1: Bug Fix Iteration

**Task**: BUG-UI-001 - Fix delete button error handling

**Steps**:
1. Select task from backlog
2. Mark in-progress
3. Write failing test
4. Implement fix
5. Run tests (all pass)
6. Clean up code
7. Commit
8. Update docs
9. Verify
10. Stop

**Output**:
```
✅ BUG-UI-001 Complete
Files: landing.html (MODIFIED)
Tests: 257 passed
Coverage: 93%
Lines: -15 (removed duplicate error handling)
```

### Example 2: Feature Implementation

**Task**: FEATURE-006 - Add /api/settings endpoint

**Steps**:
1. Select task
2. Analyze existing code
3. Write API tests
4. Implement endpoint
5. Add service layer
6. Extract utilities
7. Run full suite
8. Document
9. Verify
10. Stop

**Output**:
```
✅ FEATURE-006 Complete
Files: server.py (+50), services.py (NEW, 80), test_api.py (+120)
Tests: 265 passed (+8 new)
Coverage: 94%
Lines: +250 total, but split across 3 files
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Starting multiple tasks** - Only ONE task per iteration
2. **Skipping tests** - Always write tests first
3. **Large commits** - Make small, logical commits
4. **Ignoring coverage** - Maintain ≥90% coverage
5. **Leaving warnings** - Fix all deprecation warnings
6. **Creating ad-hoc docs** - Only update existing docs
7. **Magic numbers** - Use named constants
8. **Duplicate code** - Extract to utilities
9. **Large files** - Split files >500 lines
10. **Incomplete cleanup** - Remove all dead code

---

## 🏁 SUCCESS CRITERIA

An iteration is successful when:
- ✅ Exactly ONE task completed
- ✅ All 257+ tests passing
- ✅ Code coverage ≥90%
- ✅ No deprecation warnings
- ✅ Backlog updated
- ✅ Documentation updated
- ✅ Code compressed (dead code removed)
- ✅ SOLID principles followed
- ✅ Commits are clean and descriptive
- ✅ Ready for next iteration

---

**Remember**: Quality over speed. A well-tested, clean, compressed codebase is better than rushed, bloated code.
