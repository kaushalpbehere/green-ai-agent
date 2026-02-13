"""
Tests for Export API Endpoints
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ui.dashboard_app import app

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestExportAPI:
    """Test export API endpoints"""

    def test_api_export_csv_no_results(self, client):
        """Test CSV export when no results are available"""
        with patch('src.ui.dashboard_app.last_scan_results', None):
            response = client.get('/api/export/csv')
            assert response.status_code == 400
            assert b'No scan results available' in response.data

    def test_api_export_html_no_results(self, client):
        """Test HTML export when no results are available"""
        with patch('src.ui.dashboard_app.last_scan_results', None):
            response = client.get('/api/export/html')
            assert response.status_code == 400
            assert b'No scan results available' in response.data

    def test_api_export_csv_success(self, client):
        """Test successful CSV export"""
        mock_results = {'issues': []}

        with patch('src.ui.dashboard_app.last_scan_results', mock_results), \
             patch('src.core.export.CSVExporter') as MockExporter, \
             patch('src.ui.dashboard_app.open', new_callable=MagicMock) as mock_open_file:

            # Mock file reading
            mock_file_handle = MagicMock()
            mock_file_handle.read.return_value = 'header1,header2\nval1,val2'
            mock_open_file.return_value.__enter__.return_value = mock_file_handle

            # Mock Path logic
            with patch('pathlib.Path') as MockPath:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True
                mock_path_instance.name = 'green-ai-report-TestProject.csv'

                # Mock the chain: Path(__file__).parent.parent.parent / 'output' / filename
                # Output dir
                mock_output_dir = MagicMock()
                MockPath.return_value.parent.parent.parent.__truediv__.return_value = mock_output_dir
                # Output path
                mock_output_dir.__truediv__.return_value = mock_path_instance

                response = client.get('/api/export/csv?project=TestProject')

                assert response.status_code == 200
                assert response.content_type == 'text/csv; charset=utf-8'
                # Check filename in content disposition
                assert 'filename="green-ai-report-TestProject.csv"' in response.headers['Content-Disposition']

                # Verify cleanup
                mock_path_instance.unlink.assert_called()

    def test_api_export_html_success(self, client):
        """Test successful HTML export"""
        mock_results = {'issues': []}

        with patch('src.ui.dashboard_app.last_scan_results', mock_results), \
             patch('src.core.export.HTMLReporter') as MockReporter, \
             patch('src.ui.dashboard_app.open', new_callable=MagicMock) as mock_open_file:

            # Mock file reading
            mock_file_handle = MagicMock()
            mock_file_handle.read.return_value = '<html>Content</html>'
            mock_open_file.return_value.__enter__.return_value = mock_file_handle

            # Mock Path logic
            with patch('pathlib.Path') as MockPath:
                mock_path_instance = MagicMock()
                mock_path_instance.exists.return_value = True

                # Mock the chain
                mock_output_dir = MagicMock()
                MockPath.return_value.parent.parent.parent.__truediv__.return_value = mock_output_dir
                mock_output_dir.__truediv__.return_value = mock_path_instance

                response = client.get('/api/export/html?project=TestProject')

                assert response.status_code == 200
                assert response.content_type == 'text/html; charset=utf-8'

                # Verify cleanup
                mock_path_instance.unlink.assert_called()
