import time
import os
import json
import psutil
import platform
import subprocess
from typing import Dict, Any, Optional
from src.utils.logger import logger

class CalibrationAgent:
    """
    Agent responsible for calibrating the emission model based on host hardware performance.
    Runs micro-benchmarks to normalize energy factors.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join('data', 'system_profile.json')
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self.profile = self.load_profile()

    def load_profile(self) -> Dict[str, Any]:
        """Load existing system profile or return default."""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load system profile: {e}")
        return {}

    def run_calibration(self) -> Dict[str, Any]:
        """Execute micro-benchmarks and store results."""
        logger.info("Starting system calibration benchmarks...")
        
        cpu_score = self._benchmark_cpu()
        mem_score = self._benchmark_memory()
        
        # Reference: Baseline machine does ~50,000 sorted() calls in 1s.
        baseline_cpu = 50000
        cpu_coefficient = baseline_cpu / cpu_score if cpu_score > 0 else 1.0
        
        cpu_multiplier = round(cpu_coefficient, 4)
        self.profile = {
            'timestamp': time.time(),
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': os.cpu_count(),
            'total_memory': psutil.virtual_memory().total,
            'benchmarks': {
                'cpu_score': cpu_score,
                'mem_score': mem_score
            },
            'coefficients': {
                'cpu_multiplier': cpu_multiplier,
                'efficiency_tier': self._get_efficiency_tier(cpu_multiplier)
            }
        }
        
        try:
            with open(self.data_path, 'w') as f:
                json.dump(self.profile, f, indent=4)
            logger.info(f"Calibration complete. System Multiplier: {cpu_multiplier}x")
        except Exception as e:
            logger.error(f"Failed to save system profile: {e}")
            
        return self.profile

    def _benchmark_cpu(self) -> float:
        """Measure operations per second for a standard computational task."""
        start = time.time()
        count = 0
        while time.time() - start < 0.5: # Run for 0.5 second
            # More representative: List creation and sorting
            _ = sorted([x for x in range(100)])
            count += 1
        return count * 2 # Normalize to 1s

    def _benchmark_memory(self) -> float:
        """Measure throughput for memory operations (MB/s)."""
        data = bytearray(10 * 1024 * 1024) # 10MB
        start = time.time()
        count = 0
        while time.time() - start < 1.0:
            _ = data[:] # Memory copy
            count += len(data)
        return count / (1024 * 1024)

    def _get_efficiency_tier(self, multiplier: float) -> str:
        if multiplier < 0.5: return "High Efficiency (Cloud/Server)"
        if multiplier < 1.5: return "Standard (Workstation)"
        return "Legacy (Laptop/Old Hardware)"

    def get_coefficient(self) -> float:
        """Get the CPU multiplier for emission calculation."""
        return self.profile.get('coefficients', {}).get('cpu_multiplier', 1.0)
