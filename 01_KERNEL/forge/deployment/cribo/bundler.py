# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cribo Bundler: The Kinetic Python Module Linker
Bundles Python packages into single standalone .py files for zero-dependency deployment.
"""

import argparse
import ast
import logging
import shutil
import sys
import tempfile
import zipapp
from pathlib import Path
from typing import List, Set

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # For Python < 3.11


logger = logging.getLogger(__name__)


class CriboBundler:
    """
    Cribo (Latin: "To Sift")
    Bundles Python code by sifting through imports and inlining dependencies.
    """

    def __init__(
        self, entry_point: str, output_path: str = None, search_paths: List[str] = None, config_path: str = None
    ):
        self.entry_point = Path(entry_point).resolve()
        if not self.entry_point.exists():
            raise FileNotFoundError(f"Entry point {self.entry_point} not found")

        self.config = self._load_config(config_path)

        self.project_root = self.entry_point.parent
        self.output_path = (
            Path(output_path) if output_path else self.entry_point.parent / f"{self.entry_point.stem}_bundled.py"
        )

        # Enhanced Search Paths
        self.search_paths = [self.project_root]
        if search_paths:
            self.search_paths.extend([Path(p).resolve() for p in search_paths])

        # Auto-detect common roots
        repo_root = self.project_root.parent
        self.search_paths.append(repo_root)  # CAMELOT_OS
        self.search_paths.append(repo_root / "src")  # CAMELOT_OS/src

        self.processed_files: Set[Path] = set()
        self.stdlib_modules = self._get_stdlib_modules()
        self.external_deps = set(self.config.get("bundler", {}).get("external", []))

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from cribo.toml"""
        cfg_path = Path(config_path) if config_path else self.entry_point.parent / "cribo.toml"
        if cfg_path.exists():
            try:
                with open(cfg_path, "rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                logger.warning("Failed to load config at %s: %s", cfg_path, e)
        return {}

    def _get_stdlib_modules(self) -> Set[str]:
        """Get set of standard library module names"""
        return set(sys.builtin_module_names) | set(sys.modules.keys())

    def analyze_imports(self, file_path: Path) -> List[str]:
        """
        Extract local imports from a Python file.
        Returns list of absolute paths to imported local modules.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return []

        local_modules = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_local_import(alias.name, local_modules)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_local_import(node.module, local_modules)

        return local_modules

    def _is_within_search_paths(self, resolved: Path) -> bool:
        """Reject any path that escapes all declared search roots."""
        return any(str(resolved).startswith(str(p.resolve())) for p in self.search_paths)

    def _check_local_import(self, module_name: str, local_modules: List[Path]):
        """Check if import is local and add to list"""
        if module_name in self.stdlib_modules:
            return

        # Check if the base package is marked as external
        base_module = module_name.split(".")[0]
        if base_module in self.external_deps:
            return

        for path in self.search_paths:
            # Check for .py file
            module_path = (path / f"{module_name.replace('.', '/')}.py").resolve()
            if module_path.exists() and self._is_within_search_paths(module_path):
                local_modules.append(module_path)
                return

            # Check for package (__init__.py)
            package_path = (path / module_name.replace(".", "/") / "__init__.py").resolve()
            if package_path.exists() and self._is_within_search_paths(package_path):
                local_modules.append(package_path)
                return

    def bundle(self):
        """
        Execute the bundling process via zipapp.
        """
        logger.info("📦 [Cribo] Bundling %s...", self.entry_point.name)

        files_to_process = [self.entry_point]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            while files_to_process:
                current_file = files_to_process.pop(0)
                if current_file in self.processed_files:
                    continue

                self.processed_files.add(current_file)

                # Determine relative structure for zipapp inclusion
                if current_file == self.entry_point:
                    target_path = temp_dir_path / "__main__.py"
                else:
                    rel_path = None
                    for sp in self.search_paths:
                        try:
                            rel_path = current_file.relative_to(sp)
                            break
                        except ValueError:
                            pass

                    if not rel_path:
                        rel_path = current_file.name

                    target_path = temp_dir_path / rel_path

                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(current_file, target_path)

                # Find dependencies
                deps = self.analyze_imports(current_file)
                files_to_process.extend(deps)

            # Construct zero-dependency zip archive (.pyz)
            zipapp.create_archive(temp_dir_path, target=self.output_path, interpreter="/usr/bin/env python3")

        logger.info("✅ [Cribo] Bundle created at: %s", self.output_path)
        logger.info("   - Files packed: %d", len(self.processed_files))
        logger.info("   - Total size: %d bytes", self.output_path.stat().st_size)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Cribo Bundler: The Kinetic Python Module Linker")
    parser.add_argument("entry", help="Path to the main entry point Python script.")
    parser.add_argument("out", nargs="?", help="Path to output the bundled executable (.pyz).")
    parser.add_argument("--search-paths", nargs="*", help="Additional paths to search for local modules.")
    parser.add_argument("--config", help="Path to cribo.toml configuration file.")

    args = parser.parse_args()

    bundler = CriboBundler(
        entry_point=args.entry, output_path=args.out, search_paths=args.search_paths, config_path=args.config
    )
    bundler.bundle()


if __name__ == "__main__":
    main()
