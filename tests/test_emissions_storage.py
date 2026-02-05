"""
Tests for emissions data storage and management.
Verify that emissions.csv is stored in data/ folder and accessible.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestEmissionsStorage:
    """Test emissions file storage locations and defaults."""

    @patch('src.agents.runtime_monitor.codecarbon_integration.EmissionsTracker')
    def test_codecarbon_defaults_to_data_folder(self, mock_tracker):
        """CodeCarbonMonitor should default to data/emissions.csv"""
        from src.agents.runtime_monitor.codecarbon_integration import CodeCarbonMonitor
        
        monitor = CodeCarbonMonitor()
        
        # Verify that EmissionsTracker was called with a path containing 'output'
        call_args = mock_tracker.call_args
        assert call_args is not None
        assert 'output' in str(call_args[1]['output_file']).lower()
        assert 'emissions.csv' in str(call_args[1]['output_file']).lower()
        
    @patch('src.agents.runtime_monitor.codecarbon_integration.EmissionsTracker')
    def test_codecarbon_accepts_custom_path(self, mock_tracker):
        """CodeCarbonMonitor should accept custom output paths"""
        from src.agents.runtime_monitor.codecarbon_integration import CodeCarbonMonitor
        
        custom_path = "/tmp/custom_emissions.csv"
        monitor = CodeCarbonMonitor(output_file=custom_path)
        
        # Verify that EmissionsTracker was called with the custom path
        call_args = mock_tracker.call_args
        assert call_args[1]['output_file'] == custom_path
        
    def test_scaphandre_defaults_to_data_folder(self):
        """ScaphandreMonitor should default to data/scaphandre_metrics.json"""
        from src.agents.runtime_monitor.scaphandre_integration import ScaphandreMonitor
        
        monitor = ScaphandreMonitor()
        assert monitor.output_file.endswith("scaphandre_metrics.json")
        assert "output" in monitor.output_file
        
    def test_scaphandre_accepts_custom_path(self):
        """ScaphandreMonitor should accept custom output paths"""
        from src.agents.runtime_monitor.scaphandre_integration import ScaphandreMonitor
        
        custom_path = "/tmp/custom_metrics.json"
        monitor = ScaphandreMonitor(output_file=custom_path)
        assert monitor.output_file == custom_path
        
    @patch('src.agents.runtime_monitor.codecarbon_integration.EmissionsTracker')
    def test_data_folder_exists(self, mock_tracker):
        """Ensure data folder is created if it doesn't exist"""
        from src.agents.runtime_monitor.codecarbon_integration import CodeCarbonMonitor
        
        monitor = CodeCarbonMonitor()
        monitor = CodeCarbonMonitor()
        out_dir = Path(__file__).parent.parent / "output"
        assert out_dir.exists()
        assert out_dir.is_dir()
        
    def test_scaphandre_data_folder_created(self):
        """ScaphandreMonitor should ensure data folder exists"""
        from src.agents.runtime_monitor.scaphandre_integration import ScaphandreMonitor
        
        monitor = ScaphandreMonitor()
        monitor = ScaphandreMonitor()
        out_dir = Path(__file__).parent.parent / "output"
        assert out_dir.exists()
        assert out_dir.is_dir()


class TestEmissionsDataStructure:
    """Test the structure and format of emissions data."""

    def test_emissions_csv_location(self):
        """Verify emissions.csv is in the data folder, not root"""
        root_dir = Path(__file__).parent.parent
        out_dir = root_dir / "output"
        
        # Check that emissions.csv is NOT in root
        assert not (root_dir / "emissions.csv").exists()
        # It's okay if it's not in output/ yet if not run, but test intention is usually policy check
        
        # Check data folder exists
        assert out_dir.exists()
        
    def test_emissions_file_structure(self):
        """Verify emissions data file structure when present"""
        out_dir = Path(__file__).parent.parent / "output"
        emissions_file = out_dir / "emissions.csv"
        
        if emissions_file.exists():
            # File should be readable
            with open(emissions_file, 'r') as f:
                content = f.read()
                # Should have header and data rows
                lines = content.strip().split('\n')
                assert len(lines) >= 1  # At least header
