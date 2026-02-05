# runtime_monitor/main.py
"""
Main entry point for runtime monitoring in GASA.
"""

from .data_collector import RuntimeDataCollector
from .pattern_analyzer import PatternAnalyzer
from .remediation_suggester import RemediationSuggester

def run_runtime_analysis(code_snippet, language="python", iterations=1):
    """Run full runtime analysis pipeline."""
    collector = RuntimeDataCollector(language)
    reports = collector.collect_data(code_snippet, iterations)
    analyzer = PatternAnalyzer()
    patterns = analyzer.analyze(reports)
    suggester = RemediationSuggester()
    remediations = suggester.suggest(patterns)
    return {
        "reports": reports,
        "patterns": patterns,
        "remediations": remediations
    }

if __name__ == "__main__":
    # Example usage
    sample_code = """
def run():
    import time
    for i in range(1000000):
        _ = i ** 2
    time.sleep(1)
"""
    result = run_runtime_analysis(sample_code)
    print(result)