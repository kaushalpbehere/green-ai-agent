
import pytest
from src.core.detectors import detect_violations

def test_js_ast_migration_rules(tmp_path):
    """Test all migrated JavaScript rules using Tree-sitter AST."""

    js_content = """
    // Deprecated APIs
    document.write("hello");
    const m = require('moment');
    import moment from 'moment';

    // Inefficient browser APIs
    setInterval(() => {}, 1000);
    window.alert("msg");
    confirm("Are you sure?");
    prompt("Name?");

    // Nested loops (Depth 2)
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < 10; j++) {
            console.log(i, j);
        }
    }

    // DOM in loop
    while (true) {
        document.getElementById("id").innerHTML = "content";
        document.body.appendChild(div);
    }

    // Infinite loop
    while (true) {
        // infinite
    }

    // Sync IO
    const fs = require('fs');
    fs.readFileSync('file.txt');
    new XMLHttpRequest();

    // String concatenation in loop
    let s = "";
    for (let i = 0; i < 10; i++) {
        s += "string";
    }

    // Inefficient loop
    for (let k = 0; k < 5; k++) {}

    // Direct DOM manipulation
    const el = document.querySelector(".class");
    """

    js_file = tmp_path / "test_migration.js"
    js_file.write_text(js_content, encoding="utf-8")

    violations = detect_violations(js_content, str(js_file), language='javascript')

    # Helper to check if rule was triggered
    def check_rule(rule_id, count=1):
        found = [v for v in violations if v['id'] == rule_id]
        assert len(found) >= count, f"Rule {rule_id} not detected (expected {count}, found {len(found)})"
        return found

    # 1. Deprecated APIs
    check_rule('document_write', 1)
    check_rule('momentjs_deprecated', 2) # require and import

    # 2. Inefficient Browser APIs
    check_rule('setInterval_animation', 1)
    check_rule('alert_usage', 3) # alert, confirm, prompt

    # 3. Loops
    check_rule('no_n2_algorithms', 1) # Nested loop
    check_rule('no_infinite_loops', 2) # Two while(true) loops
    check_rule('inefficient_loop', 2) # Two for loops (nested outer and inner, and separate one)

    # 4. DOM in Loop
    check_rule('unnecessary_dom_manipulation', 4)
    # innerHTML (in loop), appendChild (in loop), querySelector (direct), getElementById (direct inside loop?)
    # Wait, getElementById is direct DOM query (unnecessary_dom_manipulation) AND inside loop (unnecessary_dom_manipulation)
    # My code reports both?
    # Direct DOM query checks: document.querySelector | document.getElementById
    # DOM in loop checks: innerHTML, appendChild... inside loop.
    # getElementById inside loop matches Direct DOM query.
    # It does NOT match DOM in loop because 'getElementById' is not in dom_methods list for loop check?
    # dom_methods = ["appendChild", "innerHTML", "textContent", "setAttribute", "classList", "write"]
    # So getElementById inside loop triggers 'unnecessary_dom_manipulation' via _detect_dom_manipulation (Direct Query).

    # Let's count specific messages if needed, but ID check is good enough for now.

    # 5. Sync IO
    check_rule('synchronous_io', 2) # readFileSync, XMLHttpRequest

    # 6. String Concatenation
    check_rule('string_concatenation', 1)
