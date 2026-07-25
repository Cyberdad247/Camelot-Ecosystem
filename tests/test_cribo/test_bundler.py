import subprocess
import tempfile
import zipfile
from pathlib import Path


def test_bundler_executes_securely():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        pkg_dir = temp_dir_path / "my_pkg"
        pkg_dir.mkdir()

        # Create my_pkg
        (pkg_dir / "__init__.py").write_text("def hello():\n    print('Hello from sub!')\n")
        (pkg_dir / "bar.py").write_text("def bar():\n    print('Hello from bar!')\n")

        # Create main.py
        main_py = temp_dir_path / "main.py"
        main_py.write_text("import my_pkg\nmy_pkg.hello()\nimport my_pkg.bar\nmy_pkg.bar.bar()\n")

        # Run bundler
        bundler_path = Path("01_KERNEL/forge/deployment/cribo/bundler.py").resolve()
        output_pyz = temp_dir_path / "bundled.pyz"

        subprocess.run(["uv", "run", "python3", str(bundler_path), str(main_py), str(output_pyz)], check=True)

        # Execute the bundled zip archive
        result = subprocess.run(["uv", "run", "python3", str(output_pyz)], capture_output=True, text=True, check=True)

        assert "Hello from sub!" in result.stdout
        assert "Hello from bar!" in result.stdout


def test_bundler_config_exclusion():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Create dummy external package
        external_pkg_dir = temp_dir_path / "external_pkg"
        external_pkg_dir.mkdir()
        (external_pkg_dir / "__init__.py").write_text("def external_func():\n    print('External!')\n")

        # Create dummy internal package
        internal_pkg_dir = temp_dir_path / "internal_pkg"
        internal_pkg_dir.mkdir()
        (internal_pkg_dir / "__init__.py").write_text("def internal_func():\n    print('Internal!')\n")

        # Create config file
        config_toml = temp_dir_path / "cribo.toml"
        config_toml.write_text('[bundler]\nexternal = ["external_pkg"]\n')

        # Create main.py
        main_py = temp_dir_path / "main.py"
        main_py.write_text(
            "try:\n    import external_pkg\nexcept ImportError:\n    pass\nimport internal_pkg\ninternal_pkg.internal_func()\n"
        )

        # Run bundler
        bundler_path = Path("01_KERNEL/forge/deployment/cribo/bundler.py").resolve()
        output_pyz = temp_dir_path / "bundled.pyz"

        subprocess.run(
            ["uv", "run", "python3", str(bundler_path), str(main_py), str(output_pyz), "--config", str(config_toml)],
            check=True,
        )

        # Verify the archive contents directly
        # The file is a zip archive with a shebang, so zipfile can read it directly
        with zipfile.ZipFile(output_pyz, "r") as zf:
            namelist = zf.namelist()
            assert any(name.startswith("internal_pkg/") for name in namelist), "internal_pkg should be bundled"
            assert not any(name.startswith("external_pkg/") for name in namelist), "external_pkg should NOT be bundled"
