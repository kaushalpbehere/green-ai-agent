import pytest
from src.core.sca.dependency_parser import (
    parse_python_requirements,
    parse_node_package_json,
    parse_go_mod
)


def test_parse_python_requirements():
    content = """
# This is a comment
requests==2.31.0
Jinja2>=3.0.0
flask==3.0.0 # another comment
urllib3
"""
    result = parse_python_requirements(content)
    assert result == {
        "requests": "2.31.0",
        "Jinja2": "",
        "flask": "3.0.0",
        "urllib3": ""
    }


def test_parse_node_package_json():
    content = """
{
  "name": "my-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "~4.17.21"
  },
  "devDependencies": {
    "jest": "29.5.0"
  }
}
"""
    result = parse_node_package_json(content)
    assert result == {
        "express": "4.18.2",
        "lodash": "4.17.21",
        "jest": "29.5.0"
    }


def test_parse_node_package_json_invalid():
    content = "invalid json {"
    result = parse_node_package_json(content)
    assert result == {}


def test_parse_go_mod():
    content = """
module example.com/my/thing

go 1.20

require (
    github.com/gin-gonic/gin v1.9.1 // indirect
    golang.org/x/net v0.10.0
)

require github.com/stretchr/testify v1.8.4
"""
    result = parse_go_mod(content)
    assert result == {
        "github.com/gin-gonic/gin": "1.9.1",
        "golang.org/x/net": "0.10.0",
        "github.com/stretchr/testify": "1.8.4"
    }
