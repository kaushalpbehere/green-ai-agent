"""
Unit tests for PythonViolationDetector visitors
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.detectors import PythonViolationDetector

class TestPythonVisitors:
    def _get_violations(self, code):
        detector = PythonViolationDetector(code, "test_file.py")
        return detector.detect_all()

    def test_visit_For_nested_loops(self):
        code = """
def nested_loops():
    for i in range(10):
        for j in range(10):
            pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'no_n2_algorithms' and v['severity'] == 'major' for v in violations)

    def test_visit_For_triple_nested_loops(self):
        code = """
def triple_nested_loops():
    for i in range(10):
        for j in range(10):
            for k in range(10):
                pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'no_n2_algorithms' and v['severity'] == 'critical' for v in violations)

    def test_visit_For_range_len_inefficiency(self):
        code = """
def inefficient_loop(items):
    for i in range(len(items)):
        print(items[i])
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'inefficient_loop' for v in violations)

    def test_visit_For_keys_iteration(self):
        code = """
def keys_iteration(d):
    for key in d.keys():
        print(key)
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'inefficient_dictionary_iteration' for v in violations)

    def test_visit_While_infinite_loop(self):
        code = """
def infinite_loop():
    while True:
        pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'no_infinite_loops' for v in violations)

    def test_visit_While_nested_loop(self):
        code = """
def nested_while():
    while True:
        while True:
            while True:
                break
            break
        break
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'excessive_nesting_depth' for v in violations)

    def test_visit_FunctionDef_mutable_default(self):
        code = """
def mutable_default(x=[]):
    x.append(1)
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'mutable_default_argument' for v in violations)

    def test_visit_FunctionDef_complexity(self):
        # Create a function with high complexity > 10
        code = """
def complex_function(x):
    if x == 1: pass
    elif x == 2: pass
    elif x == 3: pass
    elif x == 4: pass
    elif x == 5: pass
    elif x == 6: pass
    elif x == 7: pass
    elif x == 8: pass
    elif x == 9: pass
    elif x == 10: pass
    elif x == 11: pass
"""
        violations = self._get_violations(code)
        # Complexity starts at 1, +11 ifs = 12. Should trigger.
        assert any(v['id'] == 'high_cyclomatic_complexity' for v in violations)

    def test_visit_Call_blocking_io(self):
        code = """
import time
def blocking_io():
    time.sleep(1)
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'blocking_io' for v in violations)

    def test_visit_Call_open_without_context(self):
        code = """
def open_file():
    f = open('file.txt', 'r')
    content = f.read()
    f.close()
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'proper_resource_cleanup' for v in violations)

    def test_visit_Call_print(self):
        code = """
def print_stuff():
    print("hello")
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'excessive_logging' and 'print' in v['message'] for v in violations)

    def test_visit_Call_list_comp_any(self):
        code = """
def list_comp_any(items):
    if any([x > 0 for x in items]):
        pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'any_all_list_comprehension' for v in violations)

    def test_visit_Try_in_loop(self):
        code = """
def try_in_loop(items):
    for item in items:
        try:
            print(item)
        except:
            pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'exceptions_in_loop' for v in violations)

    def test_visit_Global(self):
        code = """
x = 0
def global_usage():
    global x
    x += 1
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'global_variable_mutation' for v in violations)

    def test_visit_AugAssign_string_concat_loop(self):
        code = """
def string_concat(items):
    s = ""
    for item in items:
        s += item
"""
        violations = self._get_violations(code)
        # Assuming type inference might fail if not explicit, but here s="" sets var_types['s'] = 'str'
        assert any(v['id'] == 'string_concatenation_in_loop' for v in violations)

    def test_visit_Call_process_spawning(self):
        code = """
import subprocess
def spawn_process():
    subprocess.run(['ls'])
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'process_spawning' for v in violations)

    def test_visit_Call_readlines(self):
        code = """
def read_lines():
    with open('file.txt') as f:
        lines = f.readlines()
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'inefficient_file_read' for v in violations)

    def test_visit_Call_pandas_iterrows(self):
        code = """
import pandas as pd
def iterate_df(df):
    for index, row in df.iterrows():
        pass
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'pandas_iterrows' for v in violations)

    def test_visit_Call_deepcopy(self):
        code = """
import copy
def copy_obj(x):
    y = copy.deepcopy(x)
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'heavy_object_copy' for v in violations)

    def test_visit_Call_eager_logging(self):
        code = """
import logging
logger = logging.getLogger()
def log_something(val):
    logger.info(f"Value is {val}")
"""
        violations = self._get_violations(code)
        assert any(v['id'] == 'eager_logging_formatting' for v in violations)
