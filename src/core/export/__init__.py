"""
Export module for Green-AI — violation data export to multiple formats.

Supports CSV and HTML export with comprehensive violation and metrics data.
"""

from src.core.remediation.engine import RemediationEngine

from src.utils.security import sanitize_path
import csv
import json
import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

# Default output directory for all exports
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / 'output'


def safe_read_snippet(file_path: str, line_number: int) -> str:
    """Safely read a single line snippet from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if 0 <= line_number - 1 < len(lines):
                return lines[line_number - 1].strip()
    except Exception:
        pass
    return ""


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
            self.output_path = str(sanitize_path(output_path, allow_absolute=True))
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

        # Instantiate RemediationEngine locally to avoid UI dependency
        try:
            remediation_engine = RemediationEngine()
        except Exception:
            remediation_engine = None

        has_ai = any(i.get('category') == 'ai_sustainability' for i in sorted_issues)
        fieldnames = [
            'file', 'line', 'rule_id', 'severity', 'message',
            'energy_factor', 'effort', 'snippet', 'remediation',
        ]
        if has_ai:
            fieldnames += ['category', 'provider', 'model_tier', 'estimated_co2_g', 'co2_note']

        with open(self.output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

            # Write header
            writer.writeheader()

            # Write issues
            for issue in sorted_issues:
                # Get snippet
                snippet = safe_read_snippet(issue.get('file', ''), issue.get('line', 0))

                # Get remediation
                remediation = ""
                if remediation_engine:
                    remediation = remediation_engine.get_suggestion(issue.get('id', ''))

                row = {
                    'file': issue.get('file', 'unknown'),
                    'line': issue.get('line', 0),
                    'rule_id': issue.get('id', 'unknown_rule'),
                    'severity': issue.get('severity', 'info').lower(),
                    'message': issue.get('message', 'No message'),
                    'energy_factor': self._get_energy_factor(issue),
                    'effort': self._get_effort(issue),
                    'snippet': snippet,
                    'remediation': remediation,
                }
                if has_ai:
                    row['category'] = issue.get('category', '')
                    row['provider'] = issue.get('provider', '')
                    row['model_tier'] = issue.get('model_tier', '')
                    row['estimated_co2_g'] = issue.get('estimated_co2_g', '')
                    row['co2_note'] = issue.get('co2_note', '')
                writer.writerow(row)

            # Write summary row
            codebase_emissions = results.get('codebase_emissions', 0)
            scanning_emissions = results.get('scanning_emissions', 0)
            total_emissions = codebase_emissions + scanning_emissions
            ai_co2 = sum(i.get('estimated_co2_g', 0) for i in sorted_issues
                         if i.get('category') == 'ai_sustainability')

            summary_msg = (
                f'Total Violations: {total_violations} | '
                f'Critical: {critical_count} | High: {high_count} | '
                f'Medium: {medium_count} | Low: {low_count} | '
                f'Avg Effort: {avg_effort} | CO2: {codebase_emissions:.9f}kg'
            )
            if has_ai:
                summary_msg += f' | AI CO2 est.: {ai_co2:.4f}g'

            writer.writerow({
                'file': 'SUMMARY',
                'line': '',
                'rule_id': '',
                'severity': '',
                'message': summary_msg,
                'energy_factor': f'{total_emissions:.9f}kg',
                'effort': 'varies',
                'snippet': '',
                'remediation': '',
            })

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
    # ... (same as before) ...
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
            self.output_path = str(sanitize_path(output_path, allow_absolute=True))
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

        # Security: Escape project name for HTML
        safe_project_name = html.escape(project_name)

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

        # Pre-calculate JSON strings for charts to avoid backslashes in f-strings
        file_labels_json = json.dumps(list(by_file.keys())).replace('<', '\\u003c').replace('>', '\\u003e')
        file_counts_json = json.dumps([len(issues) for issues in by_file.values()])

        # Group by rule ID for the new chart
        rule_counts = {}
        for issue in issues:
            rule_id = issue.get('id', 'unknown')
            if rule_id not in rule_counts:
                rule_counts[rule_id] = 0
            rule_counts[rule_id] += 1

        sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
        rule_labels_json = json.dumps([r[0] for r in sorted_rules]).replace('<', '\\u003c').replace('>', '\\u003e')
        rule_counts_json = json.dumps([r[1] for r in sorted_rules])

        # Build HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Green-AI Report - {safe_project_name}</title>
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

        .controls {{
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #eee;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .search-box, .filter-box {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .search-box input, .filter-box select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
            outline: none;
        }}

        .search-box input:focus, .filter-box select:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
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
            <p>Project: <strong>{safe_project_name}</strong></p>
            <div class="timestamp">Generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        </header>
        
        <div class="summary">
            <div class="metric">
                <h3>Total Violations</h3>
                <div class="value" id="totalViolations">{len(issues)}</div>
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

        <div class="controls">
            <div class="search-box">
                <label for="searchInput">🔍 Search:</label>
                <input type="text" id="searchInput" placeholder="Search files, rules, or messages...">
            </div>
            <div class="filter-box">
                <label for="severityFilter">Filter by Severity:</label>
                <select id="severityFilter">
                    <option value="all">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="info">Info</option>
                </select>
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
                     <div class="chart-container">
                        <h3>By Rule</h3>
                        <canvas id="ruleChart"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Detailed Violations</h2>
                <div>
"""

        # Add file sections with violations
        for file_path, file_issues in sorted_files:
            safe_file_path = html.escape(file_path)
            html_content += f"""
                <div class="file-section">
                    <div class="file-name">📄 {safe_file_path}</div>
                    <div style="font-size: 0.9em; color: #666; margin-bottom: 10px;">
                        {len(file_issues)} violation(s)
                    </div>
"""

            for issue in sorted(file_issues, key=lambda x: x.get('line', 0)):
                severity = issue.get('severity', 'info').lower()
                effort = html.escape(CSVExporter._get_effort(issue))
                safe_rule_id = html.escape(issue.get('id', 'unknown'))
                safe_message = html.escape(issue.get('message', 'No message'))
                safe_line = html.escape(str(issue.get('line', '?')))
                html_content += f"""
                    <div class="violation-item severity-{severity}">
                        <div class="violation-line">Line {safe_line}</div>
                        <div class="violation-message">
                            <strong>{safe_rule_id}</strong><br>
                            {safe_message}
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
        const fileLabels = {file_labels_json};
        const fileCounts = {file_counts_json};
        
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

        // Rule Chart
        const ruleCtx = document.getElementById('ruleChart').getContext('2d');
        const ruleLabels = {rule_labels_json};
        const ruleCounts = {rule_counts_json};

        new Chart(ruleCtx, {{
            type: 'bar',
            data: {{
                labels: ruleLabels.slice(0, 10),
                datasets: [{{
                    label: 'Violations',
                    data: ruleCounts.slice(0, 10),
                    backgroundColor: '#8b5cf6',
                    borderColor: '#8b5cf6',
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

        // Search and Filter Logic
        const searchInput = document.getElementById('searchInput');
        const severityFilter = document.getElementById('severityFilter');
        const violationItems = document.querySelectorAll('.violation-item');
        const fileSections = document.querySelectorAll('.file-section');
        const totalViolationsElement = document.getElementById('totalViolations');

        function filterViolations() {{
            const searchTerm = searchInput.value.toLowerCase();
            const selectedSeverity = severityFilter.value.toLowerCase();
            let visibleCount = 0;

            fileSections.forEach(section => {{
                let hasVisibleViolations = false;
                const items = section.querySelectorAll('.violation-item');

                items.forEach(item => {{
                    const text = item.textContent.toLowerCase();
                    const severityClass = Array.from(item.classList).find(c => c.startsWith('severity-'));
                    const severity = severityClass ? severityClass.replace('severity-', '') : '';

                    const matchesSearch = text.includes(searchTerm);
                    const matchesSeverity = selectedSeverity === 'all' || severity === selectedSeverity;

                    if (matchesSearch && matchesSeverity) {{
                        item.style.display = 'grid';
                        hasVisibleViolations = true;
                        visibleCount++;
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});

                if (hasVisibleViolations) {{
                    section.style.display = 'block';
                }} else {{
                    section.style.display = 'none';
                }}
            }});

            totalViolationsElement.textContent = visibleCount;
        }}

        searchInput.addEventListener('input', filterViolations);
        severityFilter.addEventListener('change', filterViolations);

    </script>
</body>
</html>
"""

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return self.output_path
