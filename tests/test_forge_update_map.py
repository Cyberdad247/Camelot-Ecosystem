import os
import sys
import importlib.util
import tempfile
import pytest
from unittest.mock import patch

def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

update_map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '01_KERNEL', 'forge', 'update_map.py'))
update_map = import_from_path('update_map', update_map_path)
generate_tree = update_map.generate_tree

def test_generate_tree_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "test_file.txt"), "w") as f:
            f.write("test")

        tree = generate_tree(tmpdir)

        assert "# 🗺️ CAMELOT APEX: ENTIRE MAP (Territory)" in tree
        assert "**Timestamp:**" in tree
        assert "**Mode:** Kinetic Purity [Active]" in tree
        assert f"**Root:** `{tmpdir}`" in tree
        assert "📂 CAMELOT_OS/" in tree
        assert "- test_file.txt" in tree

def test_generate_tree_excludes():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, ".git"))
        with open(os.path.join(tmpdir, ".git", "hidden.txt"), "w") as f:
            f.write("hidden")

        tree = generate_tree(tmpdir)

        assert "📂 .git/" not in tree
        assert "hidden.txt" not in tree

def test_generate_tree_core_recursion():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "src", "nested"))
        with open(os.path.join(tmpdir, "src", "nested", "file.py"), "w") as f:
            f.write("code")

        tree = generate_tree(tmpdir)

        assert "📂 src/" in tree
        assert "    📂 nested/" in tree
        assert "file.py" not in tree

def test_generate_tree_core_tag():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "01_KERNEL"))

        tree = generate_tree(tmpdir)

        assert "📂 01_KERNEL/ [CORE]" in tree

def test_generate_tree_non_core_no_recursion():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "random_dir"))
        with open(os.path.join(tmpdir, "random_dir", "unseen.txt"), "w") as f:
            f.write("unseen")

        tree = generate_tree(tmpdir)

        assert "📂 random_dir/" in tree
        assert "unseen.txt" not in tree

def test_generate_tree_depth_cap():
    with tempfile.TemporaryDirectory() as tmpdir:
        current = tmpdir
        for i in range(15):
            current = os.path.join(current, "src")
            os.makedirs(current, exist_ok=True)

        tree = generate_tree(tmpdir)

        count_src = tree.count("📂 src/")
        assert count_src == 11

def test_generate_tree_permission_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "src"))

        original_listdir = os.listdir
        def mock_listdir(path):
            if "src" in path and path.endswith("src"):
                raise PermissionError("Access denied")
            return original_listdir(path)

        with patch('os.listdir', side_effect=mock_listdir):
            tree = generate_tree(tmpdir)

            assert "📂 src/" in tree
