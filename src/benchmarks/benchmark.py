"""
Performance Benchmarking for GASA
"""

import time
import subprocess
import sys
import os
from codecarbon import EmissionsTracker

def benchmark_scan(target='tests/', iterations=3):
    """Benchmark scanning performance"""
    times = []
    emissions = []
    
    for i in range(iterations):
        print(f"Benchmark iteration {i+1}/{iterations}")
        
        tracker = EmissionsTracker()
        tracker.start()
        start_time = time.time()
        
        # Run scan
        result = subprocess.run([
            sys.executable, 'src/main.py', 'scan', target
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/../')
        
        end_time = time.time()
        scan_emissions = tracker.stop()
        
        if result.returncode == 0:
            times.append(end_time - start_time)
            emissions.append(scan_emissions)
            print(".2f")
        else:
            print(f"Scan failed: {result.stderr}")
    
    if times:
        avg_time = sum(times) / len(times)
        avg_emissions = sum(emissions) / len(emissions)
        print("\nBenchmark Results:")
        print(".2f")
        print(".6f")
    else:
        print("No successful scans")

if __name__ == '__main__':
    benchmark_scan()