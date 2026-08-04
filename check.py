with open(".github/workflows/verify_os.yml", "r") as f:
    text = f.read()

import re

# Find all dorny/paths-filter uses
filters = re.finditer(r'uses:\s*dorny/paths-filter@v3', text)
for f in filters:
    print(f"Found filter at position {f.start()}")
