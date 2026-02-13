# Development Standards

## 🛠️ Codebase Structure

We follow a modular `src` layout. All source code resides in `src/`.

```
green-ai-agent/
├── src/                      # Source code (all modules)
├── tests/                    # Test files (pytest)
├── rules/                    # YAML rule definitions
├── docs/                     # Documentation (backlog, release-notes, vision, standards)
├── output/                   # ALL generated reports (CSV, HTML, emissions, logs)
├── data/                     # Data files (CSVs from scanning)
└── [root files]              # Only: README.md, requirements.txt, config files
```

### 🚫 Copilot & File Creation Policy

> **STRICT RULE:** No new files or folders may be created in this repository by Copilot or any automated tool without explicit USER permission. All documentation, code, and configuration changes must be reviewed and approved by a human user. Any attempt to auto-generate files, markdowns, or logs outside the approved structure will be rejected.

- All outputs must go to the `output/` folder.
- Only `BACKLOG.md`, `release-notes.md`, `vision.md`, and `development-standards.md` are allowed in `docs/`.
- No new markdown or config files may be created in any folder unless approved by the USER.
- All code, test, and rule files must follow the structure in this README.
- Any violation of this policy will be reverted.

## 📝 Coding Conventions

### Python (PEP 8+)

- **Imports**: Always use absolute imports rooted at `src`.
  ```python
  # ✅ CORRECT
  from src.core.export import CSVExporter
  from src.core.scanner import Scanner

  # ❌ WRONG
  from export import CSVExporter
  ```

- **Path Handling**: Use `pathlib.Path` for cross-platform compatibility.
  ```python
  # ✅ CORRECT
  from pathlib import Path
  output_dir = Path(__file__).parent.parent.parent / 'output'

  # ❌ WRONG - String paths, platform-specific
  output_file = 'output\\report.csv'
  ```

- **Type Hints**: Use type hints for function arguments and return values.
  ```python
  def analyze_complexity(code: str) -> dict[str, int]:
      ...
  ```

- **Output Files**: All generated files must be saved in the `output/` directory.
  ```python
  # ✅ CORRECT - Uses output folder
  from src.core.export import CSVExporter
  exporter = CSVExporter()  # Defaults to output/green-ai-report.csv

  # ❌ WRONG - Creates file in root
  exporter = CSVExporter('green-ai-report.csv')
  ```

- **Logging**: All logs must be directed to `output/logs/app.log`.
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

### JavaScript / TypeScript (If applicable)

- Use strict mode (`'use strict';`).
- Prefer `const` over `let`, avoid `var`.
- Use async/await for asynchronous operations.

## ✅ Testing (Pytest)

- **Framework**: Use `pytest`.
- **Location**: `tests/` directory.
- **Coverage**: Maintain >80% code coverage. Target 85%+.
- **Mocking**: Use `unittest.mock` or `pytest-mock` for external dependencies (network, file I/O).
- **Fixtures**: Use `conftest.py` for shared fixtures.

Run tests:
```bash
pytest tests/ -v
```

## 📦 Data Models

- Use `pydantic` for data validation and serialization.
- Ensure strict typing for all models.

## 🧹 Maintenance & Folder Policy

- All cache, build, and temporary folders (e.g., `.pytest_cache/`, `__pycache__/`, `data/`) are deleted as part of regular maintenance and must not be committed or recreated.
- Only the following folders are allowed at the top level: `src/`, `tests/`, `rules/`, `docs/`, `output/`, `.github/`.
- All module documentation should be merged into the main README unless it is essential for developer onboarding or rule explanation.
- If a file or folder is not referenced in code or documentation, it will be deleted.

## 🔄 Workflow

1. **Pull Request**: Create a PR for significant changes (>200 LOC or 5 tasks).
2. **Review**: All PRs must be reviewed.
3. **Merge**: Merge only when all tests pass and coverage is maintained.
4. **Release**: Update `docs/release-notes.md` with user-facing changes.
