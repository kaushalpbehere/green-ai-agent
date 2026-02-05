# tests/test_runtime_monitor.py
"""
Unit tests for runtime monitoring module.
"""

import unittest
from src.agents.runtime_monitor.pattern_analyzer import PatternAnalyzer

class TestPatternAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PatternAnalyzer()

    def test_high_cpu_detection(self):
        reports = [{"avg_cpu_percent": 85}]
        patterns = self.analyzer.analyze(reports)
        self.assertTrue(any(p["type"] == "high_cpu_usage" for p in patterns))

    def test_no_patterns(self):
        reports = [{"avg_cpu_percent": 50, "avg_memory_percent": 60, "emissions_kg": 0.05}]
        patterns = self.analyzer.analyze(reports)
        self.assertEqual(len(patterns), 0)

if __name__ == "__main__":
    unittest.main()