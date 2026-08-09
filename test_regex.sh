#!/bin/bash
file="docs/architecture.md"
if [[ ! "$file" =~ (\.gitignore|api/|rules/.*|standards/.*|architecture\.md|release\.md|backlog\.md|release-notes\.md|project-health\.md|conflict-map\.md|vision\.md|eventlet-migration\.md|system-health\.md)$ ]]; then
    echo "No match"
else
    echo "Match"
fi
