import pytest
from src.core.quality.metrics import DuplicationDetector

def test_type1_duplication():
    detector = DuplicationDetector()
    content1 = """
def test():
    a = 1
    b = 2
    c = a + b
    return c
"""
    content2 = """
def test():
    a = 1
    b = 2
    c = a + b
    return c
"""
    detector.add_file("file1.py", content1)
    detector.add_file("file2.py", content2)
    duplications = detector.detect()
    assert len(duplications["type_1"]) == 1
    assert len(duplications["type_2"]) == 0

def test_type2_duplication():
    detector = DuplicationDetector()
    content1 = """
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
    content2 = """
def calculate_metrics(items):
    output = []
    for x in items:
        output.append(x * 2)
    return output
"""
    detector.add_file("file1.py", content1)
    detector.add_file("file2.py", content2)
    duplications = detector.detect()
    assert len(duplications["type_1"]) == 0
    assert len(duplications["type_2"]) == 1

def test_no_duplication():
    detector = DuplicationDetector()
    content1 = """
def func1():
    a = 1
    return a
"""
    content2 = """
def func2():
    b = 2
    c = 3
    return b + c
"""
    detector.add_file("file1.py", content1)
    detector.add_file("file2.py", content2)
    duplications = detector.detect()
    assert len(duplications["type_1"]) == 0
    assert len(duplications["type_2"]) == 0

from src.core.quality.metrics import DeadCodeDetector

def test_dead_code_detector_with_unused():
    detector = DeadCodeDetector()
    content = """
def used_function():
    print("used")

def unused_function():
    print("unused")

used_function()
"""
    results = detector.analyze_content("test.py", content)
    # vulture might find 'unused_function'
    unused_names = [res["name"] for res in results]
    assert "unused_function" in unused_names

def test_dead_code_detector_without_unused():
    detector = DeadCodeDetector()
    content = """
def used_function():
    print("used")

used_function()
"""
    results = detector.analyze_content("test.py", content)
    assert len(results) == 0
