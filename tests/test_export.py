"""
Unit tests for export module (CSV and HTML export functionality)
"""

import pytest
import os
import csv
import tempfile
from src.core.export import CSVExporter, HTMLReporter


class TestCSVExporter:
    """Test CSV export functionality."""
    
    @pytest.fixture
    def sample_results(self):
        """Create sample scan results for testing."""
        return {
            'issues': [
                {
                    'id': 'excessive_nesting_depth',
                    'line': 12,
                    'severity': 'critical',
                    'message': '3-level nested loop detected',
                    'file': 'app.py',
                    'energy_factor': '100x',
                    'effort': 'high'
                },
                {
                    'id': 'io_in_loop',
                    'line': 45,
                    'severity': 'critical',
                    'message': 'File read in loop',
                    'file': 'app.py',
                    'energy_factor': '1000x',
                    'effort': 'high'
                },
                {
                    'id': 'blocking_io',
                    'line': 88,
                    'severity': 'high',
                    'message': 'Blocking I/O operation',
                    'file': 'utils.py',
                    'energy_factor': '100x',
                    'effort': 'medium'
                },
                {
                    'id': 'unused_variable',
                    'line': 120,
                    'severity': 'medium',
                    'message': 'Variable not used',
                    'file': 'utils.py',
                    'energy_factor': '1x',
                    'effort': 'easy'
                }
            ],
            'codebase_emissions': 0.000001234,
            'scanning_emissions': 0.000000567,
            'per_file_emissions': {
                'app.py': 0.000001,
                'utils.py': 0.0000002
            }
        }
    
    def test_csv_export_creates_file(self, sample_results):
        """Test that CSV export creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.csv')
            exporter = CSVExporter(output_path)
            result = exporter.export(sample_results)
            
            assert os.path.exists(result)
            assert result == output_path
    
    def test_csv_export_default_filename(self, sample_results):
        """Test CSV export with default filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'green-ai-report.csv')
            exporter = CSVExporter()  # Uses default
            # Manually set path for testing
            exporter.output_path = output_path
            result = exporter.export(sample_results)
            
            assert os.path.exists(output_path)
    
    def test_csv_export_format(self, sample_results):
        """Test that CSV export has correct format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.csv')
            exporter = CSVExporter(output_path)
            exporter.export(sample_results)
            
            # Read and verify CSV
            with open(output_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Should have issues + summary row
            assert len(rows) == 5  # 4 issues + 1 summary
            
            # Check header
            with open(output_path, 'r') as f:
                header = f.readline().strip()
                expected_fields = ['file', 'line', 'rule_id', 'severity', 'message', 'energy_factor', 'effort']
                assert all(field in header for field in expected_fields)
    
    def test_csv_export_severity_sorting(self, sample_results):
        """Test that issues are sorted by severity (critical first)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.csv')
            exporter = CSVExporter(output_path)
            exporter.export(sample_results)
            
            with open(output_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # First two should be critical (excluding summary)
            assert rows[0]['severity'] == 'critical'
            assert rows[1]['severity'] == 'critical'
            assert rows[2]['severity'] == 'high'
            assert rows[3]['severity'] == 'medium'
    
    def test_csv_export_summary_row(self, sample_results):
        """Test that summary row is added correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.csv')
            exporter = CSVExporter(output_path)
            exporter.export(sample_results)
            
            with open(output_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            summary = rows[-1]  # Last row
            assert summary['file'] == 'SUMMARY'
            assert 'Total Violations: 4' in summary['message']
            assert 'Critical: 2' in summary['message']
            assert 'High: 1' in summary['message']
            assert 'Medium: 1' in summary['message']
    
    def test_get_statistics(self, sample_results):
        """Test statistics calculation."""
        exporter = CSVExporter()
        stats = exporter.get_statistics(sample_results)
        
        assert stats['total_violations'] == 4
        assert stats['severity_counts']['critical'] == 2
        assert stats['severity_counts']['high'] == 1
        assert stats['severity_counts']['medium'] == 1
        assert stats['severity_counts']['low'] == 0
        assert stats['affected_files'] == 2
        assert stats['codebase_emissions'] == 0.000001234
    
    def test_csv_export_empty_results(self):
        """Test CSV export with no violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.csv')
            exporter = CSVExporter(output_path)
            
            results = {
                'issues': [],
                'codebase_emissions': 0,
                'scanning_emissions': 0,
                'per_file_emissions': {}
            }
            
            result = exporter.export(results)
            assert os.path.exists(result)
            
            # Should still have header and summary
            with open(output_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 1  # Only summary row
            assert rows[0]['file'] == 'SUMMARY'
    
    def test_energy_factor_inference(self):
        """Test energy factor inference for missing values."""
        exporter = CSVExporter()
        
        # Critical issue without explicit energy_factor
        issue_critical = {
            'id': 'test_rule',
            'severity': 'critical',
            'line': 10
        }
        assert exporter._get_energy_factor(issue_critical) == '100x'
        
        # High severity
        issue_high = {
            'id': 'test_rule',
            'severity': 'high'
        }
        assert exporter._get_energy_factor(issue_high) == '10x'
        
        # IO in loop specific
        issue_io = {
            'id': 'io_in_loop',
            'severity': 'low'
        }
        assert exporter._get_energy_factor(issue_io) == '1000x'


class TestHTMLReporter:
    """Test HTML report generation."""
    
    @pytest.fixture
    def sample_results(self):
        """Create sample scan results for testing."""
        return {
            'issues': [
                {
                    'id': 'excessive_nesting_depth',
                    'line': 12,
                    'severity': 'critical',
                    'message': '3-level nested loop detected',
                    'file': 'app.py'
                },
                {
                    'id': 'blocking_io',
                    'line': 88,
                    'severity': 'high',
                    'message': 'Blocking I/O operation',
                    'file': 'utils.py'
                }
            ],
            'codebase_emissions': 0.000001234,
            'scanning_emissions': 0.000000567,
            'per_file_emissions': {
                'app.py': 0.000001,
                'utils.py': 0.0000002
            }
        }
    
    def test_html_export_creates_file(self, sample_results):
        """Test that HTML export creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.html')
            reporter = HTMLReporter(output_path)
            result = reporter.export(sample_results)
            
            assert os.path.exists(result)
            assert result == output_path
    
    def test_html_export_default_filename(self, sample_results):
        """Test HTML export with default filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'green-ai-report.html')
            reporter = HTMLReporter()  # Uses default
            # Manually set path for testing
            reporter.output_path = output_path
            result = reporter.export(sample_results)
            
            assert os.path.exists(output_path)
    
    def test_html_export_contains_key_elements(self, sample_results):
        """Test that HTML contains expected elements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.html')
            reporter = HTMLReporter(output_path)
            reporter.export(sample_results, project_name='TestProject')
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key HTML elements
            assert '<html' in content.lower()
            assert 'Green-AI Report' in content
            assert 'TestProject' in content
            assert 'app.py' in content
            assert 'utils.py' in content
            assert 'excessive_nesting_depth' in content
            assert 'blocking_io' in content
            assert '<canvas' in content  # Charts
    
    def test_html_export_statistics_display(self, sample_results):
        """Test that HTML displays statistics correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.html')
            reporter = HTMLReporter(output_path)
            reporter.export(sample_results)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for metric displays
            assert 'Total Violations' in content
            assert '2' in content  # 2 violations
            assert 'Critical Issues' in content
            assert '1' in content  # 1 critical
            assert 'Affected Files' in content
            assert 'CO₂' in content or 'CO2' in content
    
    def test_html_export_emissions_section(self, sample_results):
        """Test that HTML includes emissions data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.html')
            reporter = HTMLReporter(output_path)
            reporter.export(sample_results)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for emissions section
            assert 'Energy Impact' in content
            assert 'Codebase Emissions' in content
            assert 'Scanning Process Emissions' in content
    
    def test_html_export_empty_results(self):
        """Test HTML export with no violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'test_report.html')
            reporter = HTMLReporter(output_path)
            
            results = {
                'issues': [],
                'codebase_emissions': 0,
                'scanning_emissions': 0,
                'per_file_emissions': {}
            }
            
            result = reporter.export(results)
            assert os.path.exists(result)
            
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'Green-AI Report' in content
            assert '<html' in content.lower()
    
    def test_get_color_for_severity(self):
        """Test severity color mapping."""
        assert HTMLReporter._get_color_for_severity('critical') == '#ef4444'
        assert HTMLReporter._get_color_for_severity('high') == '#f97316'
        assert HTMLReporter._get_color_for_severity('medium') == '#eab308'
        assert HTMLReporter._get_color_for_severity('low') == '#3b82f6'
        assert HTMLReporter._get_color_for_severity('info') == '#8b5cf6'
        assert HTMLReporter._get_color_for_severity('unknown') == '#6b7280'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
