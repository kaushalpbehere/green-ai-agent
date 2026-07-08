"""
PDF Export module for Green-AI using WeasyPrint.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.utils.logger import logger
from src.utils.security import sanitize_path
from src.core.export.charts import ChartGenerator

# Default output directory
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / 'output'
TEMPLATE_DIR = Path(__file__).parent / 'templates'


class PDFExporter:
    """Export scan results to PDF format."""

    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize PDF exporter.

        Args:
            output_path: Path to write PDF file. If None, defaults to 'output/green-ai-report.pdf'
        """
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if output_path:
            self.output_path = str(sanitize_path(output_path, allow_absolute=True))
        else:
            self.output_path = str(OUTPUT_DIR / 'green-ai-report.pdf')

    def export(self, results: Dict[str, Any], project_name: str = 'Scan') -> str:
        """
        Export scan results to PDF file.

        Args:
            results: Scan results dictionary
            project_name: Name of the project being scanned

        Returns:
            Path to generated PDF file
        """
        try:
            import weasyprint
        except ImportError:
            logger.error("WeasyPrint not installed. Cannot export PDF.")
            return ""

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
        sorted_files = dict(sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True))

        # Prepare Top 5 files for chart
        top_files = dict(list(sorted_files.items())[:5])
        top_files_data = {k: len(v) for k, v in top_files.items()}

        # Generate Charts
        severity_chart = ChartGenerator.generate_pie_chart(severity_counts, "Severity Distribution")
        top_files_chart = ChartGenerator.generate_bar_chart(top_files_data, "Top Violations by File")

        # Emissions
        codebase_emissions = results.get('codebase_emissions', 0)
        scanning_emissions = results.get('scanning_emissions', 0)
        total_emissions = codebase_emissions + scanning_emissions

        # Prepare context for template
        context = {
            'project_name': project_name,
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_violations': len(issues),
            'critical_count': severity_counts['critical'],
            'affected_files': len(by_file),
            'codebase_emissions': codebase_emissions,
            'scanning_emissions': scanning_emissions,
            'total_emissions': total_emissions,
            'files': sorted_files,
            'severity_chart': severity_chart,
            'top_files_chart': top_files_chart
        }

        # Render HTML
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('pdf_report.html')
        html_content = template.render(**context)

        # Generate PDF
        try:
            weasyprint.HTML(string=html_content).write_pdf(self.output_path)
            logger.info(f"PDF report exported to {self.output_path}")
            return self.output_path
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise e
