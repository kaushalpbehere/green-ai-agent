import pytest
import ast
from src.core.detectors import detect_violations

class TestAdditionalRules:

    def test_eager_logging_formatting(self):
        code = """
import logging
logger = logging.getLogger()
val = 1
logger.info(f"Value: {val}")
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "eager_logging_formatting" in ids

    def test_eager_logging_formatting_class_attr(self):
        code = """
class MyClass:
    def __init__(self):
        self.logger = logging.getLogger()
    def log(self):
        val = 1
        self.logger.info(f"Value: {val}")
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "eager_logging_formatting" in ids

    def test_mutable_default_argument(self):
        code = """
def foo(l=[]):
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "mutable_default_argument" in ids

    def test_mutable_default_argument_kw(self):
        code = """
def foo(*, l=[]):
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "mutable_default_argument" in ids

    def test_any_all_list_comprehension(self):
        code = """
l = [1, 2, 3]
if any([x > 0 for x in l]):
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "any_all_list_comprehension" in ids

    def test_bare_except(self):
        code = """
try:
    pass
except:
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "bare_except" in ids

    def test_unnecessary_generator_list(self):
        code = """
l = [1, 2, 3]
s = sum([x for x in l])
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "unnecessary_generator_list" in ids
