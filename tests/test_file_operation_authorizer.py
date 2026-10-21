import tempfile
import unittest
from pathlib import Path

from application.projects.file_operation_authorizer import (
    AuthorizationError,
    FileOperationAuthorizer,
)


class FileOperationAuthorizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_supervised_requires_approval_for_edit(self):
        auth = FileOperationAuthorizer(self.root)

        with self.assertRaises(AuthorizationError):
            auth.authorize("edit", "app.py")

        self.assertTrue(
            auth.authorize("edit", "app.py", user_approved=True)
        )

    def test_autonomous_allows_only_granted_actions(self):
        auth = FileOperationAuthorizer(
            self.root,
            mode=FileOperationAuthorizer.AUTONOMOUS,
            autonomous_permissions={"create", "edit"},
        )

        self.assertTrue(auth.authorize("edit", "app.py"))

        with self.assertRaises(AuthorizationError):
            auth.authorize("delete", "app.py")

    def test_autonomous_approval_does_not_override_permissions(self):
        auth = FileOperationAuthorizer(
            self.root,
            mode=FileOperationAuthorizer.AUTONOMOUS,
            autonomous_permissions={"create"},
        )

        with self.assertRaises(AuthorizationError):
            auth.authorize("delete", "app.py", user_approved=True)
    def test_read_is_allowed_in_both_modes(self):
        auth = FileOperationAuthorizer(self.root)
        self.assertTrue(auth.authorize("read", "app.py"))

    def test_blocks_parent_traversal(self):
        auth = FileOperationAuthorizer(self.root)

        with self.assertRaises(AuthorizationError):
            auth.authorize("edit", "../outside.py", user_approved=True)

    def test_blocks_absolute_path(self):
        auth = FileOperationAuthorizer(self.root)

        with self.assertRaises(AuthorizationError):
            auth.authorize(
                "edit", str(self.root / "app.py"), user_approved=True
            )

    def test_blocks_unknown_actions(self):
        auth = FileOperationAuthorizer(self.root)

        with self.assertRaises(AuthorizationError):
            auth.authorize("execute_command", "app.py")

    def test_rejects_unknown_permissions(self):
        with self.assertRaises(AuthorizationError):
            FileOperationAuthorizer(
                self.root,
                mode=FileOperationAuthorizer.AUTONOMOUS,
                autonomous_permissions={"formatar_disco"},
            )

    def test_blocks_backup_directory(self):
        auth = FileOperationAuthorizer(self.root)

        with self.assertRaises(AuthorizationError):
            auth.authorize(
                "edit", ".iafordev_backups/backup.py",
                user_approved=True,
            )


if __name__ == "__main__":
    unittest.main()
