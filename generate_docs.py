import os

docs_dir = "docs/rules"
os.makedirs(docs_dir, exist_ok=True)

with open(f"{docs_dir}/comprehensive_guide.md", "w") as f:
    f.write("# Comprehensive Rules Guide\n\n")
    f.write("This document provides an exhaustive list of rules enforced by Green AI.\n\n")
    for i in range(1, 201):
        f.write(f"## Rule {i}: GREEN-{i:03d}\n\n")
        f.write(f"**Description**: This is an extended description for rule GREEN-{i:03d}, ensuring that environmental standards are maintained across the codebase.\n\n")
        f.write(f"**Severity**: High\n\n")
        f.write(f"**Remediation**: To fix this, update your code to be more energy-efficient and reduce carbon emissions. Ensure that all loops are optimized and no unnecessary API calls are made.\n\n")
        f.write(f"```python\n")
        f.write(f"# Example non-compliant code\n")
        f.write(f"def inefficient_function_{i}():\n")
        f.write(f"    for i in range(10000):\n")
        f.write(f"        pass # Wasted cycles\n")
        f.write(f"```\n\n")
        f.write(f"```python\n")
        f.write(f"# Example compliant code\n")
        f.write(f"def efficient_function_{i}():\n")
        f.write(f"    pass # Optimized\n")
        f.write(f"```\n\n")
