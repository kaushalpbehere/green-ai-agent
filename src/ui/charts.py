"""
Chart data generation for Green AI Agent Dashboard.
Provides structured data for visualizations (pie charts, bar charts, etc.)
"""

from typing import Dict, List, Any
from collections import defaultdict


class ChartDataGenerator:
    """Generate chart data from scan results for dashboard visualization."""
    
    @staticmethod
    def violations_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate severity distribution chart data.
        
        Returns:
            {
                'labels': ['Critical', 'High', 'Medium', 'Low'],
                'data': [count, count, count, count],
                'colors': ['#dc2626', '#dc2626', '#f59e0b', '#3b82f6'],
                'percentages': [0.0, 0.0, 50.0, 50.0]
            }
        """
        severity_map = {
            'critical': {'label': 'Critical', 'color': '#dc2626'},
            'high': {'label': 'High', 'color': '#dc2626'},
            'medium': {'label': 'Medium', 'color': '#f59e0b'},
            'low': {'label': 'Low', 'color': '#3b82f6'},
        }
        
        counts = defaultdict(int)
        for issue in issues:
            severity = issue.get('severity', 'low').lower()
            counts[severity] += 1
        
        labels = []
        data = []
        colors = []
        total = sum(counts.values())
        percentages = []
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in counts or total > 0:
                count = counts.get(severity, 0)
                labels.append(severity_map[severity]['label'])
                data.append(count)
                colors.append(severity_map[severity]['color'])
                pct = (count / total * 100) if total > 0 else 0
                percentages.append(round(pct, 1))
        
        return {
            'labels': labels,
            'data': data,
            'colors': colors,
            'percentages': percentages,
            'total': total
        }
    
    @staticmethod
    def violations_by_type(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate violation type distribution chart data.
        
        Returns:
            {
                'labels': ['Memory', 'CPU', 'IO', ...],
                'data': [count, count, count, ...],
                'percentages': [20.0, 15.0, 10.0, ...]
            }
        """
        type_counts = defaultdict(int)
        total = len(issues)
        
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type == 'green_violation':
                # Extract violation type from ID (e.g., "MEMORY_LEAK" -> "Memory Leak")
                violation_id = issue.get('id', 'unknown').lower()
                if 'memory' in violation_id:
                    type_counts['Memory'] += 1
                elif 'cpu' in violation_id or 'loop' in violation_id:
                    type_counts['CPU'] += 1
                elif 'io' in violation_id or 'disk' in violation_id:
                    type_counts['I/O'] += 1
                elif 'network' in violation_id:
                    type_counts['Network'] += 1
                elif 'energy' in violation_id or 'battery' in violation_id:
                    type_counts['Energy'] += 1
                else:
                    type_counts['Other'] += 1
        
        labels = sorted(type_counts.keys())
        data = [type_counts[label] for label in labels]
        percentages = [round(count / total * 100, 1) if total > 0 else 0 for count in data]
        
        return {
            'labels': labels,
            'data': data,
            'percentages': percentages,
            'total': total
        }
    
    @staticmethod
    def violations_by_file(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate violations per file breakdown.
        
        Returns:
            {
                'labels': ['file1.py', 'file2.py', ...],
                'data': [count, count, ...],
                'emissions': [emissions_kg, emissions_kg, ...],
                'percentages': [30.0, 25.0, ...]
            }
        """
        file_violations = defaultdict(lambda: {'count': 0, 'emissions': 0.0})
        total = len(issues)
        
        for issue in issues:
            filename = issue.get('file', 'unknown')
            file_violations[filename]['count'] += 1
            file_violations[filename]['emissions'] += issue.get('codebase_emissions', 0.0)
        
        # Sort by count descending, limit to top 10
        sorted_files = sorted(
            file_violations.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        labels = [f[0] for f in sorted_files]
        data = [f[1]['count'] for f in sorted_files]
        emissions = [round(f[1]['emissions'], 9) for f in sorted_files]
        
        total_emissions = sum(emissions)
        percentages = [
            round(f[1]['count'] / total * 100, 1) if total > 0 else 0
            for f in sorted_files
        ]
        
        return {
            'labels': labels,
            'data': data,
            'emissions': emissions,
            'percentages': percentages,
            'total': total,
            'total_emissions': total_emissions
        }
    
    @staticmethod
    def top_violations(issues: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top violations by emissions impact.
        
        Returns:
            [
                {
                    'id': 'RULE_ID',
                    'severity': 'high',
                    'emissions': 0.0000001,
                    'file': 'file.py',
                    'line': 42,
                    'message': 'Issue description'
                },
                ...
            ]
        """
        # Sort by emissions impact (descending)
        sorted_issues = sorted(
            issues,
            key=lambda x: x.get('codebase_emissions', 0.0),
            reverse=True
        )[:limit]
        
        return [
            {
                'id': issue.get('id', 'unknown'),
                'severity': issue.get('severity', 'low'),
                'emissions': round(issue.get('codebase_emissions', 0.0), 9),
                'file': issue.get('file', 'unknown'),
                'line': issue.get('line', 0),
                'message': issue.get('message', 'N/A'),
                'effort': issue.get('effort', 'Unknown')
            }
            for issue in sorted_issues
        ]
    
    @staticmethod
    def emissions_trend(per_file_emissions: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate emissions by file trend data for bar chart.
        
        Returns:
            {
                'labels': ['file1.py', 'file2.py', ...],
                'data': [emissions, emissions, ...],
                'total': total_emissions,
                'average': average_emissions
            }
        """
        if not per_file_emissions:
            return {
                'labels': [],
                'data': [],
                'total': 0.0,
                'average': 0.0
            }
        
        # Sort by emissions descending, limit to top 10
        sorted_files = sorted(
            per_file_emissions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        labels = [f[0] for f in sorted_files]
        data = [round(f[1], 9) for f in sorted_files]
        
        total = sum(per_file_emissions.values())
        average = total / len(per_file_emissions) if per_file_emissions else 0.0
        
        return {
            'labels': labels,
            'data': data,
            'total': round(total, 9),
            'average': round(average, 9)
        }
    
    @staticmethod
    def summary_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate key summary metrics for dashboard.
        
        Returns:
            {
                'total_issues': 0,
                'critical_issues': 0,
                'total_emissions': 0.0,
                'scanning_emissions': 0.0,
                'codebase_emissions': 0.0,
                'avg_issue_emissions': 0.0,
                'most_affected_file': 'file.py',
                'highest_impact_rule': 'RULE_ID'
            }
        """
        issues = results.get('issues', [])
        total_issues = len(issues)
        
        critical_issues = sum(
            1 for issue in issues
            if issue.get('severity') in ['critical', 'high']
        )
        
        scanning_emissions = results.get('scanning_emissions', 0.0)
        codebase_emissions = results.get('codebase_emissions', 0.0)
        total_emissions = scanning_emissions + codebase_emissions
        
        avg_issue_emissions = 0.0
        if total_issues > 0:
            total_issue_emissions = sum(
                issue.get('codebase_emissions', 0.0)
                for issue in issues
            )
            avg_issue_emissions = total_issue_emissions / total_issues
        
        # Find most affected file
        per_file = results.get('per_file_emissions', {})
        most_affected_file = max(per_file, key=per_file.get) if per_file else 'N/A'
        
        # Find highest impact rule
        highest_impact_rule = 'N/A'
        if issues:
            highest_issue = max(
                issues,
                key=lambda x: x.get('codebase_emissions', 0.0)
            )
            highest_impact_rule = highest_issue.get('id', 'N/A')
        
        return {
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'medium_issues': sum(1 for issue in issues if issue.get('severity') == 'medium'),
            'low_issues': sum(1 for issue in issues if issue.get('severity') == 'low'),
            'total_emissions': round(total_emissions, 9),
            'scanning_emissions': round(scanning_emissions, 9),
            'codebase_emissions': round(codebase_emissions, 9),
            'avg_issue_emissions': round(avg_issue_emissions, 9),
            'most_affected_file': most_affected_file,
            'highest_impact_rule': highest_impact_rule,
            'total_files': len(per_file) if per_file else 0
        }


def generate_all_charts(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate all chart data from scan results."""
    generator = ChartDataGenerator()
    
    issues = results.get('issues', [])
    per_file_emissions = results.get('per_file_emissions', {})
    
    return {
        'severity_chart': generator.violations_by_severity(issues),
        'type_chart': generator.violations_by_type(issues),
        'file_chart': generator.violations_by_file(issues),
        'top_violations': generator.top_violations(issues, limit=10),
        'emissions_trend': generator.emissions_trend(per_file_emissions),
        'summary_metrics': generator.summary_metrics(results)
    }
