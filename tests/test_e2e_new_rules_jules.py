"""
E2E tests for New Rules (Inefficient Dictionary Iteration, String Concatenation)
"""
import pytest
from src.core.scanner import Scanner

def test_e2e_new_rules_jules(tmp_path):
    repro_content = """
# 1. Inefficient Dictionary Iteration
def process_dict(data):
    for key in data.keys():
        print(key)

# 2. String Concatenation in Loop
def concat_string(items):
    s = ""
    for item in items:
        s += item
"""
    repro_file = tmp_path / 'temp_repro_new_rules.py'
    repro_file.write_text(repro_content, encoding='utf-8')

    scanner = Scanner(language='python') # Explicitly set language
    results = scanner.scan(str(repro_file))

    assert 'issues' in results
    issues = results['issues']

    found_dict_iter = False
    found_string_concat = False

    for issue in issues:
        if issue['id'] == 'inefficient_dictionary_iteration':
            found_dict_iter = True
        elif issue['id'] == 'string_concatenation_in_loop':
            found_string_concat = True

    assert found_dict_iter, "Inefficient dictionary iteration not detected in E2E test"
    assert found_string_concat, "String concatenation in loop not detected in E2E test"
