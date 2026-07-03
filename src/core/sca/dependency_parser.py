import json
import re
from typing import Dict


def parse_python_requirements(content: str) -> Dict[str, str]:
    """Parse dependencies from a requirements.txt file."""
    dependencies = {}
    lines = content.split('\n')
    for line in lines:
        line = line.split('#')[0].strip()
        if not line:
            continue
        # Support basic requirements like requests==2.34.2 or requests>=2.34.2
        # For OSV query we might just take the exact version or no version if missing.
        match = re.match(r'^([a-zA-Z0-9_\-]+)(.*?)$', line)
        if match:
            pkg_name = match.group(1).strip()
            version_spec = match.group(2).strip()

            # Extract first exact version if specified (e.g., ==1.0.0)
            version_match = re.search(r'==([a-zA-Z0-9_\-\.]+)', version_spec)
            version = version_match.group(1) if version_match else ""
            dependencies[pkg_name] = version
    return dependencies


def parse_node_package_json(content: str) -> Dict[str, str]:
    """Parse dependencies from a package.json file."""
    dependencies = {}
    try:
        data = json.loads(content)
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})

        all_deps = {**deps, **dev_deps}

        for pkg, ver in all_deps.items():
            # Strip ^ or ~ prefix
            clean_ver = re.sub(r'^[\^~=><]+', '', str(ver)).strip()
            dependencies[pkg] = clean_ver
    except json.JSONDecodeError:
        pass

    return dependencies


def parse_go_mod(content: str) -> Dict[str, str]:
    """Parse dependencies from a go.mod file."""
    dependencies = {}
    lines = content.split('\n')

    in_require_block = False

    for line in lines:
        line = line.split('//')[0].strip()
        if not line:
            continue

        if line == "require (":
            in_require_block = True
            continue
        elif line == ")" and in_require_block:
            in_require_block = False
            continue

        if line.startswith("require "):
            # Single line require
            parts = line[8:].strip().split()
            if len(parts) >= 2:
                dependencies[parts[0]] = parts[1].lstrip('v')
        elif in_require_block:
            # Inside require block
            parts = line.split()
            if len(parts) >= 2:
                dependencies[parts[0]] = parts[1].lstrip('v')

    return dependencies
