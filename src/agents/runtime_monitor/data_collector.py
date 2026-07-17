# runtime_monitor/data_collector.py
"""
Collects runtime data from monitors and correlates with code execution.
"""

import time
from .codecarbon_integration import CodeCarbonMonitor
from .scaphandre_integration import ScaphandreMonitor


class RuntimeDataCollector:
    def __init__(self, language="python"):
        self.language = language
        if language == "python":
            self.monitor = CodeCarbonMonitor()
        else:
            self.monitor = ScaphandreMonitor()

    def instrument_execution(self, func):
        """Decorator to instrument function execution."""
        def wrapper(*args, **kwargs):
            self.monitor.start_monitoring()
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            self.monitor.stop_monitoring()
            execution_time = end_time - start_time
            report = self.monitor.get_report()
            report["execution_time_sec"] = execution_time
            # Store or return report
            return result, report
        return wrapper

    def collect_data(self, code_snippet, iterations=1):
        """Execute code snippet multiple times and collect data."""
        reports = []
        import tempfile
        import importlib.util
        import os

        # Write snippet to temporary file to avoid exec()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code_snippet)
            temp_path = f.name

        try:
            for _ in range(iterations):
                # Load module dynamically
                spec = importlib.util.spec_from_file_location("dynamic_module", temp_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # nosec B102

                # Assuming the code defines a function 'run'
                if hasattr(module, 'run'):
                    instrumented_run = self.instrument_execution(module.run)
                    _, report = instrumented_run()
                    reports.append(report)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return reports

    def collect_from_command(self, command):
        """Execute command and collect data."""
        self.monitor.start_monitoring()
        start_time = time.time()

        import subprocess  # nosec B404
        import shlex

        # Ensure command is a list for safer execution
        if isinstance(command, str):
            cmd = shlex.split(command)
        else:
            cmd = command

        subprocess.run(cmd, capture_output=True, shell=False, check=True)  # nosec B603

        end_time = time.time()
        self.monitor.stop_monitoring()
        execution_time = end_time - start_time
        report = self.monitor.get_report()
        report["execution_time_sec"] = execution_time
        return report
