"""
Additional test coverage for analyzer and scanner modules
"""

import pytest
from src.core.analyzer import EmissionAnalyzer, ComplexityMetrics
from src.core.scanner import Scanner


class TestEmissionAnalyzer:
    def test_emission_analyzer_init(self):
        analyzer = EmissionAnalyzer()
        assert analyzer is not None
    
    def test_analyze_codebase_empty(self):
        analyzer = EmissionAnalyzer()
        codebase_emissions, per_file_emissions = analyzer.analyze_codebase({})
        assert codebase_emissions == 0.0
        assert per_file_emissions == {}
    
    def test_analyze_codebase_with_content(self):
        analyzer = EmissionAnalyzer()
        file_contents = {
            'test.py': 'x = 1\ny = 2\n',
            'test2.py': 'def foo():\n    pass\n'
        }
        codebase_emissions, per_file_emissions = analyzer.analyze_codebase(file_contents)
        assert codebase_emissions > 0.0
        assert 'test.py' in per_file_emissions
        assert 'test2.py' in per_file_emissions
    
    def test_get_per_line_emissions(self):
        analyzer = EmissionAnalyzer()
        issues = [
            {'id': 'inefficient_loop', 'line': 5, 'file': 'test.py'},
            {'id': 'unused_import', 'line': 2, 'file': 'test.py'}
        ]
        updated_issues = analyzer.get_per_line_emissions(issues, 0.0001)
        assert len(updated_issues) == 2
        assert 'codebase_emissions' in updated_issues[0]
    
    def test_complexity_metrics_dataclass(self):
        metrics = ComplexityMetrics(
            lines_of_code=100,
            cyclomatic_complexity=5,
            max_nesting_depth=2,
            function_count=3,
            class_count=1,
            recursive_functions=set(),
            memory_usage_estimate=50.0,
            loop_iterations_estimate=100,
            has_io_operations=False,
            has_expensive_operations=False
        )
        assert metrics.lines_of_code == 100
        assert metrics.cyclomatic_complexity == 5


class TestScannerAdvanced:
    def test_scanner_is_supported_file(self):
        scanner = Scanner(language='python')
        assert scanner._is_supported_file('test.py') is True
        assert scanner._is_supported_file('test.js') is False
        assert scanner._is_supported_file('test.txt') is False
    
    def test_scanner_javascript_support(self):
        scanner = Scanner(language='javascript')
        assert scanner._is_supported_file('test.js') is True
        assert scanner._is_supported_file('test.py') is False
    
    def test_scanner_get_files(self):
        scanner = Scanner()
        files = scanner._get_files('tests/')
        assert isinstance(files, list)
        assert len(files) > 0
        # Should find Python test files
        py_files = [f for f in files if f.endswith('.py')]
        assert len(py_files) > 0
    
    def test_scanner_get_run_command_unsupported(self):
        scanner = Scanner(language='ruby')
        cmd = scanner._get_run_command('test.rb')
        assert cmd is None
