# runtime_monitor/scaphandre_integration.py
"""
Integration with Scaphandre for general energy consumption monitoring.
"""

import subprocess
import json
import time
import psutil

class ScaphandreMonitor:
    def __init__(self, scaphandre_path="scaphandre", output_file=None):
        from pathlib import Path
        if output_file is None:
            # Default to data folder
            output_dir = Path(__file__).parent.parent.parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_file = str(output_dir / "scaphandre_metrics.json")
        self.scaphandre_path = scaphandre_path
        self.output_file = output_file
        self.process = None

    def start_monitoring(self, pid=None):
        """Start Scaphandre monitoring for a specific process or system-wide."""
        cmd = [self.scaphandre_path, "json", "--step", "30"]
        if pid:
            cmd.extend(["--process", str(pid)])
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.start_time = time.time()

    def stop_monitoring(self):
        """Stop monitoring and collect data."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.end_time = time.time()
            # Parse output (assuming JSON output)
            output, _ = self.process.communicate()
            try:
                self.metrics = json.loads(output.decode())
            except:
                self.metrics = {}

    def get_report(self):
        """Return energy consumption report."""
        duration = self.end_time - self.start_time
        energy_consumed = self.metrics.get("energy_consumed_wh", 0)  # Example metric
        return {
            "energy_wh": energy_consumed,
            "duration_sec": duration,
            "power_watts_avg": energy_consumed / (duration / 3600) if duration else 0
        }