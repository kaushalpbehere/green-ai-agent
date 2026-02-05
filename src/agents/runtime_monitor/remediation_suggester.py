# runtime_monitor/remediation_suggester.py
"""
Suggests remediations based on identified patterns.
"""

class RemediationSuggester:
    def __init__(self):
        self.suggestions = {
            "high_cpu_usage": [
                "Optimize loops: Use vectorization or parallel processing.",
                "Reduce computational complexity: Cache results or use more efficient algorithms.",
                "Profile code: Use tools like cProfile to identify bottlenecks."
            ],
            "high_memory_usage": [
                "Use generators instead of lists for large data.",
                "Optimize data structures: Switch to more memory-efficient types.",
                "Implement garbage collection hints."
            ],
            "high_emissions": [
                "Schedule computations during off-peak hours.",
                "Use energy-efficient hardware or cloud instances.",
                "Optimize code to reduce execution time."
            ]
        }

    def suggest(self, patterns):
        """Generate remediation suggestions."""
        remediations = []
        for pattern in patterns:
            pattern_type = pattern["type"]
            if pattern_type in self.suggestions:
                remediations.extend(self.suggestions[pattern_type])
        return list(set(remediations))  # Remove duplicates