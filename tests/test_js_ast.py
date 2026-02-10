import pytest
from src.core.detectors import detect_violations, JavaScriptASTDetector, HAS_TREE_SITTER

@pytest.mark.skipif(not HAS_TREE_SITTER, reason="Tree-sitter not available")
def test_excessive_logging():
    code = """
    console.log('debug');
    console.debug('more debug');
    console.warn('warning'); // Should not match
    """
    violations = detect_violations(code, 'test.js', language='javascript')

    log_violations = [v for v in violations if v['id'] == 'excessive_console_logging']
    assert len(log_violations) == 2
    # Lines might need adjustment depending on whitespace/parsing
    assert any(v['line'] == 2 for v in log_violations)
    assert any(v['line'] == 3 for v in log_violations)

@pytest.mark.skipif(not HAS_TREE_SITTER, reason="Tree-sitter not available")
def test_eval_usage():
    code = """
    const x = eval("2 + 2");
    """
    violations = detect_violations(code, 'test.js', language='javascript')

    eval_violations = [v for v in violations if v['id'] == 'eval_usage']
    assert len(eval_violations) == 1
    assert eval_violations[0]['line'] == 2

@pytest.mark.skipif(not HAS_TREE_SITTER, reason="Tree-sitter not available")
def test_magic_numbers():
    code = """
    const a = 123;
    const b = 1000; // Exempt
    const c = 99; // Exempt
    const d = 500.5;
    """
    violations = detect_violations(code, 'test.js', language='javascript')

    magic_violations = [v for v in violations if v['id'] == 'magic_numbers']
    assert len(magic_violations) >= 2 # Might catch more if regex also runs
    # Check specifically for values 123 and 500.5

    lines = [v['line'] for v in magic_violations]
    assert 2 in lines
    assert 5 in lines

@pytest.mark.skipif(not HAS_TREE_SITTER, reason="Tree-sitter not available")
def test_infinite_loops():
    code = """
    while (true) {
        console.log('loop');
    }
    """
    violations = detect_violations(code, 'test.js', language='javascript')

    loop_violations = [v for v in violations if v['id'] == 'no_infinite_loops']
    assert len(loop_violations) == 1
    assert loop_violations[0]['line'] == 2

@pytest.mark.skipif(not HAS_TREE_SITTER, reason="Tree-sitter not available")
def test_string_concatenation_in_loop():
    code = """
    let s = "";
    for (let i = 0; i < 10; i++) {
        s += "a";
    }

    while(condition) {
        s += "b";
    }

    s += "c"; // Not in loop
    """
    violations = detect_violations(code, 'test.js', language='javascript')

    concat_violations = [v for v in violations if v['id'] == 'string_concatenation']
    assert len(concat_violations) == 2
    lines = [v['line'] for v in concat_violations]
    assert 4 in lines
    assert 8 in lines
