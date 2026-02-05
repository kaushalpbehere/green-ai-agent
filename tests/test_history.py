"""
Unit tests for history module (trending and historical tracking)
"""

import pytest
import os
import tempfile
import json
from datetime import datetime, timedelta
from src.core.history import HistoryManager, ScanHistory


class TestScanHistory:
    """Test ScanHistory class"""
    
    def test_scan_history_creation(self):
        """Test creating a ScanHistory object"""
        issues = [
            {'severity': 'critical', 'file': 'app.py', 'line': 10},
            {'severity': 'high', 'file': 'utils.py', 'line': 20}
        ]
        
        history = ScanHistory(
            project_name='test_project',
            timestamp=datetime.now().isoformat(),
            violations=2,
            codebase_emissions=0.000001,
            scanning_emissions=0.0000001,
            issues=issues,
            grade='B'
        )
        
        assert history.project_name == 'test_project'
        assert history.violations == 2
        assert history.grade == 'B'
    
    def test_severity_breakdown(self):
        """Test severity breakdown calculation"""
        issues = [
            {'severity': 'critical'},
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]
        
        history = ScanHistory(
            project_name='test',
            timestamp=datetime.now().isoformat(),
            violations=5,
            codebase_emissions=0,
            scanning_emissions=0,
            issues=issues
        )
        
        breakdown = history._get_severity_breakdown()
        assert breakdown['critical'] == 2
        assert breakdown['high'] == 1
        assert breakdown['medium'] == 1
        assert breakdown['low'] == 1
        assert breakdown['info'] == 0
    
    def test_to_dict_serialization(self):
        """Test converting to dictionary"""
        history = ScanHistory(
            project_name='test',
            timestamp='2026-01-27T10:00:00',
            violations=5,
            codebase_emissions=0.000001,
            scanning_emissions=0.0000001,
            issues=[],
            grade='C'
        )
        
        data = history.to_dict()
        assert data['project_name'] == 'test'
        assert data['violations'] == 5
        assert data['grade'] == 'C'
        assert 'severity_breakdown' in data
    
    def test_from_dict_deserialization(self):
        """Test creating from dictionary"""
        data = {
            'project_name': 'test_project',
            'timestamp': '2026-01-27T10:00:00',
            'violations': 3,
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001,
            'grade': 'B',
            'issues': []
        }
        
        history = ScanHistory.from_dict(data)
        assert history.project_name == 'test_project'
        assert history.violations == 3


class TestHistoryManager:
    """Test HistoryManager class"""
    
    @pytest.fixture
    def temp_history_dir(self):
        """Create temporary history directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def history_manager(self, temp_history_dir):
        """Create HistoryManager with temp directory"""
        return HistoryManager(temp_history_dir)
    
    def test_directory_creation(self, temp_history_dir):
        """Test that history directory is created"""
        manager = HistoryManager(temp_history_dir)
        assert os.path.exists(temp_history_dir)
    
    def test_add_scan(self, history_manager):
        """Test adding a scan to history"""
        results = {
            'issues': [
                {'severity': 'critical', 'file': 'app.py', 'line': 10},
                {'severity': 'high', 'file': 'utils.py', 'line': 20}
            ],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        
        history = history_manager.add_scan('test_project', results)
        
        assert history.project_name == 'test_project'
        assert history.violations == 2
        assert isinstance(history.timestamp, str)
    
    def test_get_project_history(self, history_manager):
        """Test retrieving project history"""
        results1 = {
            'issues': [{'severity': 'high'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        results2 = {
            'issues': [{'severity': 'high'}, {'severity': 'medium'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        
        history_manager.add_scan('test_project', results1)
        history_manager.add_scan('test_project', results2)
        
        history = history_manager.get_project_history('test_project')
        
        assert len(history) == 2
        assert history[0].violations == 1
        assert history[1].violations == 2
    
    def test_history_persistence(self, history_manager):
        """Test that history is persisted to file"""
        results = {
            'issues': [{'severity': 'critical'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        
        history_manager.add_scan('test_project', results)
        
        # Create new manager with same directory
        manager2 = HistoryManager(history_manager.history_dir)
        history = manager2.get_project_history('test_project')
        
        assert len(history) == 1
        assert history[0].violations == 1
    
    def test_get_trending_data_insufficient_data(self, history_manager):
        """Test trending data with less than 2 scans"""
        results = {
            'issues': [{'severity': 'high'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        
        history_manager.add_scan('test_project', results)
        
        trending = history_manager.get_trending_data('test_project')
        
        assert trending['trend'] == 'insufficient_data'
        assert trending['scans_available'] == 1
    
    def test_get_trending_data_improving(self, history_manager):
        """Test trending data showing improvement"""
        # First scan: 5 violations
        results1 = {
            'issues': [
                {'severity': 'critical'}, {'severity': 'critical'},
                {'severity': 'high'}, {'severity': 'high'}, {'severity': 'medium'}
            ],
            'codebase_emissions': 0.000005,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results1)
        
        # Second scan: 2 violations (improvement)
        results2 = {
            'issues': [
                {'severity': 'high'}, {'severity': 'medium'}
            ],
            'codebase_emissions': 0.000002,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results2)
        
        trending = history_manager.get_trending_data('test_project', days=30)
        
        assert trending['trend'] == 'improving'
        assert trending['violations']['delta'] == -3
        assert trending['violations']['change_pct'] == -60.0
        assert trending['scans_analyzed'] == 2
    
    def test_get_trending_data_worsening(self, history_manager):
        """Test trending data showing deterioration"""
        # First scan: 1 violation
        results1 = {
            'issues': [{'severity': 'low'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results1)
        
        # Second scan: 3 violations (worse)
        results2 = {
            'issues': [
                {'severity': 'high'}, {'severity': 'medium'}, {'severity': 'low'}
            ],
            'codebase_emissions': 0.000003,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results2)
        
        trending = history_manager.get_trending_data('test_project')
        
        assert trending['trend'] == 'worsening'
        assert trending['violations']['delta'] == 2
    
    def test_get_trending_data_stable(self, history_manager):
        """Test trending data showing no change"""
        # First scan: 3 violations
        results1 = {
            'issues': [
                {'severity': 'high'}, {'severity': 'medium'}, {'severity': 'low'}
            ],
            'codebase_emissions': 0.000003,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results1)
        
        # Second scan: 3 violations (same)
        results2 = {
            'issues': [
                {'severity': 'high'}, {'severity': 'medium'}, {'severity': 'low'}
            ],
            'codebase_emissions': 0.000003,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results2)
        
        trending = history_manager.get_trending_data('test_project')
        
        assert trending['trend'] == 'stable'
        assert trending['violations']['delta'] == 0
    
    def test_compare_scans(self, history_manager):
        """Test comparing two scans"""
        # First scan
        results1 = {
            'issues': [
                {'severity': 'critical', 'file': 'app.py', 'line': 10, 'id': 'rule1'},
                {'severity': 'high', 'file': 'utils.py', 'line': 20, 'id': 'rule2'}
            ],
            'codebase_emissions': 0.000002,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results1)
        
        # Second scan (one fixed, one new)
        results2 = {
            'issues': [
                {'severity': 'high', 'file': 'utils.py', 'line': 20, 'id': 'rule2'},
                {'severity': 'medium', 'file': 'config.py', 'line': 30, 'id': 'rule3'}
            ],
            'codebase_emissions': 0.000002,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results2)
        
        comparison = history_manager.compare_scans('test_project')
        
        assert comparison['changes']['fixed_violations'] == 1  # rule1
        assert comparison['changes']['new_violations'] == 1    # rule3
        assert comparison['changes']['net_change'] == 0
    
    def test_get_history_by_days(self, history_manager):
        """Test filtering history by days"""
        # Add old scan (manually adjust timestamp)
        results_old = {
            'issues': [{'severity': 'high'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results_old)
        
        # Add recent scan
        results_new = {
            'issues': [{'severity': 'high'}, {'severity': 'medium'}],
            'codebase_emissions': 0.000001,
            'scanning_emissions': 0.0000001
        }
        history_manager.add_scan('test_project', results_new)
        
        # Get all history
        all_history = history_manager.get_project_history('test_project')
        assert len(all_history) == 2
        
        # Get recent history (should be limited)
        recent = history_manager.get_project_history('test_project', days=1)
        assert len(recent) == 2  # Both are within last day
    
    def test_calculate_grade_all_critical(self):
        """Test grade calculation for critical violations"""
        issues = [
            {'severity': 'critical'},
            {'severity': 'critical'},
            {'severity': 'critical'}
        ]
        
        grade = HistoryManager._calculate_grade(issues)
        assert grade == 'F'
    
    def test_calculate_grade_all_low(self):
        """Test grade calculation for low violations"""
        issues = [
            {'severity': 'low'},
            {'severity': 'low'},
            {'severity': 'info'}
        ]
        
        grade = HistoryManager._calculate_grade(issues)
        assert grade == 'A'
    
    def test_calculate_grade_mixed(self):
        """Test grade calculation for mixed violations"""
        issues = [
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]
        
        grade = HistoryManager._calculate_grade(issues)
        assert grade in ['A', 'B', 'C', 'D', 'F']
    
    def test_calculate_grade_empty(self):
        """Test grade calculation for no violations"""
        grade = HistoryManager._calculate_grade([])
        assert grade == 'A'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
