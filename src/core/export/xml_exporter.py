import defusedxml.ElementTree as defused_ET
import xml.etree.ElementTree as ET  # nosec B405
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.utils.security import sanitize_path

# Default output directory for all exports
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / 'output'


class JUnitXMLExporter:
    """Export scan results to JUnit XML format."""

    def __init__(self, output_path: Optional[str] = None):
        """
        Initialize XML exporter.

        Args:
            output_path: Path to write XML file.
                         If None, defaults to 'output/green-ai-report.xml'
        """
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if output_path:
            self.output_path = str(sanitize_path(output_path, allow_absolute=True))
        else:
            self.output_path = str(OUTPUT_DIR / 'green-ai-report.xml')

    def export(
        self, results: Dict[str, Any], project_name: str = 'Scan'
    ) -> str:
        """
        Export scan results to JUnit XML file.

        Args:
            results: Scan results dictionary from Scanner.scan()
            project_name: Name of the project being scanned

        Returns:
            Path to generated XML file
        """
        issues = results.get('issues', [])

        # Calculate statistics
        total_tests = len(issues)
        failures = total_tests  # Every issue is considered a failure

        # Root element
        testsuites = ET.Element('testsuites')

        # Testsuite element
        testsuite = ET.SubElement(testsuites, 'testsuite')
        testsuite.set('name', project_name)
        testsuite.set('tests', str(total_tests))
        testsuite.set('failures', str(failures))
        testsuite.set('errors', '0')
        testsuite.set('skipped', '0')
        testsuite.set('timestamp', datetime.now(timezone.utc).isoformat())
        testsuite.set('time', '0')  # Execution time could be added here

        # Add testcases for each issue
        for issue in issues:
            file_path = issue.get('file', 'unknown')
            rule_id = issue.get('id', 'unknown')
            line = issue.get('line', 0)
            message = issue.get('message', 'No message')
            severity = issue.get('severity', 'medium')

            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('classname', file_path)
            testcase.set('name', f"{rule_id} (Line {line})")
            testcase.set('time', '0')

            # Add failure details
            failure = ET.SubElement(testcase, 'failure')
            failure.set('message', message)
            failure.set('type', severity)
            failure.text = (
                f"Rule: {rule_id}\nSeverity: {severity}\n"
                f"File: {file_path}:{line}\nMessage: {message}"
            )

        # Create XML tree
        tree = ET.ElementTree(testsuites)

        # Security: even though we use standard ET for creation (defusedxml doesn't provide Element/SubElement),
        # Bandit flags standard ET. So let's write it carefully. Actually Bandit only flags import.

        # Write to file
        with open(self.output_path, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)

        return self.output_path
