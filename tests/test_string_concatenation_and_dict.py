
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.detectors import PythonViolationDetector

class TestStringConcatenationAndDict:
    def test_string_concatenation_loop_plus(self):
        code = """
def process(items):
    s = ""
    for item in items:
        s = s + item
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'string_concatenation_in_loop':
                found = True
                assert v['severity'] == 'medium'
                break
        assert found, "String concatenation (+) not detected"

    def test_string_concatenation_loop_aug_assign(self):
        code = """
def process(items):
    s = ""
    for item in items:
        s += item
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'string_concatenation_in_loop':
                found = True
                break
        assert found, "String concatenation (+=) not detected"

    def test_string_concatenation_loop_no_string(self):
        code = """
def process(items):
    s = 0
    for item in items:
        s += 1
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'string_concatenation_in_loop':
                found = True
                break
        assert not found, "Integer addition (+=) incorrectly flagged as string concatenation"

    def test_inefficient_dictionary_iteration(self):
        code = """
def process(data):
    for key in data.keys():
        pass
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'inefficient_dictionary_iteration':
                found = True
                break
        assert found, "Inefficient dictionary iteration (.keys()) not detected"

    def test_efficient_dictionary_iteration(self):
        code = """
def process(data):
    for key in data:
        pass
    for key, val in data.items():
        pass
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'inefficient_dictionary_iteration':
                found = True
                break
        assert not found, "Efficient dictionary iteration flagged incorrectly"

    def test_string_concatenation_complex(self):
        code = """
def process(items):
    s = "start"
    for item in items:
        s = s + "separator" + item
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'string_concatenation_in_loop':
                found = True
                break
        assert found, "Complex string concatenation not detected"

    def test_string_concatenation_loop_no_accumulation(self):
        code = """
def process(items):
    for item in items:
        x = "a" + "b"
        print(x)
"""
        detector = PythonViolationDetector(code, "test_file.py")
        violations = detector.detect_all()

        found = False
        for v in violations:
            if v['id'] == 'string_concatenation_in_loop':
                found = True
                break
        assert not found, "Non-accumulating string concatenation flagged incorrectly"
