#!/bin/bash
# Pre-commit hook to enforce codebase standards
# Copy this to .git/hooks/pre-commit

set -e

echo "🔍 Running pre-commit checks..."

# Check 1: No CSV/HTML files in root
if git diff --cached --name-only | grep -E '\.(csv|html)$' | grep -v '^output/'; then
    echo "❌ Error: CSV/HTML files should be in output/ folder, not root"
    exit 1
fi

# Check 2: No unauthorized files in docs/
DOCS_FILES=$(git diff --cached --name-only | grep '^docs/' || true)
for file in $DOCS_FILES; do
    if [[ ! "$file" =~ (\.gitignore|api/|rules/.*|standards/.*|backlog\.md|release-notes\.md|project-health\.md|conflict-map\.md|vision\.md|eventlet-migration\.md|system-health\.md)$ ]]; then
        # Ensure we are not failing on DELETED files.
        # git diff --cached --name-only just gives names, we should check status.
        if git diff --cached --name-status | grep -q "^D.*$file$"; then
           continue
        fi
        echo "❌ Error: Only standard doc files allowed in docs/"
        echo "   Attempted to add/modify: $file"
        exit 1
    fi
done

# Check 3: Python files have proper imports
PYTHON_FILES=$(git diff --cached --name-only | grep '\.py$' || true)
for file in $PYTHON_FILES; do
    # Basic check - can be enhanced
    if grep -q "^from [a-z]" "$file" 2>/dev/null; then
        if ! grep -q "^from src\." "$file" 2>/dev/null; then
            echo "⚠️  Warning: Check imports in $file (should use 'from src.xxx import')"
        fi
    fi
done

# Check 4: Test coverage minimum
if [[ -f "pytest.ini" ]]; then
    echo "✓ Tests will be run in CI/CD"
fi

# Check 5: Auto-scan staged Python files for Green AI violations
# Collect staged python files into an array to handle spaces correctly
STAGED_PY_FILES=()
while IFS= read -r file; do
    if [[ "$file" == *.py ]]; then
        STAGED_PY_FILES+=("$file")
    fi
done < <(git diff --cached --name-only)

if [ ${#STAGED_PY_FILES[@]} -gt 0 ]; then
    echo "🔍 Scanning staged Python files for green software violations..."

    # Run scan
    # We use python3 -m src.cli scan <files>
    if ! python3 -m src.cli scan "${STAGED_PY_FILES[@]}" --language python; then
        echo "❌ Error: Green AI violations found. Please fix them before committing."
        echo "   Tip: Use 'green-ai scan <file> --fix-all' or fix manually."
        exit 1
    fi
fi


# Check 6: Enforce 500 LOC change minimum
echo "🔍 Checking lines of code (LOC) changed..."
DIFF_STAT=$(git diff --cached --shortstat || true)

if [ -z "$DIFF_STAT" ]; then
    echo "❌ Error: No changes staged."
    exit 1
fi

INSERTIONS=$(echo "$DIFF_STAT" | grep -o '[0-9]\+ insertion' | awk '{print $1}')
DELETIONS=$(echo "$DIFF_STAT" | grep -o '[0-9]\+ deletion' | awk '{print $1}')

INSERTIONS=${INSERTIONS:-0}
DELETIONS=${DELETIONS:-0}
TOTAL_LOC=$((INSERTIONS + DELETIONS))

if [ "$TOTAL_LOC" -lt 500 ]; then
    echo "❌ Error: Commit must contain at least 500 lines of code change. Current: $TOTAL_LOC"
    exit 1
fi
echo "✓ LOC check passed ($TOTAL_LOC changes)"

echo "✅ Pre-commit checks passed!"
exit 0
