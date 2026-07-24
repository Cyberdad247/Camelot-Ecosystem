import os
import subprocess
import tempfile
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
        output_py = temp_dir_path / "bundled.py"

        subprocess.run(["uv", "run", "python3", str(bundler_path), str(main_py), str(output_py)], check=True)

        # Execute the bundled file
        result = subprocess.run(["uv", "run", "python3", str(output_py)], capture_output=True, text=True, check=True)

        assert "Hello from sub!" in result.stdout
        assert "Hello from bar!" in result.stdout
