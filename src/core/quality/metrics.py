import ast
import hashlib
from typing import List, Dict, Tuple, Any

class Type1Visitor(ast.NodeVisitor):
    """
    Type-1 clone detection: Exact match (except whitespace and comments).
    We hash the sequence of AST node types.
    """
    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        self.nodes.append(type(node).__name__)
        # Differentiate functions/classes by their exact structure, including names for Type 1
        if isinstance(node, ast.Name):
            self.nodes.append(node.id)
        elif isinstance(node, ast.arg):
            self.nodes.append(node.arg)
        elif isinstance(node, ast.FunctionDef):
            self.nodes.append(node.name)
        elif isinstance(node, ast.ClassDef):
            self.nodes.append(node.name)
        elif isinstance(node, ast.Attribute):
            self.nodes.append(node.attr)
        elif isinstance(node, ast.keyword):
            self.nodes.append(node.arg or "VAR")
        elif isinstance(node, ast.Constant):
            self.nodes.append(str(node.value))

        super().generic_visit(node)

class Type2Visitor(ast.NodeVisitor):
    """
    Type-2 clone detection: Structurally identical, but variable names,
    types, and literals may differ.
    """
    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        if isinstance(node, ast.Name):
            self.nodes.append("VAR")
        elif isinstance(node, ast.arg):
            self.nodes.append("VAR")
        elif isinstance(node, ast.FunctionDef):
            self.nodes.append("FUNC_DEF")
        elif isinstance(node, ast.ClassDef):
            self.nodes.append("CLASS_DEF")
        elif isinstance(node, ast.Attribute):
            self.nodes.append(node.attr)
        elif isinstance(node, ast.keyword):
            self.nodes.append(node.arg or "VAR")
        elif isinstance(node, ast.Constant):
            self.nodes.append(f"CONST_{type(node.value).__name__}")
        else:
            self.nodes.append(type(node).__name__)
        super().generic_visit(node)

class DuplicationDetector:
    """
    Detects Type-1 and Type-2 code duplications.
    """
    def __init__(self, min_statements=3):
        self.min_statements = min_statements
        self.files = {}

    def add_file(self, filename: str, content: str):
        try:
            tree = ast.parse(content)
            self.files[filename] = tree
        except SyntaxError:
            pass

    def _hash_ast(self, node, visitor_cls):
        visitor = visitor_cls()
        visitor.visit(node)
        return hashlib.md5("".join(visitor.nodes).encode()).hexdigest()

    def _extract_blocks(self, tree):
        blocks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # Only consider blocks with enough substance
                if len(node.body) >= self.min_statements:
                    blocks.append(node)
        return blocks

    def detect(self) -> Dict[str, List[Dict[str, Any]]]:
        type1_hashes = {}
        type2_hashes = {}

        results = {"type_1": [], "type_2": []}

        for filename, tree in self.files.items():
            blocks = self._extract_blocks(tree)

            for block in blocks:
                # Type 1 (Exact match except whitespace/comments)
                t1_hash = self._hash_ast(block, Type1Visitor)
                is_type1 = False
                if t1_hash in type1_hashes:
                    # Avoid self-matching in the same place
                    if type1_hashes[t1_hash]["file"] != filename or type1_hashes[t1_hash]["line"] != block.lineno:
                        results["type_1"].append({
                            "file1": type1_hashes[t1_hash]["file"],
                            "line1": type1_hashes[t1_hash]["line"],
                            "file2": filename,
                            "line2": block.lineno
                        })
                        is_type1 = True
                else:
                    type1_hashes[t1_hash] = {"file": filename, "line": block.lineno}

                # Type 2 (Syntactically identical, different variables/constants)
                t2_hash = self._hash_ast(block, Type2Visitor)
                if t2_hash in type2_hashes:
                    # Only report as Type 2 if it's not already reported as Type 1
                    if not is_type1 and (type2_hashes[t2_hash]["file"] != filename or type2_hashes[t2_hash]["line"] != block.lineno):
                        results["type_2"].append({
                            "file1": type2_hashes[t2_hash]["file"],
                            "line1": type2_hashes[t2_hash]["line"],
                            "file2": filename,
                            "line2": block.lineno
                        })
                else:
                    type2_hashes[t2_hash] = {"file": filename, "line": block.lineno}

        return results
