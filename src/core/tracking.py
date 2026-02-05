"""
Emissions Tracking Module - Phase 2.0.1

Provides pluggable emissions tracking with optional profiling.
- NoOpTracker: 0 overhead (default)
- ProfilingTracker: Full monitoring (with --profile flag)

This module ensures Green-AI doesn't waste resources on monitoring itself!
"""

import time
from typing import Dict, Optional
from abc import ABC, abstractmethod


class BaseTracker(ABC):
    """Abstract base class for emissions tracking."""
    
    @abstractmethod
    def start(self) -> None:
        """Start tracking emissions."""
        pass
    
    @abstractmethod
    def stop(self) -> Dict[str, float]:
        """Stop tracking and return emissions data.
        
        Returns:
            Dict with keys: 'emissions' (kg CO2), 'cpu' (%), 'memory' (MB)
        """
        pass
    
    @abstractmethod
    def get_emissions(self) -> Optional[float]:
        """Get current emissions estimate in kg CO2."""
        pass


class NoOpTracker(BaseTracker):
    """No-operation tracker with zero overhead.
    
    Used by default for normal scans to avoid monitoring overhead.
    Returns zero values to indicate no tracking.
    """
    
    def __init__(self):
        """Initialize no-op tracker."""
        self.start_time = None
    
    def start(self) -> None:
        """Start tracking (instant, no overhead)."""
        self.start_time = time.time()
    
    def stop(self) -> Dict[str, float]:
        """Stop tracking (instant, no overhead).
        
        Returns:
            Zero values indicating no tracking was performed.
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'emissions': 0.0,
            'cpu': 0.0,
            'memory': 0.0,
            'duration_seconds': elapsed,
            'tracking_enabled': False
        }
    
    def get_emissions(self) -> Optional[float]:
        """Get current emissions (always 0)."""
        return 0.0


class ProfilingTracker(BaseTracker):
    """Wrapper around CodeCarbon for full profiling mode."""
    
    def __init__(self):
        """Initialize profiling tracker with CodeCarbon."""
        self.codecarbon_avail = False
        try:
            from codecarbon import EmissionsTracker
            from pathlib import Path
            
            # Ensure output directory exists
            output_dir = Path(__file__).parent.parent.parent / 'output' / 'emissions'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.emissions_tracker = EmissionsTracker(
                output_dir=str(output_dir),
                output_file='emissions.csv',
                log_level='error'  # Minimize console noise
            )
            self.codecarbon_avail = True
            self.enabled = True
        except ImportError:
            self.emissions_tracker = None
            self.enabled = False
            
    def start(self) -> None:
        """Start tracking."""
        if self.enabled and self.codecarbon_avail:
            self.emissions_tracker.start()
        
        # Track start resources
        self.start_time = time.time()
        try:
            import psutil
            process = psutil.Process()
            self.start_cpu = process.cpu_percent()
            self.start_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            self.start_cpu = 0
            self.start_memory = 0
    
    def stop(self) -> Dict[str, float]:
        """Stop tracking and return data."""
        emissions = 0.0
        
        if self.enabled and self.codecarbon_avail:
            emissions = self.emissions_tracker.stop()
            if emissions is None:
                emissions = 0.0
                
        # Get resource usage
        cpu_usage = 0.0
        memory_usage = 0.0
        try:
            import psutil
            process = psutil.Process()
            cpu_usage = process.cpu_percent()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pass
            
        return {
            'emissions': float(emissions),
            'cpu': cpu_usage,
            'memory': memory_usage,
            'tracking_enabled': True
        }
    
    def get_emissions(self) -> Optional[float]:
        return 0.0


def create_tracker(enable_profiling: bool = False) -> BaseTracker:
    if enable_profiling:
        return ProfilingTracker()
    else:
        return NoOpTracker()
