"""
E2E tests for Advanced Rules (Deep Recursion, Inefficient Lookup, Regex in Loop)
"""
import pytest
from src.core.scanner import Scanner
import os

def test_e2e_advanced_rules_repro():
    repro_content = """
import re

# 1. Deep Recursion
def recursive_function(n):
    if n <= 0:
        return 0
    return 1 + recursive_function(n - 1)

# 2. Inefficient Lookup
def inefficient_lookup():
    my_list = [1, 2, 3, 4, 5]
    for i in range(100):
        if i in my_list: # Violation: list lookup in loop
            print("Found")

# 3. Regex in Loop
def regex_in_loop():
    data = ["a", "b", "c"]
    for item in data:
        pattern = re.compile(r"[a-z]") # Violation: re.compile in loop
        if pattern.match(item):
            print("Match")
"""
    repro_file = 'temp_repro_rules.py'
    try:
        with open(repro_file, 'w') as f:
            f.write(repro_content)

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

    finally:
        if os.path.exists(repro_file):
            os.remove(repro_file)
