"""
Codebase Emission Analyzer

Analyzes Python code to estimate the carbon emissions it would produce if executed.
Uses code complexity metrics (loop depth, recursion, memory usage) to estimate energy consumption.
"""

import ast
import re
from typing import Dict, Tuple, List
from dataclasses import dataclass
from src.core.calibration import CalibrationAgent


@dataclass
class ComplexityMetrics:
    """Metrics to measure code complexity and energy consumption."""
    lines_of_code: int
    cyclomatic_complexity: int  # Decision points (if/for/while)
    max_nesting_depth: int  # Maximum nesting level
    function_count: int
    class_count: int
    recursive_functions: set  # Names of recursive functions
    memory_usage_estimate: float  # Estimated peak memory in MB
    loop_iterations_estimate: int  # Estimated total iterations
    has_io_operations: bool  # File/network I/O detected
    has_expensive_operations: bool  # Sorting, searching, regex
    
    def calculate_complexity_score(self) -> float:
        """Calculate a composite complexity score (0-100)."""
        score = 0.0
        
        # Lines of code contribution (max 20 points)
        loc_score = min(20, (self.lines_of_code / 1000) * 20)
        score += loc_score
        
        # Cyclomatic complexity contribution (max 25 points)
        cc_score = min(25, (self.cyclomatic_complexity / 50) * 25)
        score += cc_score
        
        # Nesting depth contribution (max 15 points)
        depth_score = min(15, (self.max_nesting_depth / 10) * 15)
        score += depth_score
        
        # Loop iterations contribution (max 20 points)
        loop_score = min(20, (self.loop_iterations_estimate / 100000) * 20)
        score += loop_score
        
        # Function/class count contribution (max 10 points)
        entity_score = min(10, ((self.function_count + self.class_count) / 100) * 10)
        score += entity_score
        
        # I/O operations bonus (5 points)
        if self.has_io_operations:
            score += 5
        
        # Expensive operations bonus (5 points)
        if self.has_expensive_operations:
            score += 5
        
        # Recursion penalty (up to -10 points for inefficient recursion)
        if self.recursive_functions:
            score += min(10, len(self.recursive_functions) * 2)
        
        return min(100, score)


class CodeComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze Python code complexity."""
    
    def __init__(self):
        self.cyclomatic_complexity = 1
        self.max_nesting_depth = 0
        self.current_depth = 0
        self.function_count = 0
        self.class_count = 0
        self.recursive_functions = set()
        self.function_names = set()
        self.current_function_calls = set()
        self.current_function = None
        self.has_io_operations = False
        self.has_expensive_operations = False
        self.loop_iterations_estimate = 0
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions and recursion."""
        self.function_count += 1
        self.function_names.add(node.name)
        
        prev_function = self.current_function
        prev_calls = self.current_function_calls
        
        self.current_function = node.name
        self.current_function_calls = set()
        
        self.generic_visit(node)
        
        # Check for recursion
        if node.name in self.current_function_calls:
            self.recursive_functions.add(node.name)
        
        self.current_function = prev_function
        self.current_function_calls = prev_calls
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions."""
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If) -> None:
        """Track if statements (cyclomatic complexity)."""
        self.cyclomatic_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_For(self, node: ast.For) -> None:
        """Track for loops."""
        self.cyclomatic_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        
        # Try to estimate loop iterations
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == 'range' and node.iter.args:
                    arg = node.iter.args[0]
                    if isinstance(arg, ast.Constant):
                        self.loop_iterations_estimate += arg.value
                    elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                        self.loop_iterations_estimate += 1000  # Estimate
        
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_While(self, node: ast.While) -> None:
        """Track while loops."""
        self.cyclomatic_complexity += 1
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)
        self.loop_iterations_estimate += 1000  # Estimate
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Track exception handlers."""
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Track function calls and I/O/expensive operations."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Track recursion
            if self.current_function and func_name == self.current_function:
                self.current_function_calls.add(func_name)
            
            # Detect I/O operations
            if func_name in ('open', 'read', 'write', 'requests', 'urlopen', 'socket'):
                self.has_io_operations = True
            
            # Detect expensive operations
            if func_name in ('sort', 'sorted', 'search', 're.compile', 'json.dumps', 'pickle.dumps'):
                self.has_expensive_operations = True
        
        self.generic_visit(node)


class EmissionAnalyzer:
    """
    Analyzes code to estimate carbon emissions from execution.
    
    CALIBRATION NOTES (v0.2):
    - BASELINE: 0.00000001 kg CO2 per line is too high for MVP
    - TIER 1 violations (nested loops, I/O): 100-1000x energy multiplier
    - TIER 2 violations (memory, complexity): 3-100x energy multiplier
    - Calibrated against typical Python/JavaScript execution profiles
    """
    
    # TIER 1: Critical violations (direct energy impact)
    # Empirical factors based on energy profiling
    NESTED_LOOP_MULTIPLIER = 100  # 3+ levels: 100x more energy
    REDUNDANT_COMPUTATION_MULTIPLIER = 10  # 10x waste
    MEMORY_OPERATION_MULTIPLIER = 3  # 2-3x more energy than CPU
    IO_OPERATION_OVERHEAD = 1000  # 1000x more than CPU op
    
    # TIER 2: Code quality violations
    RESOURCE_LEAK_PENALTY = 2  # 2x for persistent resource
    ALGORITHM_COMPLEXITY_MULTIPLIER = 100  # O(n²) vs O(n)
    
    # Baseline calibration
    BASELINE_CO2_PER_1000_LINES = 0.0000001  # kg CO2 for 1000 LOC
    COMPLEXITY_SCORE_MULTIPLIER = 0.00000001  # Per complexity point
    
    def __init__(self, calibration_coefficient: float = 1.0):
        self.total_codebase_emissions = 0.0
        self.per_issue_emissions = {}
        self.calibration_coefficient = calibration_coefficient
    
    def analyze_file(self, file_path: str, content: str) -> ComplexityMetrics:
        """Analyze a Python file for complexity metrics."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Return default metrics if syntax error
            return ComplexityMetrics(
                lines_of_code=content.count('\n') + 1,
                cyclomatic_complexity=1,
                max_nesting_depth=0,
                function_count=0,
                class_count=0,
                recursive_functions=set(),
                memory_usage_estimate=0.0,
                loop_iterations_estimate=0,
                has_io_operations=False,
                has_expensive_operations=False
            )
        
        analyzer = CodeComplexityAnalyzer()
        analyzer.visit(tree)
        
        # Estimate memory usage
        memory_estimate = self._estimate_memory_usage(content)
        
        metrics = ComplexityMetrics(
            lines_of_code=content.count('\n') + 1,
            cyclomatic_complexity=analyzer.cyclomatic_complexity,
            max_nesting_depth=analyzer.max_nesting_depth,
            function_count=analyzer.function_count,
            class_count=analyzer.class_count,
            recursive_functions=analyzer.recursive_functions,
            memory_usage_estimate=memory_estimate,
            loop_iterations_estimate=analyzer.loop_iterations_estimate,
            has_io_operations=analyzer.has_io_operations,
            has_expensive_operations=analyzer.has_expensive_operations
        )
        
        return metrics
    
    def _estimate_memory_usage(self, content: str) -> float:
        """Estimate memory usage from code patterns."""
        memory_mb = 10.0  # Base memory
        
        # Check for large data structures
        if re.search(r'\[.*\].*\*\s*[0-9]{4,}', content):
            memory_mb += 100  # Large lists
        
        if re.search(r'dict\(|{.*:.*}', content):
            memory_mb += 50  # Dictionaries
        
        if re.search(r'\.read\(\)|\.readlines\(\)', content):
            memory_mb += 200  # File reading
        
        if re.search(r'DataFrame|numpy|np\.array', content):
            memory_mb += 500  # Data science libraries
        
        return memory_mb
    
    def estimate_emissions(self, metrics: ComplexityMetrics, language: str = 'python') -> float:
        """
        Estimate carbon emissions for code execution based on complexity metrics.
        
        APPROACH:
        1. Start with baseline (LOC-based)
        2. Apply multipliers for complexity factors
        3. Weight by impact severity
        
        Returns kg CO2
        """
        emissions = 0.0
        
        # 1. BASELINE: Lines of code
        # 1000 LOC = 0.0000001 kg CO2
        emissions += (metrics.lines_of_code / 1000) * self.BASELINE_CO2_PER_1000_LINES
        
        # 2. COMPLEXITY SCORE (0-100)
        # Higher complexity = more CPU branches = more energy
        complexity_score = metrics.calculate_complexity_score()
        emissions += (complexity_score / 100) * self.COMPLEXITY_SCORE_MULTIPLIER
        
        # 3. LOOP COMPLEXITY (most impactful)
        # Estimated loop iterations directly increase energy
        loop_energy = (metrics.loop_iterations_estimate / 100000) * 0.00000001
        emissions += loop_energy
        
        # 4. I/O OPERATIONS (very expensive)
        if metrics.has_io_operations:
            emissions += 0.0000001  # Each I/O costs significant energy
        
        # 5. MEMORY OPERATIONS (2-3x expensive)
        memory_energy = (metrics.memory_usage_estimate / 100) * 0.00000001
        emissions += memory_energy
        
        # 6. RECURSION PENALTY
        if metrics.recursive_functions:
            emissions += len(metrics.recursive_functions) * 0.00000001
        
        if metrics.has_expensive_operations:
            emissions += 0.00000001
        
        # 8. APPLY SYSTEM CALIBRATION
        emissions *= self.calibration_coefficient
        
        return max(emissions, 0.00000001)  # Minimum threshold
    
    def analyze_codebase(self, file_contents: Dict[str, str]|List[Tuple[str, str]]) -> Tuple[float, Dict[str, float]]:
        """
        Analyze codebase for emissions.
        
        Args:
            file_contents: Dictionary of path:content OR List/Iterator of (path, content)
        
        Returns:
            Tuple of (total_emissions, per_file_emissions)
        """
        total_emissions = 0.0
        per_file_emissions = {}
        
        # Handle both dict and iterable
        items = file_contents.items() if isinstance(file_contents, dict) else file_contents
        
        for file_path, content in items:
            if file_path.endswith('.py'):
                metrics = self.analyze_file(file_path, content)
                emissions = self.estimate_emissions(metrics)
                per_file_emissions[file_path] = emissions
                total_emissions += emissions
        
        return total_emissions, per_file_emissions
    
    def add_to_analysis(self, file_path: str, content: str) -> float:
        """
        Incrementally add a file to the total codebase analysis.
        Useful for lazy loading scenarios where we don't want to store all contents.
        """
        if file_path.endswith('.py'):
            metrics = self.analyze_file(file_path, content)
            emissions = self.estimate_emissions(metrics)
            self.total_codebase_emissions += emissions
            return emissions
        return 0.0
    
    def get_per_line_emissions(self, issues: List[Dict], total_emissions: float) -> List[Dict]:
        """
        Distribute total emissions across issues based on their lines and severity.
        
        Args:
            issues: List of issues found during scan
            total_emissions: Total codebase emissions in kg CO2
        
        Returns:
            Updated issue list with emissions field
        """
        if not issues or total_emissions == 0:
            for issue in issues:
                issue['codebase_emissions'] = 0.0
            return issues
        
        # Weight issues by severity and line number
        severity_weights = {'high': 3, 'medium': 2, 'low': 1}
        total_weight = sum(severity_weights.get(issue.get('severity', 'low'), 1) for issue in issues)
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            weight = severity_weights.get(severity, 1)
            
            # Distribute emissions proportionally
            issue_emissions = (weight / total_weight) * total_emissions if total_weight > 0 else 0
            issue['codebase_emissions'] = issue_emissions
        
        return issues


# Convenience functions
def analyze_code_complexity(file_path: str, content: str) -> ComplexityMetrics:
    """Analyze code complexity from file content."""
    analyzer = EmissionAnalyzer()
    return analyzer.analyze_file(file_path, content)


def estimate_codebase_emissions(file_contents: Dict[str, str]) -> float:
    """Estimate total emissions for a codebase."""
    analyzer = EmissionAnalyzer()
    total, _ = analyzer.analyze_codebase(file_contents)
    return total
