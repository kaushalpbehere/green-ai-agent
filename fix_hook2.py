with open(".git_hooks_pre-commit.sh", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "if [[ ! \"$file\" =~ (\\.gitignore|api/|rules/.*|standards/.*|backlog\\.md|" in line:
        lines[i] = "    if [[ ! \"$file\" =~ (\\.gitignore|api/|rules/.*|standards/.*|architecture\\.md|release\\.md|backlog\\.md|release-notes\\.md|project-health\\.md|conflict-map\\.md|vision\\.md|eventlet-migration\\.md|system-health\\.md)$ ]]; then\n"

with open(".git_hooks_pre-commit.sh", "w") as f:
    f.writelines(lines)
