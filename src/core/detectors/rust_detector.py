"""
Rust-specific detection strategies for green software violations.
"""

from typing import List, Dict, Set
from tree_sitter import Language, Query, QueryCursor
import tree_sitter_rust
from src.utils.logger import logger
from .base_detector import BaseTreeSitterDetector

# Query Constants
QUERY_PRINTLN = """
(macro_invocation
  macro: (identifier) @macro_name
  (#match? @macro_name "^(print|println|eprint|eprintln)$"))
"""

QUERY_EMPTY_BLOCK = """(block) @block"""

QUERY_LOOP = """
(loop_expression) @loop
(for_expression) @loop
(while_expression) @loop
"""

QUERY_STRING_CONCAT = """
(compound_assignment_expr
  left: (identifier)
  operator: "+="
  right: (string_literal)
) @concat

(assignment_expression
  left: (identifier)
  right: (binary_expression
    operator: "+"
    right: (string_literal)
  )
) @concat
"""

class RustASTDetector(BaseTreeSitterDetector):
    """AST-based detector for Rust using Tree-sitter."""

    _CACHED_LANGUAGE = None
    _CACHED_QUERIES = {}

    def __init__(self, content: str, file_path: str):
        if RustASTDetector._CACHED_LANGUAGE is None:
            try:
                RustASTDetector._CACHED_LANGUAGE = Language(tree_sitter_rust.language())
            except Exception as e:
                logger.error(f"Failed to initialize Rust language: {e}")

        lang_arg = RustASTDetector._CACHED_LANGUAGE if RustASTDetector._CACHED_LANGUAGE else tree_sitter_rust
        super().__init__(content, file_path, lang_arg)

    def _get_query(self, query_scm: str) -> Query:
        """Get or compile a query."""
        if not self.language:
            return None

        if query_scm not in RustASTDetector._CACHED_QUERIES:
            try:
                RustASTDetector._CACHED_QUERIES[query_scm] = Query(self.language, query_scm)
            except Exception as e:
                logger.error(f"Failed to compile query for Rust: {e}")
                return None
        return RustASTDetector._CACHED_QUERIES.get(query_scm)

    def detect_all(self) -> List[Dict]:
        """Run all AST-based detectors."""
        if not self.tree:
            return []

        self._detect_println()
        self._detect_empty_blocks()
        self._detect_infinite_loop()
        self._detect_string_concatenation_in_loop()

        return self.violations

    def _detect_println(self) -> None:
        """Detect println! macro usage."""
        self._run_query(
            QUERY_PRINTLN,
            'rust_formatted_print',
            'minor',
            'println! detected. Use a logger or remove in production.',
            'rust_println'
        )

    def _detect_empty_blocks(self) -> None:
        """Detect empty blocks."""
        query = self._get_query(QUERY_EMPTY_BLOCK)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        for _, captures in matches:
            nodes = captures.get('block', [])
            for node in nodes:
                # The block node in Rust typically has `{` and `}` as children
                if node.named_child_count == 0:
                    self._add_violation(
                        node,
                        'rust_empty_block',
                        'minor',
                        'Empty block detected.',
                        'empty_block'
                    )

    def _detect_infinite_loop(self) -> None:
        """Detect infinite loops (loop {})."""
        query = self._get_query(QUERY_LOOP)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        for _, captures in matches:
            nodes = captures.get('loop', [])
            for node in nodes:
                if node.type == 'loop_expression':
                    body = None
                    for child in node.children:
                        if child.type == 'block':
                            body = child
                            break

                    if body:
                        has_break = False
                        def visit(n):
                            nonlocal has_break
                            if n.type == 'break_expression' or n.type == 'return_expression':
                                has_break = True
                            for c in n.children:
                                visit(c)
                        visit(body)

                        if not has_break:
                            self._add_violation(
                                node,
                                'rust_infinite_loop',
                                'critical',
                                'Infinite loop detected (loop {}). Ensure break condition exists.',
                                'rust_infinite_loop'
                            )

    def _detect_string_concatenation_in_loop(self) -> None:
        """Detect string concatenation inside loops (O(n^2))."""
        query = self._get_query(QUERY_STRING_CONCAT)
        if not query:
            return

        cursor = QueryCursor(query)
        matches = cursor.matches(self.tree.root_node)

        processed_nodes: Set[int] = set()

        for _, captures in matches:
            nodes = captures.get('concat', [])
            for node in nodes:
                if node.id in processed_nodes:
                    continue

                if self._is_in_loop(node):
                    self._add_violation(
                        node,
                        'rust_string_concatenation_in_loop',
                        'high',
                        'String concatenation in loop detected. Use String::with_capacity and push_str().',
                        'rust_str_concat'
                    )
                    processed_nodes.add(node.id)

    def _is_in_loop(self, node) -> bool:
        """Check if node is inside a loop."""
        parent = node.parent
        while parent:
            if parent.type in ('for_expression', 'while_expression', 'loop_expression'):
                return True
            parent = parent.parent
        return False
