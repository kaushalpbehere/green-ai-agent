# runtime_monitor/codecarbon_integration.py
"""
Integration with CodeCarbon for Python code emission tracking.
"""

from codecarbon import EmissionsTracker
import psutil
import time
import os
from pathlib import Path

class CodeCarbonMonitor:
    def __init__(self, output_file=None):
        if output_file is None:
            # Default to output folder
            output_dir = Path(__file__).parent.parent.parent.parent / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = str(output_dir / "emissions.csv")
        self.tracker = EmissionsTracker(output_file=output_file)
        self.cpu_usage = []
        self.memory_usage = []

    def start_monitoring(self):
        self.tracker.start()
        self.start_time = time.time()

    def stop_monitoring(self):
        self.tracker.stop()
        self.end_time = time.time()

    def collect_system_metrics(self):
        """Collect CPU and memory usage."""
        self.cpu_usage.append(psutil.cpu_percent(interval=1))
        self.memory_usage.append(psutil.virtual_memory().percent)

    def get_report(self):
        """Return emissions and system metrics report."""
        emissions = self.tracker._emissions  # Access internal emissions data
        duration = self.end_time - self.start_time
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        avg_memory = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        return {
            "emissions_kg": emissions,
            "duration_sec": duration,
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory
        }