import logging
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO):
    """
    Standardized logger setup for Green-AI.
    
    All logs are stored in output/logs/ by default.
    """
    # 1. Determine logs directory (always output/logs)
    # Using absolute path relative to project root (2 levels up from src/utils)
    base_dir = Path(__file__).parent.parent.parent
    logs_dir = base_dir / 'output' / 'logs'
    
    # 2. Ensure logs directory exists
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # Fallback to current directory if output/logs is restricted
        print(f"Warning: Could not create log directory {logs_dir}: {e}", file=sys.stderr)
        logs_dir = Path.cwd() / 'logs'
        logs_dir.mkdir(exist_ok=True)

    # 3. Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 4. Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clean up existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # 5. File Handler (Optional)
    if log_file:
        file_path = logs_dir / log_file
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 6. Console Handler (for non-dashboard context or errors)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Single instance of core logger
logger = setup_logger('green-ai', 'app.log')
