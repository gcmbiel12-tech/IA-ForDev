import tempfile
import unittest
from pathlib import Path

from application.projects.file_operation_controller import (
    FileOperationController,
)
from application.projects.file_operation_authorizer import (
    AuthorizationError, FileOperationAuthorizer,
)


class FileOperationControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_supervised_requires_callback(self):
        controller = FileOperationController(self.root)
        with self.assertRaises(AuthorizationError):
            controller.execute("create", "a.txt", "x")
        self.assertFalse((self.root / "a.txt").exists())

    def test_supervised_denial_does_not_modify_file(self):
        controller = FileOperationController(
            self.root, approval_callback=lambda *args: False
        )
        with self.assertRaises(AuthorizationError):
            controller.execute("create", "a.txt", "x")
        self.assertFalse((self.root / "a.txt").exists())

    def test_supervised_approval_allows_create_and_read(self):
        calls = []
        controller = FileOperationController(
            self.root,
            approval_callback=lambda action, path, details: (
                calls.append(action) or True
            ),
        )
        controller.execute("create", "a.txt", "conteudo")
        self.assertEqual(controller.execute("read", "a.txt"), "conteudo")
        self.assertEqual(calls, ["create"])

    def test_autonomous_permission_is_required(self):
        controller = FileOperationController(
            self.root, mode=FileOperationAuthorizer.AUTONOMOUS,
            autonomous_permissions={"create"}
        )
        controller.execute("create", "a.txt", "ok")
        with self.assertRaises(AuthorizationError):
            controller.execute("delete", "a.txt")
        self.assertTrue((self.root / "a.txt").exists())

    def test_invalid_path_is_rejected_before_callback(self):
        calls = []
        controller = FileOperationController(
            self.root,
            approval_callback=lambda *args: calls.append(args) or True,
        )
        with self.assertRaises(AuthorizationError):
            controller.execute("create", "../fora.txt", "x")
        self.assertEqual(calls, [])

    def test_edit_and_delete_use_file_service(self):
        controller = FileOperationController(
            self.root, approval_callback=lambda *args: True
        )
        controller.execute("create", "a.txt", "antes")
        controller.execute("edit", "a.txt", "depois")
        self.assertEqual(controller.execute("read", "a.txt"), "depois")
        controller.execute("delete", "a.txt")
        self.assertFalse((self.root / "a.txt").exists())


if __name__ == "__main__":
    unittest.main()
