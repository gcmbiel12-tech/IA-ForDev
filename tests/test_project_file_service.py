import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from infrastructure.filesystem.project_file_service import (
    FileOperationError,
    ProjectFileService,
)


class ProjectFileServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.service = ProjectFileService(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_file(self):
        self.service.create_file("src/example.py", "print('ok')\n")
        self.assertEqual(
            (self.root / "src/example.py").read_text(encoding="utf-8"),
            "print('ok')\n",
        )

    def test_create_does_not_overwrite(self):
        target = self.root / "example.txt"
        target.write_text("original", encoding="utf-8")

        with self.assertRaises(FileOperationError):
            self.service.create_file("example.txt", "novo")

        self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_edit_creates_backup(self):
        target = self.root / "example.txt"
        target.write_text("original", encoding="utf-8")

        backup = self.service.edit_file("example.txt", "alterado")

        self.assertEqual(target.read_text(encoding="utf-8"), "alterado")
        self.assertEqual(backup.read_text(encoding="utf-8"), "original")
        self.assertTrue(backup.is_file())

    def test_delete_requires_confirmation_and_keeps_backup(self):
        target = self.root / "example.txt"
        target.write_text("original", encoding="utf-8")

        with self.assertRaises(FileOperationError):
            self.service.delete_file("example.txt")

        self.assertTrue(target.exists())

        backup = self.service.delete_file("example.txt", confirmed=True)
        self.assertFalse(target.exists())
        self.assertEqual(backup.read_text(encoding="utf-8"), "original")

    def test_blocks_parent_traversal(self):
        with self.assertRaises(FileOperationError):
            self.service.read_file("../outside.txt")

        with self.assertRaises(FileOperationError):
            self.service.read_file("folder/../../outside.txt")

    def test_blocks_absolute_paths(self):
        with self.assertRaises(FileOperationError):
            self.service.read_file(str(self.root / "example.txt"))

    def test_blocks_windows_drive_relative_path(self):
        with self.assertRaises(FileOperationError):
            self.service.read_file("C:outside.txt")

    def test_read_file(self):
        target = self.root / "example.txt"
        target.write_text("conteudo", encoding="utf-8")
        self.assertEqual(self.service.read_file("example.txt"), "conteudo")

    def test_rejects_backup_directory_outside_project(self):
        outside = Path(self.temp.name) / "external_backups"

        with self.assertRaises(FileOperationError):
            ProjectFileService(self.root, outside)

    def test_rejects_project_root_as_backup_directory(self):
        with self.assertRaises(FileOperationError):
            ProjectFileService(self.root, self.root)

    def test_blocks_direct_access_to_backup_directory(self):
        with self.assertRaises(FileOperationError):
            self.service.create_file(
                ".iafordev_backups/manual.txt", "nao permitido"
            )

    def test_failed_backup_prevents_edit(self):
        target = self.root / "example.txt"
        target.write_text("original", encoding="utf-8")

        with patch.object(
            self.service,
            "_backup",
            side_effect=FileOperationError("falha simulada"),
        ):
            with self.assertRaises(FileOperationError):
                self.service.edit_file("example.txt", "novo")

        self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_failed_backup_prevents_delete(self):
        target = self.root / "example.txt"
        target.write_text("original", encoding="utf-8")

        with patch.object(
            self.service,
            "_backup",
            side_effect=FileOperationError("falha simulada"),
        ):
            with self.assertRaises(FileOperationError):
                self.service.delete_file("example.txt", confirmed=True)

        self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_cannot_edit_or_delete_directory(self):
        directory = self.root / "folder"
        directory.mkdir()

        with self.assertRaises(FileOperationError):
            self.service.edit_file("folder", "novo")

        with self.assertRaises(FileOperationError):
            self.service.delete_file("folder", confirmed=True)

    def test_blocks_symlink_to_external_file(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("nao alterar", encoding="utf-8")
        link = self.root / "link.txt"

        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"N?o foi poss?vel criar symlink neste Windows: {error}")

        for operation in (
            lambda: self.service.read_file("link.txt"),
            lambda: self.service.edit_file("link.txt", "alterado"),
            lambda: self.service.delete_file("link.txt", confirmed=True),
        ):
            with self.subTest(operation=operation):
                with self.assertRaises(FileOperationError):
                    operation()

        self.assertEqual(outside.read_text(encoding="utf-8"), "nao alterar")


if __name__ == "__main__":
    unittest.main()
