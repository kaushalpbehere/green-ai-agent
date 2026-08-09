with open(".git_hooks_pre-commit.sh", "r") as f:
    content = f.read()

import re
content = re.sub(
    r'\(\.gitignore\|api/\|rules/\.\*\|standards/\.\*\|backlog\\\.md\|release-notes\\\.md\|project-health\\\.md\|conflict-map\\\.md\|vision\\\.md\|eventlet-migration\\\.md\|system-health\\\.md\)',
    r'(\\.gitignore|api/|rules/.*|standards/.*|architecture\\.md|release\\.md|backlog\\.md|release-notes\\.md|project-health\\.md|conflict-map\\.md|vision\\.md|eventlet-migration\\.md|system-health\\.md)',
    content
)

# wait actually let's just rewrite the whole if line since I messed up earlier.
with open(".git_hooks_pre-commit.sh", "w") as f:
    f.write(content)
