import pytest
from src.core.ci.reporter import CIReporter

def test_generate_report_no_issues():
    reporter = CIReporter()
    report = reporter.generate_report({})
    assert "No Violations Found" in report

def test_generate_report_with_issues():
    reporter = CIReporter()
    scan_results = {
        'issues': [
            {'severity': 'critical', 'file': '/absolute/path/test.py', 'line': 10, 'message': 'test|message\nmsg', 'remediation': 'test|fix\nfix'},
            {'severity': 'medium', 'file': 'test.py', 'line': 10, 'message': 'test', 'remediation': 'test'},
            {'severity': 'info', 'file': 'test.py', 'line': 10, 'message': 'test', 'remediation': 'test'}
        ],
        'codebase_emissions': 1.23
    }
    report = reporter.generate_report(scan_results)
    assert "Found 3 violations" in report
    assert "CRITICAL" in report
    assert "test\\|message msg" in report
    assert "test\\|fix fix" in report
    assert "1.23" in report

def test_generate_report_diff_filtering():
    reporter = CIReporter()
    scan_results = {
        'issues': [
            {'severity': 'critical', 'file': 'test.py', 'line': 10, 'message': 'msg1', 'remediation': 'fix1'},
            {'severity': 'low', 'file': 'test.py', 'line': 20, 'message': 'msg2', 'remediation': 'fix2'},
            {'severity': 'high', 'file': '/absolute/other.py', 'line': 10, 'message': 'msg3', 'remediation': 'fix3'},
            {'severity': 'high', 'line': 10, 'message': 'msg4', 'remediation': 'fix4'}
        ]
    }
    diff_changes = {
        'test.py': {10, 15},
        'other.py': {10}
    }
    report = reporter.generate_report(scan_results, diff_changes)
    assert "Found 2 violations in changed files" in report
    assert "msg1" in report
    assert "msg2" not in report
    assert "msg3" in report
    assert "msg4" not in report
