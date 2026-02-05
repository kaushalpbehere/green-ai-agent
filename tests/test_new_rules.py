import pytest
from src.core.detectors import detect_violations

class TestNewRules:
    
    def test_exceptions_in_loop(self):
        code = """
for i in range(10):
    try:
        print(i)
    except:
        pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "exceptions_in_loop" in ids

    def test_heavy_object_copy(self):
        code = """
import copy
x = [1, 2]
y = copy.deepcopy(x)
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "heavy_object_copy" in ids

    def test_process_spawning(self):
        code = """
import os
import subprocess
os.system('ls')
subprocess.run(['ls'])
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "process_spawning" in ids

    def test_inefficient_file_read(self):
        code = """
with open('file.txt') as f:
    lines = f.readlines()
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "inefficient_file_read" in ids

    def test_global_variable_mutation(self):
        code = """
x = 10
def func():
    global x
    x += 1
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "global_variable_mutation" in ids

    def test_pandas_iterrows(self):
        code = """
import pandas as pd
df = pd.DataFrame()
for index, row in df.iterrows():
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "pandas_iterrows" in ids

    def test_js_eval_usage(self):
        code = "eval('alert(1)');"
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "eval_usage" in ids

    def test_js_timeout_animation(self):
        code = "setInterval(draw, 1000);"
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "setInterval_animation" in ids

    def test_js_moment_deprecated(self):
        code = "import moment from 'moment';"
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "momentjs_deprecated" in ids

    def test_js_document_write(self):
        code = "document.write('hello');"
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "document_write" in ids

    def test_js_alert_usage(self):
        code = "window.alert('hello');"
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "alert_usage" in ids
