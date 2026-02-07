"""
Export module for GASA - Violation data export to multiple formats

Supports CSV and HTML export with comprehensive violation and metrics data.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


# Default output directory for all exports
OUTPUT_DIR = Path(__file__).parent.parent.parent / 'output'


class CSVExporter:
    """Export scan results to CSV format."""
    
    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize CSV exporter.
        
        Args:
            output_path: Path to write CSV file. If None, defaults to 'output/green-ai-report.csv'
        """
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        if output_path:
            self.output_path = output_path
        else:
            self.output_path = str(OUTPUT_DIR / 'green-ai-report.csv')
    
    @staticmethod
    def _get_severity_score(severity: str) -> int:
        """Convert severity string to numeric score for sorting."""
        severity_scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'info': 0
        }
        return severity_scores.get(severity.lower(), 0)
    
    @staticmethod
    def _get_energy_factor(issue: Dict[str, Any]) -> str:
        """Extract energy factor from issue."""
        if 'energy_factor' in issue:
            return str(issue['energy_factor'])
        
        # Infer from rule ID
        severity = issue.get('severity', 'low').lower()
        if 'io_in_loop' in issue.get('id', ''):
            return '1000x'
        elif 'blocking_io' in issue.get('id', ''):
            return '100x'
        elif 'excessive_nesting' in issue.get('id', ''):
            return str(2 ** int(issue.get('line', 2) % 3 + 2)) + 'x'
        elif severity == 'critical':
            return '100x'
        elif severity == 'high':
            return '10x'
        elif severity == 'medium':
            return '1x'
        else:
            return '0.1x'
    
    @staticmethod
    def _get_effort(issue: Dict[str, Any]) -> str:
        """Extract effort estimation from issue."""
        if 'effort' in issue:
            return issue['effort']
        
        severity = issue.get('severity', 'low').lower()
        effort_map = {
            'critical': 'high',
            'high': 'medium',
            'medium': 'easy',
            'low': 'trivial',
            'info': 'trivial'
        }
        return effort_map.get(severity, 'medium')
    
    def export(self, results: Dict[str, Any], project_name: str = 'Scan') -> str:
        """
        Export scan results to CSV file.
        
        Args:
            results: Scan results dictionary from Scanner.scan()
            project_name: Name of the project being scanned
            
        Returns:
            Path to generated CSV file
        """
        issues = results.get('issues', [])
        
        # Sort by severity (critical first) then by file
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        sorted_issues = sorted(
            issues,
            key=lambda x: (
                severity_order.get(x.get('severity', 'info').lower(), 5),
                x.get('file', ''),
                x.get('line', 0)
            )
        )
        
        # Calculate totals
        total_violations = len(sorted_issues)
        critical_count = sum(1 for i in sorted_issues if i.get('severity', '').lower() == 'critical')
        high_count = sum(1 for i in sorted_issues if i.get('severity', '').lower() == 'high')
        medium_count = sum(1 for i in sorted_issues if i.get('severity', '').lower() == 'medium')
        low_count = sum(1 for i in sorted_issues if i.get('severity', '').lower() == 'low')
        
        # Average effort (simplified)
        effort_scores = {'high': 3, 'medium': 2, 'easy': 1, 'trivial': 0}
        avg_effort = 'medium'
        if total_violations > 0:
            total_effort = sum(effort_scores.get(self._get_effort(i), 1) for i in sorted_issues)
            avg_effort_score = total_effort / total_violations
            for effort_level, score in [('high', 2.5), ('medium', 1.5), ('easy', 0.5)]:
                if avg_effort_score >= score:
                    avg_effort = effort_level
                    break
        
        with open(self.output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['file', 'line', 'rule_id', 'severity', 'message', 'energy_factor', 'effort']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write issues
            for issue in sorted_issues:
                writer.writerow({
                    'file': issue.get('file', 'unknown'),
                    'line': issue.get('line', 0),
                    'rule_id': issue.get('id', 'unknown_rule'),
                    'severity': issue.get('severity', 'info').lower(),
                    'message': issue.get('message', 'No message'),
                    'energy_factor': self._get_energy_factor(issue),
                    'effort': self._get_effort(issue)
                })
            
            # Write summary row
            codebase_emissions = results.get('codebase_emissions', 0)
            scanning_emissions = results.get('scanning_emissions', 0)
            total_emissions = codebase_emissions + scanning_emissions
            
            writer.writerow({
                'file': 'SUMMARY',
                'line': '',
                'rule_id': '',
                'severity': '',
                'message': f'Total Violations: {total_violations} | Critical: {critical_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count} | Avg Effort: {avg_effort} | CO2: {codebase_emissions:.9f}kg',
                'energy_factor': f'{total_emissions:.9f}kg',
                'effort': 'varies'
            })
        
        return self.output_path


class JSONExporter:
    """Export scan results to JSON format."""

    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize JSON exporter.

        Args:
            output_path: Path to write JSON file. If None, defaults to 'output/green-ai-report.json'
        """
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if output_path:
            self.output_path = output_path
        else:
            self.output_path = str(OUTPUT_DIR / 'green-ai-report.json')

    def export(self, results: Dict[str, Any], project_name: str = 'Scan') -> str:
        """
        Export scan results to JSON file.

        Args:
            results: Scan results dictionary from Scanner.scan()
            project_name: Name of the project being scanned

        Returns:
            Path to generated JSON file
        """
        # Add metadata if not present
        if 'metadata' not in results:
            results['metadata'] = {}

        results['metadata']['project_name'] = project_name
        results['metadata']['export_time'] = datetime.utcnow().isoformat() + "Z"

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        return self.output_path
    
    def get_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate statistics from scan results.
        
        Args:
            results: Scan results dictionary
            
        Returns:
            Dictionary with statistics
        """
        issues = results.get('issues', [])
        
        severity_counts = {
            'critical': sum(1 for i in issues if i.get('severity', '').lower() == 'critical'),
            'high': sum(1 for i in issues if i.get('severity', '').lower() == 'high'),
            'medium': sum(1 for i in issues if i.get('severity', '').lower() == 'medium'),
            'low': sum(1 for i in issues if i.get('severity', '').lower() == 'low'),
            'info': sum(1 for i in issues if i.get('severity', '').lower() == 'info')
        }
        
        affected_files = len(set(i.get('file', 'unknown') for i in issues))
        
        # Group by rule ID
        rules = {}
        for issue in issues:
            rule_id = issue.get('id', 'unknown')
            if rule_id not in rules:
                rules[rule_id] = 0
            rules[rule_id] += 1
        
        return {
            'total_violations': len(issues),
            'severity_counts': severity_counts,
            'affected_files': affected_files,
            'by_rule': rules,
            'codebase_emissions': results.get('codebase_emissions', 0),
            'scanning_emissions': results.get('scanning_emissions', 0),
            'per_file_emissions': results.get('per_file_emissions', {})
        }


class HTMLReporter:
    """Export scan results to HTML format with charts and detailed breakdowns."""
    
    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize HTML reporter.
        
        Args:
            output_path: Path to write HTML file. If None, defaults to 'output/green-ai-report.html'
        """
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        if output_path:
            self.output_path = output_path
        else:
            self.output_path = str(OUTPUT_DIR / 'green-ai-report.html')
    
    @staticmethod
    def _get_color_for_severity(severity: str) -> str:
        """Get HTML color code for severity level."""
        severity_colors = {
            'critical': '#ef4444',  # red
            'high': '#f97316',      # orange
            'medium': '#eab308',    # yellow
            'low': '#3b82f6',       # blue
            'info': '#8b5cf6'       # purple
        }
        return severity_colors.get(severity.lower(), '#6b7280')
    
    @staticmethod
    def _get_severity_badge(severity: str) -> str:
        """Generate HTML badge for severity."""
        color = HTMLReporter._get_color_for_severity(severity)
        icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵',
            'info': '🟣'
        }
        icon = icons.get(severity.lower(), '⚪')
        return f'<span style="color: {color}; font-weight: bold;">{icon} {severity.upper()}</span>'
    
    def export(self, results: Dict[str, Any], project_name: str = 'Scan') -> str:
        """
        Export scan results to HTML report.
        
        Args:
            results: Scan results dictionary from Scanner.scan()
            project_name: Name of the project being scanned
            
        Returns:
            Path to generated HTML file
        """
        issues = results.get('issues', [])
        
        # Calculate statistics
        severity_counts = {
            'critical': sum(1 for i in issues if i.get('severity', '').lower() == 'critical'),
            'high': sum(1 for i in issues if i.get('severity', '').lower() == 'high'),
            'medium': sum(1 for i in issues if i.get('severity', '').lower() == 'medium'),
            'low': sum(1 for i in issues if i.get('severity', '').lower() == 'low'),
            'info': sum(1 for i in issues if i.get('severity', '').lower() == 'info')
        }
        
        # Group by file
        by_file = {}
        for issue in issues:
            file_path = issue.get('file', 'unknown')
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)
        
        # Sort files by violation count
        sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
        
        codebase_emissions = results.get('codebase_emissions', 0)
        scanning_emissions = results.get('scanning_emissions', 0)
        
        # Build HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Green-AI Report - {project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .metric {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}
        
        .metric h3 {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}
        
        .chart-container h3 {{
            margin-bottom: 15px;
            font-size: 1.1em;
            color: #333;
        }}
        
        canvas {{
            max-height: 300px;
        }}
        
        .violations-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .violations-table thead {{
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .violations-table th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
        }}
        
        .violations-table td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .violations-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .file-section {{
            margin-top: 20px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        
        .file-name {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.05em;
        }}
        
        .violation-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            display: grid;
            grid-template-columns: 80px 1fr 100px 100px;
            gap: 15px;
            align-items: center;
        }}
        
        .violation-line {{
            font-weight: 600;
            color: #667eea;
            text-align: center;
        }}
        
        .violation-message {{
            color: #555;
        }}
        
        .violation-severity {{
            text-align: center;
            font-size: 0.9em;
        }}
        
        .violation-effort {{
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .severity-critical {{ border-left-color: #ef4444; }}
        .severity-high {{ border-left-color: #f97316; }}
        .severity-medium {{ border-left-color: #eab308; }}
        .severity-low {{ border-left-color: #3b82f6; }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-critical {{ background: #fecaca; color: #dc2626; }}
        .badge-high {{ background: #fed7aa; color: #ea580c; }}
        .badge-medium {{ background: #fef08a; color: #ca8a04; }}
        .badge-low {{ background: #bfdbfe; color: #1e40af; }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .charts {{
                grid-template-columns: 1fr;
            }}
            
            .violation-item {{
                grid-template-columns: 1fr;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Green-AI Report</h1>
            <p>Project: <strong>{project_name}</strong></p>
            <div class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </header>
        
        <div class="summary">
            <div class="metric">
                <h3>Total Violations</h3>
                <div class="value">{len(issues)}</div>
            </div>
            <div class="metric">
                <h3>Critical Issues</h3>
                <div class="value" style="color: #ef4444;">{severity_counts['critical']}</div>
            </div>
            <div class="metric">
                <h3>Affected Files</h3>
                <div class="value">{len(by_file)}</div>
            </div>
            <div class="metric">
                <h3>CO₂ Impact</h3>
                <div class="value">{codebase_emissions:.6f}kg</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Violation Analysis</h2>
                <div class="charts">
                    <div class="chart-container">
                        <h3>By Severity</h3>
                        <canvas id="severityChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>By File</h3>
                        <canvas id="fileChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Detailed Violations</h2>
                <div>
"""
        
        # Add file sections with violations
        for file_path, file_issues in sorted_files:
            html_content += f"""
                <div class="file-section">
                    <div class="file-name">📄 {file_path}</div>
                    <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
                        {len(file_issues)} violation(s)
                    </div>
"""
            
            for issue in sorted(file_issues, key=lambda x: x.get('line', 0)):
                severity = issue.get('severity', 'info').lower()
                effort = CSVExporter._get_effort(issue)
                html_content += f"""
                    <div class="violation-item severity-{severity}">
                        <div class="violation-line">Line {issue.get('line', '?')}</div>
                        <div class="violation-message">
                            <strong>{issue.get('id', 'unknown')}</strong><br>
                            {issue.get('message', 'No message')}
                        </div>
                        <div class="violation-severity">
                            <span class="badge badge-{severity}">{severity.upper()}</span>
                        </div>
                        <div class="violation-effort">
                            <span style="background: #f0f0f0; padding: 4px 8px; border-radius: 4px;">{effort}</span>
                        </div>
                    </div>
"""
            
            html_content += """
                </div>
"""
        
        html_content += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>⚡ Energy Impact</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <p><strong>Codebase Emissions:</strong> {codebase_emissions:.9f} kg CO₂</p>
                    <p><strong>Scanning Process Emissions:</strong> {scanning_emissions:.9f} kg CO₂</p>
                    <p><strong>Total Emissions:</strong> {codebase_emissions + scanning_emissions:.9f} kg CO₂</p>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Green-AI Software Analyzer - Reducing Carbon Footprint of Software Development</p>
            <p style="margin-top: 10px; opacity: 0.8;">This report was automatically generated. For more information, visit <a href="https://github.com/your-org/green-ai" style="color: #667eea;">Green-AI</a></p>
        </footer>
    </div>
    
    <script>
        // Severity Chart
        const severityCtx = document.getElementById('severityChart').getContext('2d');
        new Chart(severityCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
                datasets: [{{
                    data: [{severity_counts['critical']}, {severity_counts['high']}, {severity_counts['medium']}, {severity_counts['low']}, {severity_counts['info']}],
                    backgroundColor: ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#8b5cf6'],
                    borderColor: '#fff',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // File Chart
        const fileCtx = document.getElementById('fileChart').getContext('2d');
        const fileLabels = {list(by_file.keys())};
        const fileCounts = {[len(issues) for issues in by_file.values()]};
        
        new Chart(fileCtx, {{
            type: 'bar',
            data: {{
                labels: fileLabels.slice(0, 10),
                datasets: [{{
                    label: 'Violations',
                    data: fileCounts.slice(0, 10),
                    backgroundColor: '#667eea',
                    borderColor: '#667eea',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_path
