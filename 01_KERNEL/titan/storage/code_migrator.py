# -*- coding: utf-8 -*-
"""
CODE MIGRATION SCRIPT: os.getenv() → vault.get()
Scans Python files and updates credential access patterns.

USAGE:
    python migrate_code_to_vault.py --scan      # Scan for os.getenv() usage
    python migrate_code_to_vault.py --migrate   # Migrate to vault.get()
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class CodeMigrator:
    """Migrates Python code from os.getenv() to vault.get()."""
    
    ROOT_DIR = Path(__file__).parent.parent
    LEDGER_PATH = ROOT_DIR / "PROVENANCE_LEDGER.md"
    
    # Patterns to detect
    GETENV_PATTERN = re.compile(r'os\.getenv\(["\']([A-Z_]+)["\']\)')
    ENVIRON_PATTERN = re.compile(r'os\.environ\[["\']([A-Z_]+)["\']\]')
    ENVIRON_GET_PATTERN = re.compile(r'os\.environ\.get\(["\']([A-Z_]+)["\']\)')
    
    def __init__(self):
        """Initialize the code migrator."""
        self.files_scanned = 0
        self.matches_found: List[Tuple[Path, int, str]] = []
        self.files_migrated: List[Path] = []
    
    def _log_to_ledger(self, action: str, status: str = "SUCCESS"):
        """Log migration actions to the provenance ledger."""
        timestamp = datetime.now().isoformat()
        entry = f"| {timestamp} | CODE_MIGRATOR | {action} | {status} |\n"
        
        try:
            with open(self.LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"[WARNING] Ledger Write Failed: {e}")
    
    def scan_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """
        Scan a Python file for os.getenv() usage.
        
        Args:
            file_path: Path to the Python file
        
        Returns:
            List of (line_number, line_content, credential_name) tuples
        """
        matches = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    # Check for os.getenv()
                    match = self.GETENV_PATTERN.search(line)
                    if match:
                        matches.append((line_num, line.strip(), match.group(1)))
                        continue
                    
                    # Check for os.environ[]
                    match = self.ENVIRON_PATTERN.search(line)
                    if match:
                        matches.append((line_num, line.strip(), match.group(1)))
                        continue
                    
                    # Check for os.environ.get()
                    match = self.ENVIRON_GET_PATTERN.search(line)
                    if match:
                        matches.append((line_num, line.strip(), match.group(1)))
        
        except Exception as e:
            print(f"[ERROR] Failed to scan {file_path}: {e}")
        
        return matches
    
    def scan_directory(self, directory: Path = None) -> Dict[Path, List[Tuple[int, str, str]]]:
        """
        Scan a directory for Python files with os.getenv() usage.
        
        Args:
            directory: Directory to scan (default: ROOT_DIR)
        
        Returns:
            Dictionary mapping file paths to lists of matches
        """
        if directory is None:
            directory = self.ROOT_DIR
        
        results = {}
        
        # Directories to exclude
        exclude_dirs = {
            "venv", ".venv", "__pycache__", "node_modules", 
            ".git", ".gemini", "99_HISTORY", "docs/EXTERNAL"
        }
        
        # Find all Python files
        try:
            for py_file in directory.rglob("*.py"):
                # Skip if any excluded directory is in the path
                if any(excluded in py_file.parts for excluded in exclude_dirs):
                    continue
                
                # Skip if file doesn't exist (broken symlink)
                if not py_file.exists():
                    continue
                
                self.files_scanned += 1
                matches = self.scan_file(py_file)
                
                if matches:
                    results[py_file] = matches
                    for line_num, _line, cred in matches:
                        self.matches_found.append((py_file, line_num, cred))
        except Exception as e:
            print(f"[ERROR] Directory scan failed: {e}")
        
        return results
    
    def migrate_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """
        Migrate a single file from os.getenv() to vault.get().
        
        Args:
            file_path: Path to the Python file
            dry_run: If True, only show what would be changed
        
        Returns:
            True if migration was successful
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Add vault import if not present
            if "from vault_manager import VaultManager" not in content:
                # Find the last import statement
                import_lines = []
                other_lines = []
                in_imports = True
                
                for line in content.split("\n"):
                    if in_imports and (line.startswith("import ") or line.startswith("from ")):
                        import_lines.append(line)
                    else:
                        if line.strip() and not line.startswith("#"):
                            in_imports = False
                        other_lines.append(line)
                
                # Add vault import
                vault_import = "from vault_manager import VaultManager"
                import_lines.append(vault_import)
                
                content = "\n".join(import_lines) + "\n" + "\n".join(other_lines)
            
            # Add vault initialization if not present
            if "vault = VaultManager()" not in content:
                # Add after imports
                lines = content.split("\n")
                insert_index = 0
                
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith("#") and not line.startswith("import") and not line.startswith("from"):
                        insert_index = i
                        break
                
                lines.insert(insert_index, "vault = VaultManager()")
                content = "\n".join(lines)
            
            # Replace os.getenv() with vault.get()
            content = self.GETENV_PATTERN.sub(r'vault.get("\1")', content)
            content = self.ENVIRON_PATTERN.sub(r'vault.get("\1")', content)
            content = self.ENVIRON_GET_PATTERN.sub(r'vault.get("\1")', content)
            
            if content != original_content:
                if dry_run:
                    print(f"[DRY-RUN] Would migrate: {file_path}")
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[OK] Migrated: {file_path}")
                    self.files_migrated.append(file_path)
                
                return True
        
        except Exception as e:
            print(f"[ERROR] Failed to migrate {file_path}: {e}")
            return False
        
        return False
    
    def print_scan_results(self, results: Dict[Path, List[Tuple[int, str, str]]]):
        """Print scan results."""
        print("\n" + "="*60)
        print("SCAN RESULTS")
        print("="*60)
        print(f"Files scanned: {self.files_scanned}")
        print(f"Files with matches: {len(results)}")
        print(f"Total matches: {len(self.matches_found)}")
        
        if results:
            print("\nFiles requiring migration:")
            for file_path, matches in results.items():
                rel_path = file_path.relative_to(self.ROOT_DIR)
                print(f"\n  {rel_path}:")
                for line_num, _line, cred in matches:
                    print(f"    Line {line_num}: {cred}")
                    print(f"      {_line}")
        
        print("="*60)
    
    def print_migration_summary(self):
        """Print migration summary."""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Files migrated: {len(self.files_migrated)}")
        
        if self.files_migrated:
            print("\nMigrated files:")
            for file_path in self.files_migrated:
                rel_path = file_path.relative_to(self.ROOT_DIR)
                print(f"  - {rel_path}")
        
        print("="*60)


def main():
    """CLI interface for code migration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Python code from os.getenv() to vault.get()")
    parser.add_argument("--scan", action="store_true", help="Scan for os.getenv() usage")
    parser.add_argument("--migrate", action="store_true", help="Migrate code to vault.get()")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--directory", type=str, help="Directory to scan (default: project root)")
    
    args = parser.parse_args()
    
    migrator = CodeMigrator()
    directory = Path(args.directory) if args.directory else None
    
    if args.scan:
        print("[CODE MIGRATOR] Scanning for os.getenv() usage...\n")
        results = migrator.scan_directory(directory)
        migrator.print_scan_results(results)
    
    elif args.migrate:
        print("[CODE MIGRATOR] Starting code migration...\n")
        results = migrator.scan_directory(directory)
        
        for file_path in results.keys():
            migrator.migrate_file(file_path, dry_run=args.dry_run)
        
        if not args.dry_run and migrator.files_migrated:
            migrator._log_to_ledger(
                f"MIGRATE: {len(migrator.files_migrated)} Python files to vault.get()"
            )
        
        migrator.print_migration_summary()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
