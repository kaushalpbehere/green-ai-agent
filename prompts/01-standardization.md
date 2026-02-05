# PROMPT 1: CODEBASE STANDARDIZATION (Transition Phase)

**Use When**: Bringing existing codebase to standards (ONE-TIME SETUP)

---

## OBJECTIVE
Fix ALL critical bugs, achieve 100% test pass rate, establish quality standards. ONE task per run.

## CANONICAL SOURCES
- **Backlog**: `docs/BACKLOG.md`
- **Bugs**: `.gemini/antigravity/brain/*/bug_backlog.md`
- **Standards**: This prompt

## INVARIANTS (Non-Negotiable)
1. **Always Green**: All tests MUST pass before completing
2. **Coverage ≥90%**: For modified modules
3. **No Warnings**: Fix all deprecation warnings
4. **Update Backlog**: Mark `[ ]`→`[/]`→`[x]` immediately
5. **Delete Dead Code**: Remove unused imports/functions/files
6. **Files <500 lines**: Split larger files
7. **ONE Task**: Complete exactly ONE microtask and STOP

## PROCEDURE (10 Steps)

### 1. BASELINE AUDIT
```bash
# Run tests, capture baseline
pytest tests/ -v --tb=short > baseline.txt 2>&1
pytest tests/ -v --tb=no -q 2>&1 | Select-String "passed|failed"
```
Document: Total tests, passing, failing, coverage

### 2. SELECT TASK
```bash
cat docs/BACKLOG.md  # Pick ONE P0/P1 task
```
Output: Task ID, priority, effort, files to modify

### 3. MARK IN-PROGRESS
Update `docs/BACKLOG.md`: `[ ]` → `[/]`

### 4. TDD LOOP
- Write failing test
- Implement minimum code
- Run test (expect pass)
- Refactor
- Run full suite (all pass)

### 5. CLEANUP
- Remove unused imports: `vulture src/ --min-confidence 80`
- Extract duplicates to utilities
- Split files >500 lines
- Delete commented code

### 6. TEST
```bash
# Unit + Integration + Edge + Regression
pytest tests/ -v --cov=src --cov-fail-under=90
```

### 7. COMMIT (Optional)
```bash
git add <files>
git commit -m "type(scope): description"
```

### 8. UPDATE BACKLOG
Mark complete: `[/]` → `[x]`
Add discovered bugs with priority

### 9. VERIFY
```bash
# Compare with baseline
pytest tests/ -v --tb=no -q 2>&1 | Select-String "passed|failed"
```
Ensure: No regressions, coverage improved

### 10. STOP & REPORT
```
✅ COMPLETE: <TASK-ID>
Tests: X/Y passing (was A/B) ✅ +N fixed
Coverage: X% (was Y%) ✅ +Z%
Files: <list>
Backlog: Updated
Next: <NEXT-TASK> (DO NOT START)
```

## QUALITY GATES
- [ ] All tests pass
- [ ] Coverage ≥90%
- [ ] No warnings
- [ ] Backlog updated
- [ ] Dead code removed
- [ ] Files <500 lines

## WHEN COMPLETE
When ALL bugs fixed and tests pass 100%, transition to modular prompts (PROMPT 2-5).

---

**Token Count**: ~400 tokens (vs 2000+ in full prompt)
