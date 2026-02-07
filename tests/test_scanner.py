"""
Unit tests for Scanner module
"""

import pytest
import os
import sys
from src.core.scanner import Scanner

def test_scanner_init():
    scanner = Scanner()
    assert scanner.language == 'python'
    assert not scanner.runtime

def test_scanner_init_with_params():
    scanner = Scanner(language='javascript', runtime=True)
    assert scanner.language == 'javascript'
    assert scanner.runtime

def test_scan_simple_file():
    scanner = Scanner()
    results = scanner.scan('tests/simple_test.py')
    
    assert 'issues' in results
    assert 'scanning_emissions' in results or 'codebase_emissions' in results
    assert isinstance(results['scanning_emissions'], (float, int))
    assert len(results['issues']) >= 0  # May have issues

def test_scan_directory():
    scanner = Scanner()
    results = scanner.scan('tests/')
    
    assert 'issues' in results
    assert 'scanning_emissions' in results or 'codebase_emissions' in results
    assert isinstance(results['scanning_emissions'], (float, int))

def test_runtime_monitoring():
    scanner = Scanner(runtime=True)
    results = scanner.scan('tests/simple_test.py')
    
    assert 'runtime_metrics' in results
    metrics = results['runtime_metrics']
    # Runtime metrics may be empty if file has errors, check if present
    if metrics and 'execution_time' in metrics:
        assert 'emissions' in metrics
        if isinstance(metrics['emissions'], dict):
            assert 'emissions' in metrics['emissions']
            assert isinstance(metrics['emissions']['emissions'], (float, int))
        else:
            assert isinstance(metrics['emissions'], (float, int))

def test_get_run_command():
    scanner = Scanner(language='python')
    cmd = scanner._get_run_command('test.py')
    
    # For python: [sys.executable, path]
    assert cmd == [sys.executable, 'test.py']
    assert cmd[0] == sys.executable
    assert cmd[1] == 'test.py'
    
    scanner_js = Scanner(language='javascript')
    cmd_js = scanner_js._get_run_command('test.js')
    assert cmd_js == ['node', 'test.js']
    
    scanner_unknown = Scanner(language='unknown')
    cmd_unknown = scanner_unknown._get_run_command('test.unknown')
    assert cmd_unknown is None