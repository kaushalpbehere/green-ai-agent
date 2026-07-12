# runtime_monitor/data_collector.py
"""
Collects runtime data from monitors and correlates with code execution.
"""

import time
import tempfile
import importlib.util
import os
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
        for _ in range(iterations):
            # Execute code with monitoring
            # This is simplified; in practice, use exec or subprocess
            exec_globals = {}
            # Write code snippet to a temp file and import dynamically
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_f:
                temp_f.write(code_snippet)
                temp_path = temp_f.name

            try:
                spec = importlib.util.spec_from_file_location("dynamic_snippet", temp_path)
                dynamic_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(dynamic_module)
                exec_globals = dynamic_module.__dict__
            finally:
                os.remove(temp_path)

            # Assuming the code defines a function 'run'
            if 'run' in exec_globals:
                instrumented_run = self.instrument_execution(exec_globals['run'])
                _, report = instrumented_run()
                reports.append(report)
        return reports

    def collect_from_command(self, command):
        """Execute command and collect data."""
        self.monitor.start_monitoring()
        start_time = time.time()

        import subprocess
        subprocess.run(command, capture_output=True)

        end_time = time.time()
        self.monitor.stop_monitoring()
        execution_time = end_time - start_time
        report = self.monitor.get_report()
        report["execution_time_sec"] = execution_time
        return report
