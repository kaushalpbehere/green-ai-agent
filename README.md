# Green-AI
> Empower every developer to write energy-efficient code by default.

![Version](https://img.shields.io/badge/version-v1.0.5-blue.svg)

## Status

| Milestone | Version | Phase | State | Health |
|---|---|---|---|---|
| Stability Gate | v1.0.5 | 2 — Action & Expansion | ACTIVE | Green |

## Docs

| Document | Purpose |
|---|---|
| [roadmap.md](./docs/roadmap.md) | Phased roadmap and milestones |
| [backlog.md](./docs/backlog.md) | Active task list by epic |
| [standards.md](./docs/standards.md) | Coding standards, rules, and quality gates |
| [architecture.md](./docs/architecture.md) | System design, decisions, and deployment |
| [release.md](./docs/release.md) | Release notes and health metrics |
| [CLAUDE.md](./CLAUDE.md) | Claude AI agent configuration |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Scan a directory
python -m src.cli scan ./src

# Start the dashboard
python -m src.cli dashboard --host 0.0.0.0 --port 5000

# Auto-fix with LLM
python -m src.cli fix_ai ./src

# Run tests
python -m pytest tests/ -v

# Docker
docker-compose up
```

## Languages Supported

Python · JavaScript · TypeScript · Java · Go · C#

## Active Work

**[EPIC-09] IDE Plugins** — VS Code extension + LSP server  
**[EPIC-18] Audit** — Automated security test expansion  

See [backlog.md](./docs/backlog.md) for full task list.
