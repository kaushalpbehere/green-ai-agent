import pytest
from src.core.detectors import JavaScriptASTDetector

def test_excessive_console_logging():
    code = """
    function logSomething() {
        console.log("This is a log");
        console.debug("This is a debug");
        console.info("This is an info");
    }
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    log_violations = [v for v in violations if v['id'] == 'excessive_console_logging']
    assert len(log_violations) == 3
    # Check lines (Tree-sitter is 0-indexed for rows, but my code adds 1)
    # console.log is on line 3
    assert log_violations[0]['line'] == 3
    assert log_violations[1]['line'] == 4
    assert log_violations[2]['line'] == 5

def test_eval_usage():
    code = """
    const x = 10;
    eval("x + 1");
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    eval_violations = [v for v in violations if v['id'] == 'eval_usage']
    assert len(eval_violations) == 1
    assert eval_violations[0]['line'] == 3

def test_magic_numbers():
    code = """
    const a = 101;
    const b = 1000; // Allowed
    const c = 500;
    const d = 100; // Now disallowed (>= 100)
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    magic_violations = [v for v in violations if v['id'] == 'magic_numbers']
    assert len(magic_violations) == 3

    msgs = [v['message'] for v in magic_violations]
    assert any('101.0' in m for m in msgs)
    assert any('500.0' in m for m in msgs)
    assert any('100.0' in m for m in msgs)

def test_no_false_positives():
    code = """
    const logger = {
        log: function(msg) {}
    };
    logger.log("Not console");
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()
    assert len(violations) == 0
