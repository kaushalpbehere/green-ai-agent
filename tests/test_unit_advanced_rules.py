"""
Unit tests for Advanced Rules (Deep Recursion, Inefficient Lookup, Regex in Loop)
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.detectors import PythonViolationDetector

class TestAdvancedRules:
    def test_deep_recursion_detection(self):
        code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'deep_recursion':
                found = True
                assert v['severity'] == 'major'
                break
        assert found, "Deep recursion not detected"

    def test_inefficient_lookup_detection(self):
        code = """
def process(items):
    check_list = [1, 2, 3]
    for item in items:
        if item in check_list:
            pass
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'inefficient_lookup':
                found = True
                assert 'consider converting to a set' in v['message'].lower()
                break
        assert found, "Inefficient lookup not detected"

    def test_regex_in_loop_detection(self):
        code = """
import re
def process(items):
    for item in items:
        p = re.compile(r'\d+')
        p.match(item)
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'unnecessary_computation' and 're.compile' in v['message']:
                found = True
                break
        assert found, "Regex in loop not detected"

    def test_efficient_lookup_suppression(self):
        code = """
def process(items):
    check_set = {1, 2, 3}
    for item in items:
        if item in check_set: # Should NOT be flagged
            pass
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'inefficient_lookup':
                found = True
                break
        assert not found, "Efficient lookup (set) incorrectly flagged"
