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
        for _ in range(iterations):
            # Execute code with monitoring
            # This is simplified; in practice, use exec or subprocess
            exec_globals = {}
            exec(code_snippet, exec_globals)
            # Assuming the code defines a function 'run'
            if 'run' in exec_globals:
                instrumented_run = self.instrument_execution(exec_globals['run'])
                _, report = instrumented_run()
                reports.append(report)
        return reports