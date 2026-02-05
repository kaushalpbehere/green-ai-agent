# runtime_monitor/pattern_analyzer.py
"""
Analyzes runtime data to identify energy-wasteful patterns.
"""

class PatternAnalyzer:
    def __init__(self):
        self.thresholds = {
            "high_cpu": 80,  # %
            "high_memory": 90,  # %
            "high_emissions": 0.1  # kg CO2
        }

    def analyze(self, reports):
        """Analyze list of runtime reports."""
        patterns = []
        for report in reports:
            if report.get("avg_cpu_percent", 0) > self.thresholds["high_cpu"]:
                patterns.append({
                    "type": "high_cpu_usage",
                    "severity": "high",
                    "description": "High CPU usage detected, potential inefficient loops or computations."
                })
            if report.get("avg_memory_percent", 0) > self.thresholds["high_memory"]:
                patterns.append({
                    "type": "high_memory_usage",
                    "severity": "medium",
                    "description": "High memory usage, consider optimizing data structures."
                })
            if report.get("emissions_kg", 0) > self.thresholds["high_emissions"]:
                patterns.append({
                    "type": "high_emissions",
                    "severity": "high",
                    "description": "High carbon emissions, review energy-intensive operations."
                })
        return patterns