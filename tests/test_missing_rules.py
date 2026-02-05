
import pytest
from src.core.detectors import detect_violations

class TestMissingRules:
    
    # Python Tests
    def test_py_infinite_loop(self):
        code = """
while True:
    pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "no_infinite_loops" in ids

    def test_py_inefficient_loop(self):
        code = "for i in range(len(mylist)):\n    print(i)"
        violations = detect_violations(code, "test.py", "python")
        assert any(v['id'] == 'inefficient_loop' for v in violations)

    def test_py_excessive_logging(self):
        code = "print('debug')\nlogger.info('status')"
        violations = detect_violations(code, "test.py", "python")
        assert any(v['id'] == 'excessive_logging' for v in violations)
        # Check count if needed, but simple existence check is enough for now

    def test_py_magic_numbers(self):
        code = """
x = 1234
y = x + 500
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "magic_numbers" in ids

    def test_py_n2_algorithms(self):
        code = """
for i in range(10):
    for j in range(10):
        pass
"""
        violations = detect_violations(code, "test.py", language="python")
        ids = [v['id'] for v in violations]
        assert "no_n2_algorithms" in ids

    def test_py_n3_algorithms(self):
        code = """
for i in range(10):
    for j in range(10):
        for k in range(10):
            pass
"""
        violations = detect_violations(code, "test.py", language="python")
        # Should be critical or show n2 algorithms violation as well
        ids = [v['id'] for v in violations]
        assert "no_n2_algorithms" in ids 

    # JavaScript Tests
    def test_js_infinite_loop(self):
        code = """
while(true) {
    doSomething();
}
"""
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "no_infinite_loops" in ids

    def test_js_inefficient_loop(self):
        code = """
for (let i = 0; i < 10; i++) {
    console.log(i);
}
"""
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "inefficient_loop" in ids

    def test_js_sync_io(self):
        code = """
const fs = require('fs');
const data = fs.readFileSync('file.txt');
"""
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "synchronous_io" in ids

    def test_js_excessive_console(self):
        code = """
console.log("debug");
console.debug("info");
"""
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "excessive_console_logging" in ids

    def test_js_magic_numbers(self):
        code = """
let x = 9999 ;
"""
        violations = detect_violations(code, "test.js", language="javascript")
        ids = [v['id'] for v in violations]
        assert "magic_numbers" in ids

    def test_js_unused_variable(self):
        code = "let varUnused = 10; let varUsed = 20; console.log(varUsed);"
        violations = detect_violations(code, "test.js", "javascript")
        assert any(v['id'] == 'unused_variables' for v in violations)
        
        unused_msgs = [v['message'] for v in violations if v['id'] == 'unused_variables']
        assert any("varUnused" in m for m in unused_msgs)
        assert not any("varUsed" in m for m in unused_msgs)

    def test_js_string_concatenation(self):
        code = "let s = ''; for(let i=0; i<10; i++) { s += 'a'; }"
        violations = detect_violations(code, "test.js", "javascript")
        assert any(v['id'] == 'string_concatenation' for v in violations)

    def test_js_dom_manipulation(self):
        code = "const el = document.querySelector('.my-el');"
        violations = detect_violations(code, "test.js", "javascript")
        assert any(v['id'] == 'unnecessary_dom_manipulation' for v in violations)
