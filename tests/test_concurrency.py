import pytest
import os
import tempfile
import shutil
from src.core.scanner import Scanner

def test_scanner_concurrency():
    """Test that scanner works with multiple files in parallel."""
    # Create a temporary directory with multiple Python files
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create 10 files
        for i in range(10):
            with open(os.path.join(tmpdirname, f'test_{i}.py'), 'w') as f:
                f.write(f'def test_func_{i}():\n    pass\n')

        scanner = Scanner(language='python')
        results = scanner.scan(tmpdirname)

        # Verify results
        assert 'issues' in results
        assert 'metadata' in results
        assert results['metadata']['total_files'] == 10
        # Emissions should be calculated
        assert results['codebase_emissions'] >= 0

def test_scanner_worker_concurrency_error_handling():
    """Test that worker handles errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a file with syntax error
        with open(os.path.join(tmpdirname, 'error.py'), 'w') as f:
            f.write('def broken_func(\n') # Missing closing parenthesis and block

        scanner = Scanner(language='python')
        results = scanner.scan(tmpdirname)

        assert 'issues' in results
        # Should have a syntax error issue
        assert any(issue['id'] == 'syntax_error' for issue in results['issues'])
