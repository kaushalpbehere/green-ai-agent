# PROMPT 3: FEATURE DEVELOPMENT

**Use When**: Adding new features to standardized codebase

---

## OBJECTIVE
Implement ONE feature with tests, maintain standards.

## INPUTS REQUIRED
- Feature ID from `docs/BACKLOG.md`
- Acceptance criteria
- Estimated effort

## PROCEDURE (7 Steps)

### 1. SELECT & PLAN
```bash
cat docs/BACKLOG.md  # Select ONE feature
```
Update: `[ ]` → `[/]`
Define: Files to create/modify, API contracts

### 2. WRITE TESTS FIRST
```python
# Unit tests
def test_<feature>_<scenario>():
    """Test <feature> <scenario>"""
    # Arrange, Act, Assert

# Integration tests
def test_<feature>_integration():
    """Test <feature> end-to-end"""
```

### 3. IMPLEMENT
- Create minimum code to pass tests
- Follow SOLID principles
- Add type hints
- Add docstrings

### 4. REFACTOR
- Extract utilities if needed
- Ensure files <500 lines
- Remove duplication

### 5. TEST
```bash
pytest tests/ -v --cov=src --cov-fail-under=90
```

### 6. DOCUMENT
- Update README if public API changed
- Add docstrings
- Update walkthrough

### 7. COMPLETE
- Backlog: `[/]` → `[x]`
- Report completion

## QUALITY GATES
- [ ] Tests written first
- [ ] All tests pass
- [ ] Coverage ≥90%
- [ ] Docstrings added
- [ ] No files >500 lines
- [ ] Backlog updated

---

**Token Count**: ~280 tokens
