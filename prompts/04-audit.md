# PROMPT 4: COMPREHENSIVE AUDIT

**Use When**: Periodic quality audits (weekly/before releases)

---

## OBJECTIVE
Identify ALL bugs, regressions, quality issues. Update backlog.

## PROCEDURE (5 Steps)

### 1. TEST AUDIT
```bash
# Run full suite
pytest tests/ -v --tb=short > audit_$(date +%Y%m%d).txt 2>&1

# Summary
pytest tests/ -v --tb=no -q 2>&1 | Select-String "passed|failed"
```
Document: Pass rate, failures, coverage, warnings

### 2. UI AUDIT (if applicable)
```bash
# Start server
python src/ui/server.py &

# Test checklist
```
- [ ] All buttons functional
- [ ] All forms validate
- [ ] All modals open/close
- [ ] No console errors
- [ ] No API errors

Document: Broken features, console errors, API failures

### 3. CODE QUALITY AUDIT
```bash
# Dead code
vulture src/ --min-confidence 80

# Large files
find src/ -name "*.py" -exec wc -l {} \; | sort -rn | head -10

# Duplicates
pylint src/ --disable=all --enable=duplicate-code
```
Document: Unused code, large files, duplicates

### 4. UPDATE BACKLOG
Add ALL discovered issues to `docs/BACKLOG.md`:
```markdown
## 🐛 AUDIT FINDINGS (YYYY-MM-DD)

- [ ] **BUG-AUDIT-001**: <description> (P0/P1/P2)
- [ ] **BUG-AUDIT-002**: <description> (P0/P1/P2)
...
```

### 5. CREATE AUDIT REPORT
```markdown
# Audit Report YYYY-MM-DD

## Summary
- Tests: X/Y passing (Z% pass rate)
- Coverage: X%
- UI Issues: N found
- Code Quality: M issues

## Critical Issues (P0)
- <list>

## High Priority (P1)
- <list>

## Backlog Updates
- Added N bugs
- Prioritized by severity
```

## OUTPUT
```
🔍 AUDIT COMPLETE
Date: YYYY-MM-DD
Tests: X/Y passing (Z%)
Coverage: X%
Bugs Found: N (P0: X, P1: Y, P2: Z)
Backlog: Updated with N new items
Report: audit_YYYYMMDD.md
```

---

**Token Count**: ~350 tokens
