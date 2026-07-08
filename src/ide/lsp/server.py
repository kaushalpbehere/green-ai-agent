import logging
import ast
from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    InitializeParams,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionParams,
)
from src.core.detectors.python_detector import PythonViolationDetector
from src.core.detectors.javascript_detector import JavaScriptASTDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GreenAILSP")


class GreenAILanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("green-ai-lsp", "v0.1.0")


server = GreenAILanguageServer()


def _get_severity(sev_str: str) -> DiagnosticSeverity:
    sev_str = sev_str.lower()
    if sev_str == "critical" or sev_str == "high":
        return DiagnosticSeverity.Error
    elif sev_str == "medium" or sev_str == "major":
        return DiagnosticSeverity.Warning
    elif sev_str == "low" or sev_str == "minor":
        return DiagnosticSeverity.Information
    return DiagnosticSeverity.Hint


def _validate(ls: GreenAILanguageServer, params):
    """
    Validate the document and publish diagnostics.
    Uses AST detectors for Python and JS.
    """
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    source = text_doc.source
    uri = params.text_document.uri

    diagnostics = []

    # Choose detector based on extension
    if uri.endswith('.py'):
        try:
            tree = ast.parse(source)
            detector = PythonViolationDetector(file_path=uri)
            detector.visit(tree)

            for v in detector.violations:
                line = max(0, v.line - 1)
                # Just highlight the first word if we don't have exact ranges
                range_ = Range(
                    start=Position(line=line, character=0),
                    end=Position(line=line, character=10),
                )

                msg = f"{v.message}\nRemediation: {v.remediation}"
                d = Diagnostic(
                    range=range_,
                    message=msg,
                    severity=_get_severity(v.severity),
                    source="Green-AI",
                )
                diagnostics.append(d)
        except SyntaxError as e:
            logger.debug(f"SyntaxError in Python parsing: {e}")  # Ignore syntax errors for now
    elif uri.endswith('.js') or uri.endswith('.jsx'):
        try:
            detector = JavaScriptASTDetector()
            violations = detector.analyze(source, uri)

            for v in violations:
                line = max(0, v.line - 1)
                range_ = Range(
                    start=Position(line=line, character=0),
                    end=Position(line=line, character=10),
                )

                msg = f"{v.message}\nRemediation: {v.remediation}"
                d = Diagnostic(
                    range=range_,
                    message=msg,
                    severity=_get_severity(v.severity),
                    source="Green-AI",
                )
                diagnostics.append(d)
        except Exception as e:
            logger.debug(f"Exception in JS parsing: {e}")

    ls.publish_diagnostics(text_doc.uri, diagnostics)


@server.feature("initialize")
def initialize(ls: GreenAILanguageServer, params: InitializeParams):
    """Handle initialize request."""
    msg = "Green AI LSP Initialized"
    logger.info(msg)
    ls.window_show_message(msg)
    return None


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: GreenAILanguageServer, params: DidOpenTextDocumentParams):
    """Handle document open."""
    msg = f"Document opened: {params.text_document.uri}"
    logger.info(msg)
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: GreenAILanguageServer, params: DidChangeTextDocumentParams):
    """Handle document change."""
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: GreenAILanguageServer, params: DidSaveTextDocumentParams):
    """Handle document save."""
    msg = f"Document saved: {params.text_document.uri}"
    logger.info(msg)
    _validate(ls, params)


@server.feature(TEXT_DOCUMENT_CODE_ACTION)
def code_action(ls: GreenAILanguageServer, params: CodeActionParams):
    """Handle code action requests."""
    items = []
    # Can implement real quick fixes here later based on diagnostics
    return items


def main():
    server.start_io()


if __name__ == '__main__':
    main()
