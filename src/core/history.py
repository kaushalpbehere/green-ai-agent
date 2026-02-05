"""
History Manager - Track scan results over time for trending and analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ScanHistory:
    """Represents a single scan in history"""
    
    def __init__(self, project_name: str, timestamp: str, violations: int, 
                 codebase_emissions: float, scanning_emissions: float, 
                 issues: List[Dict], grade: str = 'N/A'):
        self.project_name = project_name
        self.timestamp = timestamp
        self.violations = violations
        self.codebase_emissions = codebase_emissions
        self.scanning_emissions = scanning_emissions
        self.issues = issues
        self.grade = grade
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'project_name': self.project_name,
            'timestamp': self.timestamp,
            'violations': self.violations,
            'codebase_emissions': self.codebase_emissions,
            'scanning_emissions': self.scanning_emissions,
            'grade': self.grade,
            'issue_count': len(self.issues),
            'issues': self.issues,  # Store full issues for comparison
            'severity_breakdown': self._get_severity_breakdown()
        }
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get counts by severity"""
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for issue in self.issues:
            severity = issue.get('severity', 'info').lower()
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown
    
    @staticmethod
    def from_dict(data: Dict) -> 'ScanHistory':
        """Create from dictionary"""
        return ScanHistory(
            project_name=data.get('project_name', 'unknown'),
            timestamp=data.get('timestamp', ''),
            violations=data.get('violations', 0),
            codebase_emissions=data.get('codebase_emissions', 0),
            scanning_emissions=data.get('scanning_emissions', 0),
            issues=data.get('issues', []),
            grade=data.get('grade', 'N/A')
        )


class HistoryManager:
    """Manage scan history and trending"""
    
    def __init__(self, history_dir: Optional[str] = None):
        """
        Initialize history manager.
        
        Args:
            history_dir: Directory to store history. Defaults to ~/.green-ai/history/
        """
        if history_dir is None:
            home = os.path.expanduser('~')
            history_dir = os.path.join(home, '.green-ai', 'history')
        
        self.history_dir = history_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create history directory if it doesn't exist"""
        Path(self.history_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_project_history_file(self, project_name: str) -> str:
        """Get path to history file for project"""
        # Sanitize project name for filename
        safe_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in project_name)
        return os.path.join(self.history_dir, f'{safe_name}_history.json')
    
    def add_scan(self, project_name: str, scan_results: Dict) -> ScanHistory:
        """
        Add a scan result to history.
        
        Args:
            project_name: Name of the project
            scan_results: Dictionary from Scanner.scan()
            
        Returns:
            ScanHistory object
        """
        timestamp = datetime.now().isoformat()
        
        history = ScanHistory(
            project_name=project_name,
            timestamp=timestamp,
            violations=len(scan_results.get('issues', [])),
            codebase_emissions=scan_results.get('codebase_emissions', 0),
            scanning_emissions=scan_results.get('scanning_emissions', 0),
            issues=scan_results.get('issues', []),
            grade=self._calculate_grade(scan_results.get('issues', []))
        )
        
        # Load existing history
        history_file = self._get_project_history_file(project_name)
        scans = []
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    scans = [ScanHistory.from_dict(s).to_dict() for s in data.get('scans', [])]
            except Exception:
                scans = []
        
        # Add new scan
        scans.append(history.to_dict())
        
        # Save updated history
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({'scans': scans}, f, indent=2)
        
        return history
    
    def get_project_history(self, project_name: str, days: Optional[int] = None) -> List[ScanHistory]:
        """
        Get history for a project.
        
        Args:
            project_name: Name of the project
            days: Optional number of days to retrieve. If None, returns all.
            
        Returns:
            List of ScanHistory objects
        """
        history_file = self._get_project_history_file(project_name)
        
        if not os.path.exists(history_file):
            return []
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return []
        
        scans = [ScanHistory.from_dict(s) for s in data.get('scans', [])]
        
        if days:
            # Filter by days
            cutoff = datetime.now()
            from datetime import timedelta
            cutoff_time = cutoff - timedelta(days=days)
            scans = [s for s in scans if datetime.fromisoformat(s.timestamp) >= cutoff_time]
        
        return sorted(scans, key=lambda s: s.timestamp)
    
    def get_trending_data(self, project_name: str, days: Optional[int] = 30) -> Dict[str, Any]:
        """
        Get trending data for a project.
        
        Args:
            project_name: Name of the project
            days: Number of days to analyze. Defaults to 30.
            
        Returns:
            Dictionary with trending metrics
        """
        scans = self.get_project_history(project_name, days=days)
        
        if len(scans) < 2:
            return {
                'trend': 'insufficient_data',
                'message': 'Need at least 2 scans for trend analysis',
                'scans_available': len(scans),
                'scans': [s.to_dict() for s in scans]
            }
        
        # Calculate trends
        first_scan = scans[0]
        last_scan = scans[-1]
        
        violations_delta = last_scan.violations - first_scan.violations
        violations_change_pct = (violations_delta / first_scan.violations * 100) if first_scan.violations > 0 else 0
        
        emissions_delta = last_scan.codebase_emissions - first_scan.codebase_emissions
        emissions_change_pct = (emissions_delta / first_scan.codebase_emissions * 100) if first_scan.codebase_emissions > 0 else 0
        
        # Determine trend direction
        if violations_delta < 0:
            trend_direction = 'improving'
        elif violations_delta > 0:
            trend_direction = 'worsening'
        else:
            trend_direction = 'stable'
        
        return {
            'project_name': project_name,
            'period_days': days,
            'trend': trend_direction,
            'violations': {
                'first': first_scan.violations,
                'latest': last_scan.violations,
                'delta': violations_delta,
                'change_pct': round(violations_change_pct, 2)
            },
            'emissions': {
                'first': round(first_scan.codebase_emissions, 9),
                'latest': round(last_scan.codebase_emissions, 9),
                'delta': round(emissions_delta, 9),
                'change_pct': round(emissions_change_pct, 2)
            },
            'grade': {
                'first': first_scan.grade,
                'latest': last_scan.grade
            },
            'improvement_rate': abs(violations_delta) / len(scans) if scans else 0,
            'scans_analyzed': len(scans),
            'timeline': [s.to_dict() for s in scans]
        }
    
    def compare_scans(self, project_name: str, scan_index_1: int = -2, 
                     scan_index_2: int = -1) -> Dict[str, Any]:
        """
        Compare two scans from history.
        
        Args:
            project_name: Name of the project
            scan_index_1: Index of first scan (default: second-to-last)
            scan_index_2: Index of second scan (default: last)
            
        Returns:
            Comparison data
        """
        scans = self.get_project_history(project_name)
        
        if len(scans) < 2:
            return {'error': 'Need at least 2 scans to compare'}
        
        try:
            scan1 = scans[scan_index_1]
            scan2 = scans[scan_index_2]
        except IndexError:
            return {'error': 'Invalid scan indices'}
        
        # Find new and fixed violations using issue count comparison
        # new_violations = issues in scan2 but not in scan1
        # fixed_violations = issues in scan1 but not in scan2
        # We compare by (file, line, id) tuple
        issues1_set = {(i.get('file'), i.get('line'), i.get('id')) for i in scan1.issues}
        issues2_set = {(i.get('file'), i.get('line'), i.get('id')) for i in scan2.issues}
        
        new_violations = issues2_set - issues1_set
        fixed_violations = issues1_set - issues2_set
        
        return {
            'scan1': {
                'timestamp': scan1.timestamp,
                'violations': scan1.violations,
                'grade': scan1.grade
            },
            'scan2': {
                'timestamp': scan2.timestamp,
                'violations': scan2.violations,
                'grade': scan2.grade
            },
            'changes': {
                'new_violations': len(new_violations),
                'fixed_violations': len(fixed_violations),
                'net_change': scan2.violations - scan1.violations,
                'improvement': len(fixed_violations) > len(new_violations)
            },
            'details': {
                'new_issues': [{'file': f, 'line': l, 'id': i} for f, l, i in sorted(new_violations)],
                'fixed_issues': [{'file': f, 'line': l, 'id': i} for f, l, i in sorted(fixed_violations)]
            }
        }
    
    @staticmethod
    def _calculate_grade(issues: List[Dict]) -> str:
        """Calculate grade from issues"""
        if not issues:
            return 'A'
        
        # Count by severity
        severity_scores = {
            'critical': 5,
            'high': 3,
            'medium': 1,
            'low': 0.5,
            'info': 0
        }
        
        total_score = sum(severity_scores.get(i.get('severity', 'info').lower(), 0) for i in issues)
        issue_count = len(issues)
        
        # Grade based on weighted score
        avg_severity_score = total_score / issue_count if issue_count > 0 else 0
        
        if avg_severity_score < 0.5:
            return 'A'
        elif avg_severity_score < 1.5:
            return 'B'
        elif avg_severity_score < 3:
            return 'C'
        elif avg_severity_score < 4:
            return 'D'
        else:
            return 'F'
