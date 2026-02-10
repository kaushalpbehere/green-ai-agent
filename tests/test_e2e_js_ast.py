import pytest
from src.core.scanner import Scanner

def test_js_ast_e2e(tmp_path):
    # Create a dummy JS file
    js_file = tmp_path / "test_ast.js"
    js_file.write_text("""
    console.log("Hello");
    eval("1+1");
    const x = 999;
    """, encoding="utf-8")

    # Run scan
    scanner = Scanner(language='javascript')
    results = scanner.scan(str(tmp_path))

    issues = results['issues']

    # Assert specific violations found
    console_log = next((i for i in issues if i['id'] == 'excessive_console_logging'), None)
    eval_usage = next((i for i in issues if i['id'] == 'eval_usage'), None)

    assert console_log is not None, "excessive_console_logging should be detected"
    assert eval_usage is not None, "eval_usage should be detected"

def test_js_ast_magic_numbers(tmp_path):
    js_file = tmp_path / "test_magic.js"
    js_file.write_text("""
    const x = 500;
    """, encoding="utf-8")

    scanner = Scanner(language='javascript')
    results = scanner.scan(str(tmp_path))
    issues = results['issues']

    magic = next((i for i in issues if i['id'] == 'magic_numbers'), None)
    assert magic is not None, "magic_numbers should be detected"
    assert "500.0" in magic['message'] # Check if AST detected it (float formatted) or Regex (original string)
    # Regex version: pattern = r'[^a-zA-Z0-9_]\s([0-9]{3,})\s[^a-zA-Z0-9_]'
    # Regex message: f'Magic number "{number}" usage. Use named constants.' (number is int)
    # AST message: f'Magic number "{val}" usage. Use named constants.' (val is float)

    # So if "500.0" is in message, it confirms AST detector found it!
