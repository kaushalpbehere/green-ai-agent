"""
E2E tests for Advanced Rules (Deep Recursion, Inefficient Lookup, Regex in Loop)
"""
import pytest
from src.core.scanner import Scanner
import os

def test_e2e_advanced_rules_repro():
    repro_file = 'tests/repro_advanced_rules.py'
    assert os.path.exists(repro_file)

    scanner = Scanner()
    results = scanner.scan(repro_file)

    assert 'issues' in results
    issues = results['issues']

    found_recursion = False
    found_lookup = False
    found_regex = False

    for issue in issues:
        if issue['id'] == 'deep_recursion':
            found_recursion = True
        elif issue['id'] == 'inefficient_lookup':
            found_lookup = True
        elif issue['id'] == 'unnecessary_computation' and 're.compile' in issue['message']:
            found_regex = True

    assert found_recursion, "Deep recursion not detected in repro file"
    assert found_lookup, "Inefficient lookup not detected in repro file"
    assert found_regex, "Regex in loop not detected in repro file"
