# -*- coding: utf-8 -*-
from pathlib import Path


def purify_ledger(path: Path):
    print(f"Purifying {path}...")
    try:
        with open(path, 'rb') as f:
            raw_bytes = f.read()
        
        text = raw_bytes.decode('utf-8', errors='replace')
        
        # Using unicode escapes to avoid UTF-8 literal issues in powershell/cli
        fixed = (text
                 .replace('\u00ce\u00a9', '\u03a9')   # Omega
                 .replace('a\u009c\u0085', '\u2705') # Green check
                 .replace('a\u0080\u0094', '\u2014') # EM dash
                 .replace('a\u008f\u00b8', '\u23f3') # Hourglass
                 .replace('a\u009a\u00a0', '\u26a0') # Warning
                 .replace('\u00f0\u009f\u0094\u00b4', '\U0001f534') # Red circle
                 .replace('ANYA_I\u00a9', 'ANYA_\u03a9')
                )
        
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(fixed)
        print("Purification complete.")
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    ledger = Path("03_VAULT/PROVENANCE_LEDGER.md")
    if ledger.exists():
        purify_ledger(ledger)
    else:
        print("Ledger not found.")
