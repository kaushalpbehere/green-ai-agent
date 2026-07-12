"""
Performance Benchmarking for Green-AI
"""

import time
import subprocess
import sys
from pathlib import Path
from codecarbon import EmissionsTracker


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def benchmark_scan(target: str = 'tests/', iterations: int = 3) -> None:
    """Benchmark scanning performance."""
    times: list[float] = []
    emissions: list[float] = []

    for i in range(iterations):
        print(f"Benchmark iteration {i + 1}/{iterations}")

        tracker = EmissionsTracker()
        tracker.start()
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', 'scan', target],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )

        end_time = time.time()
        scan_emissions = tracker.stop() or 0.0

        if result.returncode == 0:
            elapsed = end_time - start_time
            times.append(elapsed)
            emissions.append(scan_emissions)
            print(f"  iteration {i + 1}: {elapsed:.2f}s, {scan_emissions:.6f} kg CO2")
        else:
            print(f"Scan failed: {result.stderr}")

    if times:
        avg_time = sum(times) / len(times)
        avg_emissions = sum(emissions) / len(emissions)
        print("\nBenchmark Results:")
        print(f"  Average time:      {avg_time:.2f}s over {len(times)} runs")
        print(f"  Average emissions: {avg_emissions:.6f} kg CO2 per scan")
    else:
        print("No successful scans")


if __name__ == '__main__':
    benchmark_scan()
