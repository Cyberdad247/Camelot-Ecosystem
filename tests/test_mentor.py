import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath('01_KERNEL'))
from EXCALIBUR.system import MENTOR  # noqa: E402


class TestMentor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = os.path.join(self.temp_dir, "ROOT")
        self.secure_archive = os.path.join(self.temp_dir, "03_VAULT", "00_SECURE_ARCHIVE")
        self.ledger_path = os.path.join(self.temp_dir, "PROVENANCE_LEDGER.md")

        os.makedirs(self.root)

        # Patch variables in MENTOR
        self.patch_root = patch.object(MENTOR, 'ROOT', self.root)
        self.patch_secure = patch.object(MENTOR, 'SECURE_ARCHIVE', self.secure_archive)
        self.patch_ledger = patch.object(MENTOR, 'LEDGER_PATH', self.ledger_path)

        self.patch_root.start()
        self.patch_secure.start()
        self.patch_ledger.start()

    def tearDown(self):
        self.patch_root.stop()
        self.patch_secure.stop()
        self.patch_ledger.stop()
        shutil.rmtree(self.temp_dir)

    def test_sanitize_environment_moves_env_file(self):
        # Create an exposed .env file
        env_file_path = os.path.join(self.root, ".env")
        with open(env_file_path, "w") as f:
            f.write("SECRET=123")

        MENTOR.sanitize_environment()

        # Check if it was moved
        self.assertFalse(os.path.exists(env_file_path))

        # Check if it is in SECURE_ARCHIVE
        archived_files = os.listdir(self.secure_archive)
        self.assertEqual(len(archived_files), 1)
        self.assertTrue(archived_files[0].endswith(".env"))

    def test_sanitize_environment_ignores_samples(self):
        # Create an allowed .env.sample file
        env_sample_path = os.path.join(self.root, ".env.sample")
        with open(env_sample_path, "w") as f:
            f.write("SECRET=123")

        MENTOR.sanitize_environment()

        # Check if it is still there
        self.assertTrue(os.path.exists(env_sample_path))
        self.assertFalse(os.path.exists(self.secure_archive)) # Since nothing was archived

    def test_sanitize_environment_multiple_env_files(self):
        # Create multiple exposed .env files
        env1_path = os.path.join(self.root, ".env.dev")
        env2_path = os.path.join(self.root, "test.env")

        with open(env1_path, "w") as f:
            f.write("SECRET=123")
        with open(env2_path, "w") as f:
            f.write("TEST=abc")

        MENTOR.sanitize_environment()

        # Check if both were moved
        self.assertFalse(os.path.exists(env1_path))
        self.assertFalse(os.path.exists(env2_path))

        archived_files = os.listdir(self.secure_archive)
        self.assertEqual(len(archived_files), 2)

    def test_sanitize_environment_ignores_skip_dirs(self):
        # Create skip_dirs with .env inside
        node_modules = os.path.join(self.root, "node_modules")
        os.makedirs(node_modules)
        env_path = os.path.join(node_modules, ".env")
        with open(env_path, "w") as f:
            f.write("SECRET=123")

        MENTOR.sanitize_environment()

        # Check if it was skipped (still exists)
        self.assertTrue(os.path.exists(env_path))
        self.assertFalse(os.path.exists(self.secure_archive))

    def test_sanitize_environment_logs_to_ledger(self):
        # Create an exposed .env file
        env_file_path = os.path.join(self.root, ".env")
        with open(env_file_path, "w") as f:
            f.write("SECRET=123")

        MENTOR.sanitize_environment()

        # Check if ledger was created and logged to
        self.assertTrue(os.path.exists(self.ledger_path))
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            ledger_content = f.read()

        self.assertIn("GOVERNANCE: Secured 1 .env files.", ledger_content)
        self.assertIn("SUCCESS", ledger_content)

    def test_sanitize_environment_handles_exception_during_move(self):
        # Create an exposed .env file
        env_file_path = os.path.join(self.root, ".env")
        with open(env_file_path, "w") as f:
            f.write("SECRET=123")

        with patch('shutil.move', side_effect=Exception("Mocked error")):
            MENTOR.sanitize_environment()

        # File shouldn't be moved
        self.assertTrue(os.path.exists(env_file_path))

        # Check that it did NOT log to ledger
        if os.path.exists(self.ledger_path):
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                ledger_content = f.read()
            self.assertNotIn("GOVERNANCE: Secured", ledger_content)

if __name__ == '__main__':
    unittest.main()
