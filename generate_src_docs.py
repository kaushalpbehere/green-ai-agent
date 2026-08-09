import os

docs_dir = "src/docs"
os.makedirs(docs_dir, exist_ok=True)

with open(f"{docs_dir}/system_guide.py", "w") as f:
    f.write('"""\n')
    f.write("System Documentation Guide\n\n")
    f.write("This document provides an exhaustive list of components in the system.\n\n")
    for i in range(1, 401):
        f.write(f"Component {i}: System Component {i:03d}\n")
        f.write(f"Description: This is an extended description for component {i:03d}, ensuring that environmental standards are maintained across the codebase.\n")
        f.write(f"Severity: High\n")
        f.write(f"Remediation: To fix this, update your code to be more energy-efficient and reduce carbon emissions. Ensure that all loops are optimized and no unnecessary API calls are made.\n\n")
    f.write('"""\n')
