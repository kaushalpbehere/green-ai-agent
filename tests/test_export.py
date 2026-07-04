"""
Unit tests for export module (CSV and HTML export functionality)
"""

import pytest
import os
import csv
import tempfile
from src.core.export import CSVExporter, HTMLReporter
from pydantic import ValidationError
import json


