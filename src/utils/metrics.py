from typing import List, Dict, Any

def calculate_average_grade(grades: List[str]) -> str:
    """
    Calculate average grade from list of letter grades.

    Args:
        grades: List of letter grades (A-F)

    Returns:
        Average grade letter (A-F) or 'N/A'
    """
    if not grades:
        return 'N/A'

    grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'F': 1}
    grade_points = [grade_values.get(g, 0) for g in grades if g in grade_values]

    if not grade_points:
        return 'N/A'

    avg = sum(grade_points) / len(grade_points)

    if avg >= 4.5:
        return 'A'
    elif avg >= 3.5:
        return 'B'
    elif avg >= 2.5:
        return 'C'
    elif avg >= 1.5:
        return 'D'
    else:
        return 'F'

def calculate_projects_grade(projects: List[Any]) -> str:
    """
    Calculate average grade from list of Project objects.

    Args:
        projects: List of Project objects (must have get_grade() method)

    Returns:
        Average grade letter (A-F) or 'N/A'
    """
    if not projects:
        return "N/A"

    grades = [p.get_grade() for p in projects if hasattr(p, 'get_grade')]
    return calculate_average_grade(grades)
