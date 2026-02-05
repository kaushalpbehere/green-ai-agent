"""
Tests for dashboard chart data generation.
Verify that chart data is correctly computed from scan results.
"""

import pytest
from src.ui.charts import ChartDataGenerator, generate_all_charts


class TestSeverityChart:
    """Test violations by severity chart data generation."""
    
    def test_empty_issues(self):
        """Empty issues should produce zero counts"""
        chart = ChartDataGenerator.violations_by_severity([])
        assert chart['total'] == 0
        assert sum(chart['data']) == 0
        
    def test_single_high_severity(self):
        """Single high-severity issue should be counted"""
        issues = [{'severity': 'high', 'id': 'TEST_001'}]
        chart = ChartDataGenerator.violations_by_severity(issues)
        assert chart['total'] == 1
        assert 'High' in chart['labels']
        
    def test_mixed_severities(self):
        """Multiple severities should be counted correctly"""
        issues = [
            {'severity': 'high'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'},
            {'severity': 'low'},
        ]
        chart = ChartDataGenerator.violations_by_severity(issues)
        assert chart['total'] == 5
        assert sum(chart['data']) == 5
        # Check percentages sum to 100
        assert abs(sum(chart['percentages']) - 100.0) < 0.1
        
    def test_case_insensitive_severity(self):
        """Severity should be case-insensitive"""
        issues = [
            {'severity': 'HIGH'},
            {'severity': 'medium'},
            {'severity': 'LOW'},
        ]
        chart = ChartDataGenerator.violations_by_severity(issues)
        assert chart['total'] == 3


class TestViolationsByType:
    """Test violations by type chart data generation."""
    
    def test_empty_issues(self):
        """Empty issues should produce empty chart"""
        chart = ChartDataGenerator.violations_by_type([])
        assert chart['total'] == 0
        
    def test_issue_type_categorization(self):
        """Issues should be categorized by type"""
        issues = [
            {'type': 'green_violation', 'id': 'MEMORY_LEAK'},
            {'type': 'green_violation', 'id': 'CPU_INTENSIVE'},
            {'type': 'green_violation', 'id': 'IO_OPERATION'},
        ]
        chart = ChartDataGenerator.violations_by_type(issues)
        assert chart['total'] == 3
        assert 'Memory' in chart['labels']
        assert 'CPU' in chart['labels']
        assert 'I/O' in chart['labels']
        
    def test_percentages_sum_to_100(self):
        """Percentages should sum to approximately 100"""
        issues = [
            {'type': 'green_violation', 'id': 'MEMORY_LEAK'},
            {'type': 'green_violation', 'id': 'CPU_INTENSIVE'},
            {'type': 'green_violation', 'id': 'IO_OPERATION'},
            {'type': 'green_violation', 'id': 'NETWORK_CALL'},
            {'type': 'green_violation', 'id': 'ENERGY_WASTE'},
        ]
        chart = ChartDataGenerator.violations_by_type(issues)
        assert abs(sum(chart['percentages']) - 100.0) < 0.1


class TestViolationsByFile:
    """Test violations by file chart data generation."""
    
    def test_empty_issues(self):
        """Empty issues should produce empty chart"""
        chart = ChartDataGenerator.violations_by_file([])
        assert chart['total'] == 0
        assert len(chart['labels']) == 0
        
    def test_single_file(self):
        """Single file with multiple issues should be counted"""
        issues = [
            {'file': 'main.py', 'codebase_emissions': 0.00001},
            {'file': 'main.py', 'codebase_emissions': 0.00002},
            {'file': 'main.py', 'codebase_emissions': 0.00003},
        ]
        chart = ChartDataGenerator.violations_by_file(issues)
        assert chart['total'] == 3
        assert 'main.py' in chart['labels']
        assert chart['data'][0] == 3
        
    def test_multiple_files_sorted(self):
        """Files should be sorted by violation count"""
        issues = [
            {'file': 'file1.py', 'codebase_emissions': 0.00001},
            {'file': 'file2.py', 'codebase_emissions': 0.00001},
            {'file': 'file2.py', 'codebase_emissions': 0.00001},
            {'file': 'file3.py', 'codebase_emissions': 0.00001},
            {'file': 'file3.py', 'codebase_emissions': 0.00001},
            {'file': 'file3.py', 'codebase_emissions': 0.00001},
        ]
        chart = ChartDataGenerator.violations_by_file(issues)
        assert chart['total'] == 6
        assert chart['labels'][0] == 'file3.py'  # Most violations
        assert chart['data'][0] == 3
        
    def test_max_10_files(self):
        """Should limit to top 10 files"""
        issues = [
            {'file': f'file{i}.py', 'codebase_emissions': 0.00001}
            for i in range(15)
        ]
        chart = ChartDataGenerator.violations_by_file(issues)
        assert len(chart['labels']) <= 10


class TestTopViolations:
    """Test top violations by emissions impact."""
    
    def test_empty_issues(self):
        """Empty issues should produce empty list"""
        top = ChartDataGenerator.top_violations([])
        assert len(top) == 0
        
    def test_sorted_by_emissions(self):
        """Violations should be sorted by emissions descending"""
        issues = [
            {'id': 'A', 'codebase_emissions': 0.00001, 'severity': 'low'},
            {'id': 'B', 'codebase_emissions': 0.00005, 'severity': 'high'},
            {'id': 'C', 'codebase_emissions': 0.00003, 'severity': 'medium'},
        ]
        top = ChartDataGenerator.top_violations(issues)
        assert top[0]['id'] == 'B'  # Highest emissions
        assert top[1]['id'] == 'C'
        assert top[2]['id'] == 'A'
        
    def test_limit_to_10(self):
        """Should limit to top 10 violations"""
        issues = [
            {'id': f'RULE_{i}', 'codebase_emissions': float(i), 'severity': 'high'}
            for i in range(15)
        ]
        top = ChartDataGenerator.top_violations(issues, limit=10)
        assert len(top) == 10
        assert top[0]['id'] == 'RULE_14'  # Highest first


class TestEmissionsTrend:
    """Test emissions by file trend chart."""
    
    def test_empty_emissions(self):
        """Empty per-file emissions should produce empty chart"""
        chart = ChartDataGenerator.emissions_trend({})
        assert chart['total'] == 0.0
        assert chart['average'] == 0.0
        assert len(chart['labels']) == 0
        
    def test_single_file(self):
        """Single file emissions should be calculated"""
        per_file = {'main.py': 0.00001}
        chart = ChartDataGenerator.emissions_trend(per_file)
        assert chart['total'] == 0.00001
        assert chart['average'] == 0.00001
        assert chart['labels'][0] == 'main.py'
        
    def test_multiple_files(self):
        """Multiple files should be calculated and averaged"""
        per_file = {
            'file1.py': 0.00001,
            'file2.py': 0.00002,
            'file3.py': 0.00003,
        }
        chart = ChartDataGenerator.emissions_trend(per_file)
        assert chart['total'] == 0.00006
        assert chart['average'] == 0.00002
        
    def test_max_10_files(self):
        """Should limit to top 10 files"""
        per_file = {f'file{i}.py': float(i) for i in range(15)}
        chart = ChartDataGenerator.emissions_trend(per_file)
        assert len(chart['labels']) <= 10


class TestSummaryMetrics:
    """Test summary metrics generation."""
    
    def test_empty_results(self):
        """Empty results should produce zero metrics"""
        metrics = ChartDataGenerator.summary_metrics({
            'issues': [],
            'scanning_emissions': 0.0,
            'codebase_emissions': 0.0,
            'per_file_emissions': {}
        })
        assert metrics['total_issues'] == 0
        assert metrics['critical_issues'] == 0
        assert metrics['total_emissions'] == 0.0
        
    def test_issue_severity_counts(self):
        """Should count issues by severity correctly"""
        results = {
            'issues': [
                {'severity': 'high', 'codebase_emissions': 0.00001},
                {'severity': 'high', 'codebase_emissions': 0.00001},
                {'severity': 'medium', 'codebase_emissions': 0.00001},
                {'severity': 'low', 'codebase_emissions': 0.00001},
            ],
            'scanning_emissions': 0.0,
            'codebase_emissions': 0.00004,
            'per_file_emissions': {}
        }
        metrics = ChartDataGenerator.summary_metrics(results)
        assert metrics['total_issues'] == 4
        assert metrics['critical_issues'] == 2
        assert metrics['medium_issues'] == 1
        assert metrics['low_issues'] == 1
        
    def test_emissions_totals(self):
        """Should calculate emission totals correctly"""
        results = {
            'issues': [],
            'scanning_emissions': 0.00001,
            'codebase_emissions': 0.00009,
            'per_file_emissions': {}
        }
        metrics = ChartDataGenerator.summary_metrics(results)
        assert metrics['scanning_emissions'] == 0.00001
        assert metrics['codebase_emissions'] == 0.00009
        assert metrics['total_emissions'] == 0.0001
        
    def test_average_issue_emissions(self):
        """Should calculate average emissions per issue"""
        results = {
            'issues': [
                {'codebase_emissions': 0.00002},
                {'codebase_emissions': 0.00004},
                {'codebase_emissions': 0.00004},
            ],
            'scanning_emissions': 0.0,
            'codebase_emissions': 0.0001,
            'per_file_emissions': {}
        }
        metrics = ChartDataGenerator.summary_metrics(results)
        assert metrics['total_issues'] == 3
        # Average: (0.00002 + 0.00004 + 0.00004) / 3 = 0.00003333...
        assert abs(metrics['avg_issue_emissions'] - 0.000033) < 0.000001


class TestGenerateAllCharts:
    """Test complete chart generation."""
    
    def test_generate_all_charts(self):
        """Should generate all chart types"""
        results = {
            'issues': [
                {
                    'id': 'RULE_001',
                    'severity': 'high',
                    'type': 'green_violation',
                    'file': 'main.py',
                    'line': 10,
                    'message': 'Test issue',
                    'codebase_emissions': 0.00001,
                    'effort': 'easy'
                },
            ],
            'scanning_emissions': 0.000001,
            'codebase_emissions': 0.00001,
            'per_file_emissions': {'main.py': 0.00001}
        }
        
        charts = generate_all_charts(results)
        
        assert 'severity_chart' in charts
        assert 'type_chart' in charts
        assert 'file_chart' in charts
        assert 'top_violations' in charts
        assert 'emissions_trend' in charts
        assert 'summary_metrics' in charts
        
        assert charts['severity_chart']['total'] == 1
        assert charts['summary_metrics']['total_issues'] == 1
        assert len(charts['top_violations']) == 1
