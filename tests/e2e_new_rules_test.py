import os
import pytest
import sys
# Add src to path if needed, though pytest usually handles it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.scanner import Scanner

def test_e2e_new_rules():
    test_file = "tests/temp_violations.py"
    with open(test_file, "w") as f:
        f.write("""
import logging
logger = logging.getLogger()
val = 1
logger.info(f"Test {val}")

def foo(l=[]):
    pass

l = [1, 2]
if any([x > 0 for x in l]):
    pass

try:
    pass
except:
    pass

s = sum([x for x in l])
""")

    try:
        scanner = Scanner(language="python")
        results = scanner.scan(test_file)

        issues = results.get('issues', [])
        ids = [i['id'] for i in issues]

        assert "eager_logging_formatting" in ids
        assert "mutable_default_argument" in ids
        assert "any_all_list_comprehension" in ids
        assert "bare_except" in ids
        assert "unnecessary_generator_list" in ids

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
