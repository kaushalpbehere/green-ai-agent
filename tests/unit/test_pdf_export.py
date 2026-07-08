"""
Tests for PDF export functionality.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.core.export.pdf_exporter import PDFExporter

class TestPDFExporter:

    @pytest.fixture
    def sample_results(self):
        return {
            'issues': [
                {
                    'id': 'io_in_loop',
                    'file': 'src/main.py',
                    'line': 10,
                    'severity': 'critical',
                    'message': 'IO inside loop',
                    'effort': 'medium',
                    'energy_factor': '100x'
                },
                {
                    'id': 'unused_variable',
                    'file': 'src/utils.py',
                    'line': 5,
                    'severity': 'low',
                    'message': 'Unused var',
                    'effort': 'trivial',
                    'energy_factor': '1x'
                }
            ],
            'codebase_emissions': 0.005,
            'scanning_emissions': 0.001,
            'per_file_emissions': {
                'src/main.py': 0.004,
                'src/utils.py': 0.001
            }
        }

    def test_pdf_export_success(self, sample_results, tmp_path):
        """Test PDF export logic with mocked WeasyPrint."""
        output_file = tmp_path / "report.pdf"
        exporter = PDFExporter(str(output_file))

        # Create a mock WeasyPrint module
        mock_weasyprint = MagicMock()
        mock_html_class = MagicMock()
        # Create a mock HTML instance
        mock_html_instance = MagicMock()
        # Ensure HTML() returns the mock instance
        mock_html_class.return_value = mock_html_instance

        # Attach HTML class to the mock module
        mock_weasyprint.HTML = mock_html_class

        # Patch sys.modules so 'import weasyprint' returns our mock
        with patch.dict(sys.modules, {'weasyprint': mock_weasyprint}):
            result_path = exporter.export(sample_results, "TestProject")

            assert result_path == str(output_file)

            # Verify HTML was instantiated
            mock_html_class.assert_called_once()
            call_args = mock_html_class.call_args
            # Verify arguments passed to HTML constructor
            # call_args could be positional or keyword depending on implementation
            # WeasyPrint HTML(string=...)
            if 'string' in call_args.kwargs:
                html_content = call_args.kwargs['string']
            elif len(call_args.args) > 0: # HTML(string)
                html_content = call_args.args[0]
            else:
                pytest.fail("HTML constructor called without string argument")

            # Check content for charts
            assert "Severity Distribution" in html_content
            assert "Top Violations by File" in html_content
            assert "<img" in html_content # Charts injected as images
            assert "data:image/png;base64," in html_content # Verify base64 PNG format

            # Verify write_pdf was called
            mock_html_instance.write_pdf.assert_called_once_with(str(output_file))

    def test_pdf_export_import_error(self, sample_results, tmp_path):
        """Test behavior when WeasyPrint is missing."""
        output_file = tmp_path / "report.pdf"
        exporter = PDFExporter(str(output_file))

        # Simulate missing module by setting it to None in sys.modules
        with patch.dict(sys.modules, {'weasyprint': None}):
             result_path = exporter.export(sample_results, "TestProject")
             assert result_path == ""
