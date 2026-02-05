# Green-AI: Lightweight Green Software Analysis Utility

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-brightgreen)]()

---

## 🌱 What is Green-AI?

Green-AI is a lightweight utility for detecting and fixing energy-inefficient code patterns. Our mission is to help developers write sustainable software by identifying green software violations in real-time.

**Key Focus**: Energy efficiency, carbon emissions reduction, sustainable development.

---

## ✨ Features (v0.1.0)

### 📊 Code Scanning
- **Multi-language support**: Python, JavaScript (expanding to 7 languages in Phase 2)
- **Tree-sitter AST parsing**: Accurate, language-agnostic code analysis
- **10+ detection rules**: Inefficient loops, unnecessary computations, resource leaks, etc.

### ⚡ Dual-Metric Emissions Tracking
- **Scanning emissions**: Real-time energy cost of analysis (CodeCarbon)
- **Codebase emissions**: Estimated energy cost of running the code
- **Per-issue breakdown**: Energy impact of each violation

### 🎯 Analysis Engine
- **Complexity metrics**: Cyclomatic complexity, nesting depth, loop iterations
- **Energy modeling**: Baseline + multipliers for code patterns
- **Severity scoring**: Low, Medium, High risk levels

### 🖥️ Web Dashboard
- **SonarQube-like visualization**: Real-time issue display
- **Severity filtering**: Filter by issue type and risk level
- **Per-file view**: Understand violations in each file
- **Dual-metric display**: See scanning + codebase emissions

### 💻 CLI Interface
```bash
# Scan a project
green-ai scan /path/to/project --language python

# Auto-fix violations
green-ai fix /path/to/project --auto

# Launch dashboard
green-ai dashboard

# Monitor runtime emissions
green-ai monitor --runtime
```

### ✅ Production Ready
- **18+ tests**: Unit, integration, and performance tests
- **60%+ coverage**: Comprehensive test suite
- **CI/CD ready**: Pytest automation, GitHub Actions compatible

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/green-ai-agent.git
cd green-ai-agent

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

### Basic Usage
```bash
# Scan Python code
python -m src.cli scan . --language python

# View web dashboard
python -m src.cli dashboard --port 5000

# Get help
python -m src.cli --help
```

---

## 📁 Project Structure

```
green-ai-agent/
├── src/
│   ├── cli.py                      # Unified CLI entry point
│   ├── core/                       # Core scanning & analysis
│   │   ├── scanner.py              # AST parsing + CodeCarbon
│   │   ├── analyzer.py             # Complexity analysis
│   │   ├── fixer.py                # Fix suggestions
│   │   └── rules.py                # Rule engine
│   ├── ui/                         # Web interface
│   │   └── server.py               # Flask dashboard
│   ├── integrations/               # Git, CI/CD (Phase 2)
│   ├── agents/                     # Autonomous fixer (Phase 2)
│   ├── storage/                    # Persistence (Phase 2)
│   └── utils/                      # Shared utilities
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── performance/                # Benchmarks
├── docs/                           # Documentation
│   ├── PRD.md                      # Product requirements
│   └── Roadmap.md                  # Development roadmap
├── scripts/                        # Build & deployment
├── archive/                        # Historical docs (Phase 1)
├── CHANGELOG.md                    # Release notes
├── BACKLOG.md                      # Active tasks
├── MASTER_BACKLOG.md               # Detailed specs
└── README.md                       # This file
```

---

## 📊 Current Status (v0.1.0)

| Aspect | Status |
|--------|--------|
| **Languages** | 2 (Python, JavaScript) |
| **Detection Rules** | 10+ |
| **Test Coverage** | ~60% |
| **Performance** | <5s per 1000 LOC |
| **Release** | ✅ Initial MVP Complete |

---

## 🗓️ Roadmap

### Phase 1: ✅ COMPLETE (74 days)
- MVP with 2 languages
- Web dashboard
- Runtime monitoring
- Basic rule engine

### Phase 2: 🟡 IN PROGRESS (January 24 - March 14, 2026)
**4 Epics, 34+ Stories, 57 Days**
- Unified core consolidation
- 5 new languages (Java, TypeScript, Go, Rust, C#)
- Autonomous fixer with LLM
- REST API + CLI enhancements
- YAML-based rules
- Git & CI/CD integration

### Phase 3: 🔮 PLANNED (March 15+)
- 10 more languages (15 total)
- Cloud deployment
- Enterprise features
- Team collaboration

**See `docs/Roadmap.md` for detailed timeline.**

---

## 🔧 Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Core language |
| Tree-sitter | 0.20.4 | Multi-language AST parsing |
| CodeCarbon | 3.2.1 | Emissions tracking |
| Flask | 3.1.2 | Web dashboard |
| Click | 8.3.1 | CLI framework |
| Pytest | 9.0.2 | Testing |

---

## 📚 Documentation

- **[PRD.md](docs/PRD.md)** - Product vision and requirements
- **[Roadmap.md](docs/Roadmap.md)** - Development timeline and milestones
- **[MASTER_BACKLOG.md](MASTER_BACKLOG.md)** - Detailed Phase 2 specs (5000+ words)
- **[BACKLOG.md](BACKLOG.md)** - Active sprint tasks
- **[CHANGELOG.md](CHANGELOG.md)** - Release notes and version history
- **[QUICK_REFERENCE_CARD.md](QUICK_REFERENCE_CARD.md)** - One-page quick reference

---

## 🤝 Contributing

Green-AI is an open-source project focused on sustainable software. We welcome contributions!

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest tests/ -v`
5. Maintain >80% code coverage
6. Submit a pull request

### Development Workflow
- All **output files go to `output/` folder** (CSV, HTML, emissions)
- Only **backlog.md** and **release-notes.md** in docs/ folder
- Write docstrings for all functions
- Add tests for new features
- Use `pathlib.Path` for file operations
- Import modules: `from src.core.xxx import`

### Repository Standards

#### Directory Organization
```
green-ai-agent/
├── src/                      # Source code (all modules)
├── tests/                    # Test files (pytest)
├── rules/                    # YAML rule definitions
├── docs/                     # ONLY: backlog.md, release-notes.md
├── output/                   # ALL generated reports (CSV, HTML, emissions, logs)
├── data/                     # Data files (CSVs from scanning)
└── [root files]              # Only: README.md, requirements.txt, config files
```

#### Code Patterns

**Output Files** - Always use output/ folder:
```python
# ✅ CORRECT - Uses output folder
from src.core.export import CSVExporter
exporter = CSVExporter()  # Defaults to output/green-ai-report.csv

# ❌ WRONG - Creates file in root
exporter = CSVExporter('green-ai-report.csv')
```

**Path Handling** - Use pathlib for cross-platform compatibility:
```python
# ✅ CORRECT
from pathlib import Path
output_dir = Path(__file__).parent.parent.parent / 'output'
output_dir.mkdir(parents=True, exist_ok=True)

# ❌ WRONG - String paths, platform-specific
output_file = 'output\\report.csv'
```

**Imports** - Always use src module pattern:
```python
# ✅ CORRECT
from src.core.export import CSVExporter
from src.core.scanner import Scanner

# ❌ WRONG
from export import CSVExporter
```

**Logging** - All logs to output/logs/:
```python
# ✅ CORRECT - Logs to output/logs/
import logging
from pathlib import Path
logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(logs_dir / 'app.log')

# ❌ WRONG - Logging to root
handler = logging.FileHandler('app.log')
```

#### Standards Summary
- **Output files**: CSV, HTML, emissions → `output/` folder only
- **Documentation**: Only backlog.md + release-notes.md in `docs/`
- **Code style**: PEP 8 + type hints
- **Test coverage**: Minimum 80%, target 85%+
- **Imports**: Always `from src.module import` pattern
- **Logs**: All to `output/logs/` (pytest, Flask, CLI)
- **Paths**: Use `pathlib.Path` for cross-platform compatibility

#### GitHub Copilot Integration
When generating code, constrain with:
- "Save results to output/ folder"
- "Update docs/backlog.md with..."
- "Use pathlib.Path for file operations"
- "All logs should go to output/logs/"

---

## 🚫 Copilot & File Creation Policy

> **STRICT RULE:** No new files or folders may be created in this repository by Copilot or any automated tool without explicit USER permission. All documentation, code, and configuration changes must be reviewed and approved by a human user. Any attempt to auto-generate files, markdowns, or logs outside the approved structure will be rejected.

- All outputs must go to the `output/` folder.
- Only `BACKLOG.md` and `release-notes.md` are allowed in `docs/`.
- No new markdown or config files may be created in any folder unless approved by the USER.
- All code, test, and rule files must follow the structure in this README.
- Any violation of this policy will be reverted.

---

## 🧹 Maintenance & Folder Policy

- All cache, build, and temporary folders (e.g., `.pytest_cache/`, `__pycache__/`, `data/`) are deleted as part of regular maintenance and must not be committed or recreated.
- Only the following folders are allowed at the top level: `src/`, `tests/`, `rules/`, `docs/`, `output/`, `.github/`.
- All module documentation should be merged into the main README unless it is essential for developer onboarding or rule explanation.
- If a file or folder is not referenced in code or documentation, it will be deleted.

---

## 📞 Support

### Questions or Issues?
- Review [docs/backlog.md](docs/backlog.md) for feature roadmap
- Review [docs/release-notes.md](docs/release-notes.md) for current version
- Check Contributing section above for development standards

---

## 📜 License

Green-AI is licensed under the MIT License. See LICENSE file for details.

---

## 🌍 Vision

Green-AI contributes to the Green Software Foundation's mission of building a more sustainable planet through better software practices.

**Let's build green, efficient, and sustainable software together! 🌱**

---

**Version**: 0.4.0  
**Last Updated**: January 28, 2026  
**Status**: Active Development (Phase 2 Launching)

