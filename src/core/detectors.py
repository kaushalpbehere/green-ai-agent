"""
Detection strategies for green software violations.

This module implements AST-based and pattern-based detection methods for each rule.
"""

import ast
import re
from typing import List, Dict, Tuple


class PythonViolationDetector(ast.NodeVisitor):
    """AST visitor to detect green software violations in Python code."""
    
    IO_PATTERNS = {'open', 'read', 'write', 'requests', 'urlopen'}
    REDUNDANT_FUNCS = {'len', 'range', 're.compile', 'datetime.now', 'time.time'}
    BLOCKING_IO = {'requests.get', 'urlopen', 'time.sleep'}

    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []
        self.current_depth = 0
        self.in_loop = False
        self.current_function = None
        self.unused_variables = {}
        self.used_variables = set()
        self.imports = {}
        
    def detect_all(self) -> List[Dict]:
        """Run all detectors and return violations."""
        try:
            tree = ast.parse(self.content)
            self.visit(tree)
            
            # Post-processing for unused detection
            self._detect_unused_variables()
            self._detect_unused_imports()
            
        except SyntaxError:
            pass
        
        return self.violations
    
    def visit_For(self, node: ast.For) -> None:
        """Detect nested loops and I/O in loops."""
        self.current_depth += 1
        
        # Rule: Excessive nesting depth (O(n^2) or worse)
        if self.current_depth >= 2:
            severity = 'critical' if self.current_depth >= 3 else 'major'
            self.violations.append({
                'id': 'no_n2_algorithms',
                'line': node.lineno,
                'severity': severity,
                'message': f'Nesting depth {self.current_depth}: O(n^{self.current_depth}) complexity detected.',
                'pattern_match': 'nested_for_loop'
            })

        # Rule: Inefficient Loop (range(len))
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            if len(node.iter.args) == 1 and isinstance(node.iter.args[0], ast.Call):
                arg_call = node.iter.args[0]
                if isinstance(arg_call.func, ast.Name) and arg_call.func.id == 'len':
                    self.violations.append({
                        'id': 'inefficient_loop',
                        'line': node.lineno,
                        'severity': 'major',
                        'message': 'Using range(len(sequence)) is inefficient. Use enumerate() or zip().',
                        'pattern_match': 'range_len'
                    })
        
        # Rule: Inefficient Lookup (item in list in loop)
        self._check_inefficient_lookups(node)
        
        # Check for I/O and redundant computations in loop
        prev_in_loop = self.in_loop
        self.in_loop = True
        self._check_io_in_loop(node)
        self._check_unnecessary_computation(node)
        
        self.generic_visit(node)
        self.in_loop = prev_in_loop
        self.current_depth -= 1
    
    def visit_While(self, node: ast.While) -> None:
        """Detect while loop violations."""
        self.current_depth += 1
        
        is_infinite = False
        test = node.test
        if isinstance(test, ast.Constant) and test.value is True:
            is_infinite = True
        elif isinstance(test, ast.NameConstant) and test.value is True:
            is_infinite = True
        elif isinstance(test, ast.Name) and test.id == 'True':
            is_infinite = True
            
        if is_infinite:
             is_infinite = True
        
        if is_infinite:
             self.violations.append({
                'id': 'no_infinite_loops',
                'line': node.lineno,
                'severity': 'critical',
                'message': 'Infinite loop detected (while True). Ensure break condition exists.',
                'pattern_match': 'infinite_while'
            })

        if self.current_depth >= 3:
            self.violations.append({
                'id': 'excessive_nesting_depth',
                'line': node.lineno,
                'severity': 'critical',
                'message': f'Nesting depth {self.current_depth}: O(n^{self.current_depth}) complexity detected.',
                'pattern_match': 'nested_while_loop'
            })
        
        prev_in_loop = self.in_loop
        self.in_loop = True
        self._check_io_in_loop(node)
        self._check_unnecessary_computation(node)
        
        self.generic_visit(node)
        self.in_loop = prev_in_loop
        self.current_depth -= 1
    
    def visit_If(self, node: ast.If) -> None:
        """Track if statements for complexity."""
        self.current_depth += 1
        self.generic_visit(node)
        self.current_depth -= 1
    
    def _check_io_in_loop(self, loop_node) -> None:
        """Check if loop contains I/O operations."""
        io_patterns = ['open', 'read', 'write', 'requests', 'urlopen']
        
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in io_patterns:
                        self.violations.append({
                            'id': 'io_in_loop',
                            'line': child.lineno,
                            'severity': 'critical',
                            'message': f'I/O operation "{child.func.id}()" in loop. Each call costs 100-1000x more energy.',
                            'pattern_match': 'io_operation_in_loop'
                        })
    
    def _check_unnecessary_computation(self, loop_node) -> None:
        """
        Check for redundant computations in loop that could be moved outside.
        E.g., len(s), range(n) if n is constant, re.compile, etc.
        """
        redundant_funcs = ['len', 'range', 're.compile', 'datetime.now', 'time.time']
        
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                func_name = None
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    # Handle re.compile or similar
                    if isinstance(child.func.value, ast.Name):
                        func_name = f"{child.func.value.id}.{child.func.attr}"
                
                if func_name in redundant_funcs:
                    # Heuristic: Check if arguments are actually dependent on loop variables
                    # For simplicity in this version, we flag common ones that are often static
                    self.violations.append({
                        'id': 'unnecessary_computation',
                        'line': child.lineno,
                        'severity': 'critical',
                        'message': f'Redundant computation "{func_name}()" in loop. Move outside for O(1) impact.',
                        'pattern_match': 'computation_outside_loop'
                    })
    
    def _check_inefficient_lookups(self, loop_node) -> None:
        """Check for membership tests on lists inside loops (O(n) vs O(1))."""
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Compare):
                for op in child.ops:
                    if isinstance(op, (ast.In, ast.NotIn)):
                        # If the right side is a Name, it might be a list
                        # This is a heuristic - in real tool we'd track types
                        if isinstance(child.comparators[0], ast.Name):
                            self.violations.append({
                                'id': 'inefficient_lookup',
                                'line': child.lineno,
                                'severity': 'medium',
                                'message': f'Membership test on "{child.comparators[0].id}" inside loop. If it is a list, consider converting to a set for O(1) lookup.',
                                'pattern_match': 'list_lookup_loop'
                            })
    
    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Detect string concatenation in loops."""
        # Check for += with strings in loops
        if self.in_loop and isinstance(node.op, ast.Add):
            # This is simplified; real detection would be more sophisticated
            pass
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls for I/O and performance issues."""
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            
            # Track used variables
            self.used_variables.add(func_name)
            
            # Rule: Blocking I/O
            blocking_io = ['requests.get', 'urlopen', 'time.sleep']
            if func_name in blocking_io or any(func_name.endswith(f'.{b}') for b in blocking_io):
                self.violations.append({
                    'id': 'blocking_io',
                    'line': node.lineno,
                    'severity': 'high',
                    'message': f'Blocking I/O operation "{func_name}()". Consider async/await.',
                    'pattern_match': 'sync_io'
                })
            
            # Rule: Resource might leak (proper_resource_cleanup)
            if func_name == 'open' and not self._is_in_context_manager(node):
                self.violations.append({
                    'id': 'proper_resource_cleanup',
                    'line': node.lineno,
                    'severity': 'high',
                    'message': 'File opened without context manager. Use "with open()" to ensure closure.',
                    'pattern_match': 'file_not_closed'
                })

            # Rule: Excessive Logging
            if func_name == 'print':
                self.violations.append({
                    'id': 'excessive_logging',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': 'Usage of "print" detected. Use logging module or remove in production.',
                    'pattern_match': 'print_usage'
                })

        # Rule: Excessive Logging (Logger methods)
        if isinstance(node.func, ast.Attribute) and node.func.attr in ['debug', 'info', 'log']:
             # Heuristic: check if called on something like 'args.logger' or 'logging' or 'logger'
             if isinstance(node.func.value, ast.Name) and node.func.value.id in ['logger', 'logging']:
                  self.violations.append({
                    'id': 'excessive_logging',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': f'Excessive logging call "{node.func.attr}". Verify log levels.',
                    'pattern_match': 'logging_call'
                })

        # Rule: Heavy object copying
        if (isinstance(node.func, ast.Attribute) and node.func.attr == 'deepcopy') or (func_name == 'deepcopy'):
            self.violations.append({
                'id': 'heavy_object_copy',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Usage of deepcopy detected. This is computationally expensive.',
                'pattern_match': 'deepcopy'
            })

        # Rule: Process Spawning
        call_s = ast.dump(node.func) # Simplified string check
        if 'subprocess' in call_s or 'os.system' in call_s or 'popen' in call_s.lower():
             # Basic filter to avoid false positives if variable names match
             is_process = False
             if isinstance(node.func, ast.Attribute):
                 if node.func.attr in ['run', 'Popen', 'system', 'spawn']:
                     is_process = True
             elif func_name in ['system', 'popen', 'spawn']:
                 is_process = True
            
             if is_process:
                self.violations.append({
                    'id': 'process_spawning',
                    'line': node.lineno,
                    'severity': 'critical',
                    'message': 'Process spawning detected. High OS overhead.',
                    'pattern_match': 'process_spawn'
                })

        # Rule: Inefficient file reading (Attribute call)
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'readlines':
            self.violations.append({
                'id': 'inefficient_file_read',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Using readlines() reads entire file into memory. Iterate file object instead.',
                'pattern_match': 'readlines'
            })

        # Rule: Pandas iterrows
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'iterrows':
            self.violations.append({
                'id': 'pandas_iterrows',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Using iterrows() is slow. Use vectorization or apply().',
                'pattern_match': 'iterrows'
            })

        self.generic_visit(node)
    
    def visit_Global(self, node: ast.Global) -> None:
        """Detect global variable usage."""
        self.violations.append({
            'id': 'global_variable_mutation',
            'line': node.lineno,
            'severity': 'minor',
            'message': 'Global variable usage detected. Can hinder optimization.',
            'pattern_match': 'global_keyword'
        })
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect try-except blocks inside loops."""
        if self.in_loop:
             self.violations.append({
                'id': 'exceptions_in_loop',
                'line': node.lineno,
                'severity': 'major',
                'message': 'Try/Except block inside loop. Exception handling is expensive.',
                'pattern_match': 'try_in_loop'
            })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detect high complexity functions and deep recursion."""
        prev_function = self.current_function
        self.current_function = node.name
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(node)
        
        if complexity > 10:
            self.violations.append({
                'id': 'high_cyclomatic_complexity',
                'line': node.lineno,
                'severity': 'medium',
                'message': f'Function has high cyclomatic complexity ({complexity}). More code paths = more CPU execution.',
                'pattern_match': 'complex_function'
            })
        
        # Rule: Deep Recursion
        if self._is_recursive(node):
             self.violations.append({
                'id': 'deep_recursion',
                'line': node.lineno,
                'severity': 'major',
                'message': f'Recursive function "{node.name}" detected. Deep recursion consumes significant stack memory and CPU.',
                'pattern_match': 'recursive_function'
            })

        self.generic_visit(node)
        self.current_function = prev_function

    def _is_recursive(self, node: ast.FunctionDef) -> bool:
        """Check if function calls itself."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == node.name:
                    return True
        return False
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track imports for unused detection."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = node.lineno
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Track variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.unused_variables[target.id] = node.lineno
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Track variable usage."""
        if isinstance(node.ctx, ast.Load):
            self.used_variables.add(node.id)
        self.generic_visit(node)
    
    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect magic numbers (Python 3.8+)."""
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if node.value > 100 and node.value not in [1000, 1024, 60, 3600]: # Exempt common constants
                self.violations.append({
                    'id': 'magic_numbers',
                    'line': node.lineno,
                    'severity': 'minor',
                    'message': f'Magic number "{node.value}" usage. Use named constants.',
                    'pattern_match': 'magic_number'
                })
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Detect context managers (proper cleanup)."""
        # Track items in with statements to identify manual open() calls elsewhere
        self.generic_visit(node)


    
    def _is_in_context_manager(self, call_node) -> bool:
        """Check if call is within a with statement."""
        # Simplified check - would need to track parent nodes properly
        return False
    
    def _calculate_cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                complexity += 1
        return complexity
    
    def _detect_unused_variables(self) -> None:
        """Detect unused variables."""
        for var_name, line_num in self.unused_variables.items():
            if var_name not in self.used_variables and not var_name.startswith('_'):
                self.violations.append({
                    'id': 'unused_variables',
                    'line': line_num,
                    'severity': 'medium',
                    'message': f'Unused variable "{var_name}". Remove to free memory.',
                    'pattern_match': 'unused_var'
                })
    
    def _detect_unused_imports(self) -> None:
        """Detect unused imports."""
        for import_name, line_num in self.imports.items():
            if import_name not in self.used_variables:
                self.violations.append({
                    'id': 'unused_imports',
                    'line': line_num,
                    'severity': 'low',
                    'message': f'Unused import "{import_name}". Module load adds startup time and memory.',
                    'pattern_match': 'unused_import'
                })


class PatternBasedDetector:
    """Pattern-based detection using regex for simple violations."""
    
    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []
    
    def detect_all(self) -> List[Dict]:
        """Run all pattern-based detectors."""
        self._detect_redundant_computation()
        self._detect_string_concatenation()
        self._detect_dead_code()
        self._detect_inefficient_data_structures()
        
        return self.violations
    
    def _detect_redundant_computation(self) -> None:
        """Detect expensive operations that could be moved outside loops."""
        patterns = [
            (r'for\s+\w+\s+in\s+.*:\s*[^\n]*len\(', 'len() in loop'),
            (r'for\s+\w+\s+in\s+.*:\s*[^\n]*\.count\(', '.count() in loop'),
            (r'for\s+\w+\s+in\s+.*:\s*[^\n]*re\.compile\(', 're.compile() in loop'),
        ]
        
        for line_num, line in enumerate(self.lines, 1):
            for pattern, desc in patterns:
                if re.search(pattern, line):
                    self.violations.append({
                        'id': 'unnecessary_computation',
                        'line': line_num,
                        'severity': 'critical',
                        'message': f'Redundant computation detected ({desc}). Move outside loop.',
                        'pattern_match': 'computation_outside_loop'
                    })
    
    def _detect_string_concatenation(self) -> None:
        """Detect string concatenation in loops."""
        in_loop = False
        for line_num, line in enumerate(self.lines, 1):
            if re.search(r'\bfor\b', line):
                in_loop = True
            elif re.search(r'^(?!\s)', line):  # Dedent
                in_loop = False
            
            if in_loop and re.search(r'\+=\s*["\']', line):
                self.violations.append({
                    'id': 'string_concatenation_in_loop',
                    'line': line_num,
                    'severity': 'medium',
                    'message': 'String concatenation in loop creates O(n²) memory allocations.',
                    'pattern_match': 'string_concat_loop'
                })
    
    def _detect_dead_code(self) -> None:
        """Detect unreachable code."""
        for line_num, line in enumerate(self.lines, 1):
            # Simple pattern: code after return/raise
            if line_num < len(self.lines):
                current = line.strip()
                next_line = self.lines[line_num].strip()
                
                if current.startswith('return') or current.startswith('raise'):
                    if next_line and not next_line.startswith(('except', 'finally', 'elif', 'else', '@', 'def', 'class')):
                        self.violations.append({
                            'id': 'dead_code_block',
                            'line': line_num + 1,
                            'severity': 'medium',
                            'message': 'Unreachable code after return/raise. Dead code increases memory.',
                            'pattern_match': 'dead_code'
                        })
    
    def _detect_inefficient_data_structures(self) -> None:
        """Detect inefficient data structure usage."""
        patterns = [
            (r'\.index\([^)]*\)\s*[!=]=', '.index() for lookup (O(n)), use set'),
            (r'\.count\([^)]*\)', '.count() for membership test (O(n)), use set'),
        ]
        
        for line_num, line in enumerate(self.lines, 1):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    self.violations.append({
                        'id': 'inefficient_data_structure',
                        'line': line_num,
                        'severity': 'high',
                        'message': message,
                        'pattern_match': 'data_struct_usage'
                    })
    
    def _detect_pandas_inefficiency(self) -> None:
        """Detect pandas inefficiencies via regex for simple cases."""
        # Already handled by AST visit_Call for iterrows, but regex can catch chained calls etc if needed.
        pass


class JavaScriptViolationDetector:
    """Pattern-based detector for JavaScript violations."""
    
    def __init__(self, content: str, file_path: str):
        self.content = content
        self.file_path = file_path
        self.lines = content.split('\n')
        self.violations = []
    
    def detect_all(self) -> List[Dict]:
        """Run all JavaScript detectors."""
        self._detect_unused_variables()
        self._detect_deprecated_apis()
        self._detect_inefficient_browser_apis()
        self._detect_nested_loops()
        self._detect_dom_manipulation_in_loop()
        self._detect_infinite_loops()
        self._detect_inefficient_loops()
        self._detect_sync_io()
        self._detect_excessive_logging()
        self._detect_magic_numbers()
        self._detect_string_concatenation()
        self._detect_dom_manipulation()
        
        return self.violations

    def _detect_unused_variables(self) -> None:
        """Detect unused variables (basic heuristic)."""
        # Find declarations: let/const/var name = ...
        # Dictionary to track counts
        var_counts = {}
        declarations = []
        
        # 1. Find all words to count usage (simple tokenizer)
        words = re.findall(r'\b\w+\b', self.content)
        for word in words:
            var_counts[word] = var_counts.get(word, 0) + 1
            
        # 2. Find specific declarations to report errors
        pattern = r'(let|const|var)\s+(\w+)\s*='
        for line_num, line in enumerate(self.lines, 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                var_name = match.group(2)
                # Filter out likely false positives (short vars, exports, etc if needed)
                if len(var_name) > 1:
                    declarations.append((var_name, line_num))

        # 3. Check if declared vars are used elsewhere
        for var_name, line_num in declarations:
            # If count is 1, it matches only the detected declaration (roughly)
            # This is a heuristic and can be fooled by comments / strings, 
            # but fits the "basic regex check" requirement.
            if var_counts.get(var_name, 0) == 1:
                self.violations.append({
                    'id': 'unused_variables',
                    'line': line_num,
                    'severity': 'minor',
                    'message': f'Variable "{var_name}" appears to be unused.',
                    'pattern_match': 'unused_var_js'
                })

    def _detect_deprecated_apis(self) -> None:
        """Detect deprecated or heavy libraries/APIs."""
        patterns = [
            (r'eval\(', 'eval_usage', 'critical', 'Eval is a security risk and slow.'),
            (r'document\.write', 'document_write', 'critical', 'document.write blocks rendering.'),
            (r'from\s+[\'"]moment[\'"]|require\([\'"]moment[\'"]\)', 'momentjs_deprecated', 'major', 'Moment.js is heavy. Use Day.js or Date.'),
        ]

        for line_num, line in enumerate(self.lines, 1):
            for pattern, rule_id, severity, msg in patterns:
                if re.search(pattern, line):
                    self.violations.append({
                        'id': rule_id,
                        'line': line_num,
                        'severity': severity,
                        'message': msg,
                        'pattern_match': rule_id
                    })

    def _detect_inefficient_browser_apis(self) -> None:
        """Detect inefficient browser APIs."""
        patterns = [
            (r'setInterval', 'setInterval_animation', 'major', 'Use requestAnimationFrame instead of setInterval.'),
            (r'window\.(alert|prompt|confirm)', 'alert_usage', 'minor', 'Native dialogs block the main thread.'),
        ]
        
        for line_num, line in enumerate(self.lines, 1):
            for pattern, rule_id, severity, msg in patterns:
                if re.search(pattern, line):
                     self.violations.append({
                        'id': rule_id,
                        'line': line_num,
                        'severity': severity,
                        'message': msg,
                        'pattern_match': rule_id
                    })
        
    
    def _detect_nested_loops(self) -> None:
        """Detect nested loops in JavaScript with scope tracking."""
        # Using a simplified scope-based tracking
        scopes = [] # Stack of scopes (type, start_line)
        
        for line_num, line in enumerate(self.lines, 1):
            # Very basic brace-based scope tracking
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Heuristic for loop start
            if re.search(r'\b(for|while|forEach|map)\b', line):
                for _ in range(open_braces):
                    scopes.append(('loop', line_num))
                
                # Check nesting
                loop_depth = sum(1 for s in scopes if s[0] == 'loop')
                if loop_depth >= 2:
                    severity = 'critical' if loop_depth >= 3 else 'major'
                    self.violations.append({
                        'id': 'no_n2_algorithms',
                        'line': line_num,
                        'severity': severity,
                        'message': f'Nesting depth {loop_depth}: Potential O(n^{loop_depth}) complexity detected.',
                        'pattern_match': 'nested_loop_js'
                    })
            else:
                for _ in range(open_braces):
                    scopes.append(('block', line_num))
            
            for _ in range(close_braces):
                if scopes:
                    scopes.pop()

    def _detect_dom_manipulation_in_loop(self) -> None:
        """Detect DOM manipulation inside loop scopes."""
        dom_methods = ['appendChild', 'innerHTML', 'textContent', 'setAttribute', 'classList.add', 'document.write']
        scopes = []
        
        for line_num, line in enumerate(self.lines, 1):
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            if re.search(r'\b(for|while|forEach|map)\b', line):
                for _ in range(open_braces):
                    scopes.append(('loop', line_num))
            else:
                for _ in range(open_braces):
                    scopes.append(('block', line_num))
            
            # Check if we are in a loop scope
            if any(s[0] == 'loop' for s in scopes):
                for method in dom_methods:
                    if method in line:
                        self.violations.append({
                            'id': 'unnecessary_dom_manipulation',
                            'line': line_num,
                            'severity': 'critical',
                            'message': f'DOM manipulation "{method}" inside loop. Causes reflows/repaints. Batch updates.',
                            'pattern_match': 'dom_in_loop'
                        })
                        break
            
            for _ in range(close_braces):
                if scopes:
                    scopes.pop()

    def _detect_infinite_loops(self) -> None:
        """Detect infinite loops."""
        pattern = r'while\s*\(\s*true\s*\)'
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                self.violations.append({
                    'id': 'no_infinite_loops',
                    'line': line_num,
                    'severity': 'critical',
                    'message': 'Infinite loop detected (while(true)).',
                    'pattern_match': 'infinite_while_js'
                })

    def _detect_inefficient_loops(self) -> None:
        """Detect inefficient C-style loops."""
        pattern = r'for\s*\(\s*(let|var)\s+\w+\s*='
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
               # Simple heuristic: if it matches standard for loop, suggest map/reduce
               self.violations.append({
                    'id': 'inefficient_loop',
                    'line': line_num,
                    'severity': 'major',
                    'message': 'C-style for loop detected. Consider using .map(), .filter(), or .reduce() for better optimization.',
                    'pattern_match': 'c_style_for'
                })

    def _detect_sync_io(self) -> None:
        """Detect synchronous I/O."""
        pattern = r'readFileSync|XMLHttpRequest'
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
                self.violations.append({
                    'id': 'synchronous_io',
                    'line': line_num,
                    'severity': 'major',
                    'message': 'Synchronous I/O blocks the main thread. Use async APIs.',
                    'pattern_match': 'sync_io_js'
                })

    def _detect_excessive_logging(self) -> None:
        """Detect excessive console logging."""
        pattern = r'console\.(log|debug)'
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
                self.violations.append({
                    'id': 'excessive_console_logging',
                    'line': line_num,
                    'severity': 'minor',
                    'message': 'Console logging detected. Remove in production.',
                    'pattern_match': 'console_log'
                })

    def _detect_string_concatenation(self) -> None:
        """Detect string concatenation in loops (JS)."""
        in_loop = False
        for line_num, line in enumerate(self.lines, 1):
            if re.search(r'\b(for|while)\b', line):
                in_loop = True
            elif re.search(r'^\s*}', line): # Simple brace-based end heuristic
                in_loop = False
            
            if in_loop and re.search(r'\+=\s*["\']', line):
                self.violations.append({
                    'id': 'string_concatenation',
                    'line': line_num,
                    'severity': 'major',
                    'message': 'String concatenation in loop creates new objects repeatedly.',
                    'pattern_match': 'string_concat_js'
                })

    def _detect_magic_numbers(self) -> None:
        """Detect magic numbers."""
        pattern = r'[^a-zA-Z0-9_]\s([0-9]{3,})\s[^a-zA-Z0-9_]'
        for line_num, line in enumerate(self.lines, 1):
            match = re.search(pattern, line)
            if match:
                 number = int(match.group(1))
                 if number not in [1000, 1024, 3600]:
                    self.violations.append({
                        'id': 'magic_numbers',
                        'line': line_num,
                        'severity': 'minor',
                        'message': f'Magic number "{number}" usage. Use named constants.',
                        'pattern_match': 'magic_number_js'
                    })

    def _detect_dom_manipulation(self) -> None:
        """Detect direct DOM manipulation."""
        pattern = r'document\.(querySelector|getElementById)'
        for line_num, line in enumerate(self.lines, 1):
            if re.search(pattern, line):
                self.violations.append({
                    'id': 'unnecessary_dom_manipulation',
                    'line': line_num,
                    'severity': 'major',
                    'message': 'Direct DOM query/manipulation. Cache references.',
                    'pattern_match': 'dom_query'
                })


def detect_violations(content: str, file_path: str, language: str = 'python') -> List[Dict]:
    """
    Detect all violations in code.
    
    Returns a list of violations with id, line, severity, message, pattern_match.
    """
    violations = []
    
    if language == 'python':
        # AST-based detection
        ast_detector = PythonViolationDetector(content, file_path)
        violations.extend(ast_detector.detect_all())
        
        # Pattern-based detection
        pattern_detector = PatternBasedDetector(content, file_path)
        violations.extend(pattern_detector.detect_all())
    
    elif language == 'javascript':
        js_detector = JavaScriptViolationDetector(content, file_path)
        violations.extend(js_detector.detect_all())
    
    return violations
