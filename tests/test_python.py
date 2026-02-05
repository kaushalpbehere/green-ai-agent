"""
Test file for Python code analysis
"""

def test_python_file_exists():
    """Verify Python test files can be analyzed"""
    import os
    assert os.path.exists(__file__)