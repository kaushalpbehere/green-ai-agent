# PROMPT 2: BUG FIX WORKFLOW

**Use When**: Fixing bugs in standardized codebase

---

## OBJECTIVE
Fix ONE bug, add regression test, maintain green status.

## INPUTS REQUIRED
- Bug ID from `docs/BACKLOG.md`
- Severity: P0/P1/P2/P3
- Affected files

## PROCEDURE (6 Steps)

### 1. SELECT & MARK
```bash
cat docs/BACKLOG.md  # Select ONE bug
```
Update: `[ ]` → `[/]`

### 2. REPRODUCE
Write test that FAILS demonstrating bug:
```python
def test_bug_<ID>_<description>():
    """Regression test for BUG-<ID>"""
    # Arrange: Setup that triggers bug
    # Act: Execute buggy code
    # Assert: Verify bug exists (should FAIL initially)
```

### 3. FIX
Implement minimum fix to pass test.

### 4. VERIFY
```bash
# Run regression test
pytest tests/test_file.py::test_bug_<ID> -v

# Run full suite
pytest tests/ -v --cov=src --cov-fail-under=90
```

### 5. UPDATE
- Backlog: `[/]` → `[x]`
- Walkthrough: Document fix, root cause, test

### 6. REPORT
```
✅ BUG-<ID> FIXED
Root Cause: <brief>
Fix: <brief>
Tests: All passing
Regression Test: test_bug_<ID>_<description>
```

## QUALITY GATES
- [ ] Regression test added
- [ ] All tests pass
- [ ] Coverage maintained
- [ ] Backlog updated

---

**Token Count**: ~250 tokens
