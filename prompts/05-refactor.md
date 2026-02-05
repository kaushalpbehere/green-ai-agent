# PROMPT 5: REFACTORING

**Use When**: Improving code quality without changing behavior

---

## OBJECTIVE
Refactor ONE module/file, maintain all tests passing.

## INPUTS REQUIRED
- Target file/module
- Refactoring goal (reduce size, extract utilities, improve naming)

## PROCEDURE (6 Steps)

### 1. BASELINE
```bash
# Run tests BEFORE refactoring
pytest tests/ -v --cov=src --cov-fail-under=90 > refactor_baseline.txt
```
Ensure: 100% tests passing

### 2. IDENTIFY IMPROVEMENTS
- Functions >50 lines → Extract helpers
- Classes >300 lines → Split
- Duplicate code → Extract to utilities
- Magic numbers → Named constants
- Poor names → Improve clarity

### 3. REFACTOR
Make changes while keeping tests green:
```bash
# After each change, run tests
pytest tests/ -v
```

### 4. VERIFY NO BEHAVIOR CHANGE
```bash
# Compare test results
pytest tests/ -v --cov=src --cov-fail-under=90 > refactor_after.txt
diff refactor_baseline.txt refactor_after.txt
```
Ensure: Same tests pass, same coverage

### 5. MEASURE IMPROVEMENT
```bash
# Before/After metrics
wc -l <file>
vulture <file>
```
Document: Lines reduced, complexity reduced

### 6. REPORT
```
✅ REFACTOR COMPLETE
File: <filename>
Lines: X → Y (-Z lines)
Functions: Extracted N helpers
Tests: All passing (no behavior change)
Coverage: Maintained at X%
```

## QUALITY GATES
- [ ] All tests still pass
- [ ] No new tests needed (behavior unchanged)
- [ ] Coverage maintained
- [ ] Code metrics improved

---

**Token Count**: ~280 tokens
