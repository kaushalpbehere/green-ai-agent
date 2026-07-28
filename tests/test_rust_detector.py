import pytest
from src.core.detectors.rust_detector import RustASTDetector
from src.core.detectors import detect_violations

def test_rust_detector():
    code = """
fn main() {
    let mut s = String::new();
    for i in 0..10 {
        s += "a";
        s = s + "b";
    }

    loop {
        println!("infinite!");
    }

    {}
}
    """
    violations = detect_violations(code, "test.rs", language="rust")
    assert len(violations) > 0
    ids = [v["id"] for v in violations]
    assert "rust_formatted_print" in ids
    assert "rust_empty_block" in ids
    assert "rust_infinite_loop" in ids
    assert "rust_string_concatenation_in_loop" in ids
