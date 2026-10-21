import tempfile
import unittest
from pathlib import Path

from app.config import MAX_FILE_BYTES
from infrastructure.filesystem.project_reader import read_project


class ProjectReaderTests(unittest.TestCase):
    def test_reads_text_and_ignores_hidden_and_binary_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "main.py").write_text("print('ok')", encoding="utf-8")
            (root / "README.md").write_text("Projeto", encoding="utf-8")
            (root / "image.png").write_bytes(b"fake")
            (root / ".secret.py").write_text("segredo", encoding="utf-8")
            (root / ".env").write_text("TOKEN=abc", encoding="utf-8")
            (root / ".venv").mkdir()
            (root / ".venv" / "ignored.py").write_text(
                "ignored", encoding="utf-8"
            )

            context, total, read_count, skipped = read_project(root)

            self.assertEqual(total, 2)
            self.assertEqual(read_count, 2)
            self.assertGreaterEqual(skipped, 3)
            self.assertIn("main.py", context)
            self.assertIn("README.md", context)
            self.assertNotIn("TOKEN=abc", context)
            self.assertNotIn("segredo", context)
            self.assertNotIn("ignored", context)

    def test_oversized_file_is_not_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "large.py").write_text(
                "x" * (MAX_FILE_BYTES + 1), encoding="utf-8"
            )

            context, total, read_count, skipped = read_project(root)

            self.assertEqual(total, 1)
            self.assertEqual(read_count, 0)
            self.assertEqual(skipped, 1)
            self.assertNotIn("x" * 100, context)

    def test_missing_directory_raises_error(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            with self.assertRaises(RuntimeError):
                read_project(missing)


if __name__ == "__main__":
    unittest.main()
