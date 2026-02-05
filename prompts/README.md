# GREEN-AI AGENT - PROMPT SYSTEM

Modular, token-efficient prompts for different development workflows.

---

## 📁 PROMPT CATALOG

### Phase 1: Transition (Use First)

**[01-standardization.md](01-standardization.md)** - Codebase Standardization  
**Use**: Bringing existing codebase to standards (ONE-TIME)  
**Tokens**: ~400  
**Goal**: Fix all bugs, 100% test pass rate, establish quality baseline

---

### Phase 2: Ongoing Development (Use After Standardization)

**[02-bugfix.md](02-bugfix.md)** - Bug Fix Workflow  
**Use**: Fixing individual bugs  
**Tokens**: ~250  
**Goal**: Fix ONE bug, add regression test, maintain green

**[03-feature.md](03-feature.md)** - Feature Development  
**Use**: Adding new features  
**Tokens**: ~280  
**Goal**: Implement ONE feature with TDD, maintain standards

**[04-audit.md](04-audit.md)** - Comprehensive Audit  
**Use**: Periodic quality checks (weekly/pre-release)  
**Tokens**: ~350  
**Goal**: Identify all issues, update backlog

**[05-refactor.md](05-refactor.md)** - Refactoring  
**Use**: Improving code quality  
**Tokens**: ~280  
**Goal**: Refactor ONE module, maintain behavior

---

## 🚀 USAGE GUIDE

### Step 1: Standardization (First Time Only)
```
Use: prompts/01-standardization.md
Complete ALL P0/P1 bugs until 100% tests pass
Transition when: All tests green, coverage ≥90%
```

### Step 2: Choose Workflow
```
Bug Fix:     prompts/02-bugfix.md
New Feature: prompts/03-feature.md
Audit:       prompts/04-audit.md (weekly)
Refactor:    prompts/05-refactor.md (as needed)
```

### Example Request
```
Follow prompts/02-bugfix.md
Fix BUG-UI-001 from docs/BACKLOG.md
```

---

## 📊 TOKEN EFFICIENCY

| Prompt | Tokens | Use Case | Frequency |
|--------|--------|----------|-----------|
| 01-standardization | ~400 | Transition | One-time |
| 02-bugfix | ~250 | Bug fixes | Per bug |
| 03-feature | ~280 | Features | Per feature |
| 04-audit | ~350 | Quality check | Weekly |
| 05-refactor | ~280 | Code quality | As needed |

**Total**: ~1,560 tokens for all prompts  
**vs Old**: ~2,000+ tokens for single monolithic prompt  
**Savings**: 22% reduction + better focus

---

## 🎯 WORKFLOW DECISION TREE

```
START
  │
  ├─ Codebase has bugs? → 01-standardization.md
  │
  ├─ Fixing a bug? → 02-bugfix.md
  │
  ├─ Adding feature? → 03-feature.md
  │
  ├─ Weekly check? → 04-audit.md
  │
  └─ Improving code? → 05-refactor.md
```

---

## 📋 SHARED INVARIANTS (All Prompts)

1. **Always Green**: All tests MUST pass
2. **Coverage ≥90%**: For modified code
3. **Update Backlog**: Real-time updates
4. **ONE Task**: Complete exactly ONE item
5. **No Warnings**: Fix deprecation warnings
6. **Files <500 lines**: Split larger files

---

## 🔄 TRANSITION PLAN

### Current State
- 16 failing tests
- Mixed code quality
- No standardization

### Phase 1: Standardization (Use 01-standardization.md)
```
Week 1-2: Fix all P0 bugs
Week 3: Fix all P1 bugs
Goal: 100% tests passing, coverage ≥90%
```

### Phase 2: Modular Development (Use 02-05)
```
Ongoing: Use specialized prompts per task
Weekly: Run 04-audit.md
As needed: Use 05-refactor.md
```

---

## 💡 BEST PRACTICES

### When to Use Each Prompt

**01-standardization.md**:
- Initial codebase setup
- After major refactoring
- When test pass rate <95%

**02-bugfix.md**:
- Any bug in backlog
- Regression fixes
- Hot fixes

**03-feature.md**:
- New functionality
- API additions
- UI enhancements

**04-audit.md**:
- Before releases
- Weekly quality checks
- After major changes

**05-refactor.md**:
- Code smells detected
- Files >500 lines
- Duplicate code found

---

## 📚 REFERENCES

- **Backlog**: `docs/BACKLOG.md`
- **Bugs**: `.gemini/antigravity/brain/*/bug_backlog.md`
- **Audits**: `.gemini/antigravity/brain/*/ui_testing_report.md`
- **History**: `.gemini/antigravity/brain/*/walkthrough.md`

---

## ⚡ QUICK START

1. **First Time**: Use `01-standardization.md` until all tests pass
2. **Ongoing**: Use `02-bugfix.md` or `03-feature.md` per task
3. **Weekly**: Run `04-audit.md` to find issues
4. **As Needed**: Use `05-refactor.md` to improve quality

---

**Remember**: Each prompt is focused, efficient, and token-optimized for its specific use case.
