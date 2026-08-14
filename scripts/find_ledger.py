# SPDX-License-Identifier: MIT

import os
from pathlib import Path


def main():
    root = Path("C:/Users/vizio/CAMELOT_OS")
    print("Searching for folders or files with 'ledger' in name...")
    for r, dirs, files in os.walk(root):
        # ignore common libraries
        if any(ignore in r for ignore in [".git", ".venv", "node_modules", "99_ARCHIVE"]):
            continue
        
        # Check dirs
        for d in dirs:
            if "ledger" in d.lower() and "provenance" not in d.lower() and "verification" not in d.lower():
                print("Dir found:", os.path.join(r, d))
                
        # Check files
        for f in files:
            if "ledger" in f.lower() and "provenance" not in f.lower() and "verification" not in f.lower():
                print("File found:", os.path.join(r, f))

if __name__ == "__main__":
    main()
