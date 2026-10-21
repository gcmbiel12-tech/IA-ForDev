import tempfile
import unittest
from pathlib import Path

from application.projects.file_operation_controller import (
    FileOperationController,
)
from application.projects.file_operation_authorizer import AuthorizationError


class FakeFileService:
    def __init__(self):
        self.calls = []

    def read_file(self, path):
        self.calls.append(("read", path))
        return "conteÃºdo lido"

    def create_file(self, path, content):
        self.calls.append(("create", path, content))
        return "criado"

    def edit_file(self, path, content):
        self.calls.append(("edit", path, content))
        return "editado"

    def delete_file(self, path, confirmed=False):
        self.calls.append(("delete", path, confirmed))
        return "excluÃ­do"


class FileOperationSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.service = FakeFileService()
        self.callback_calls = []

    def tearDown(self):
        self.temp.cleanup()

    def callback(self, action, path, details):
        self.callback_calls.append((action, path, details))
        return True

    def make_controller(
        self,
        mode="supervisionado",
        permissions=None,
        callback=None,
    ):
        return FileOperationController(
            self.root,
            mode=mode,
            autonomous_permissions=permissions,
            approval_callback=callback,
            file_service=self.service,
        )

    def test_create_rejects_non_string_content_before_approval(self):
        controller = self.make_controller(callback=self.callback)

        for invalid in (None, 123, ["texto"], {"texto": "valor"}):
            with self.subTest(content=invalid):
                with self.assertRaises(AuthorizationError):
                    controller.execute("create", "arquivo.txt", invalid)

        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.service.calls, [])

    def test_edit_rejects_non_string_content_before_service(self):
        controller = self.make_controller(callback=self.callback)

        with self.assertRaises(AuthorizationError):
            controller.execute("edit", "arquivo.txt", None)

        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.service.calls, [])

    def test_read_rejects_unnecessary_content(self):
        controller = self.make_controller()

        with self.assertRaises(AuthorizationError):
            controller.execute("read", "arquivo.txt", "nÃ£o permitido")

        self.assertEqual(self.service.calls, [])

    def test_delete_rejects_unnecessary_content(self):
        controller = self.make_controller(callback=self.callback)

        with self.assertRaises(AuthorizationError):
            controller.execute("delete", "arquivo.txt", "nÃ£o permitido")

        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.service.calls, [])

    def test_denial_prevents_service_execution(self):
        controller = self.make_controller(
            callback=lambda action, path, details: False
        )

        with self.assertRaises(AuthorizationError):
            controller.execute("create", "arquivo.txt", "conteÃºdo")

        self.assertEqual(self.service.calls, [])

    def test_approval_and_service_receive_same_content(self):
        controller = self.make_controller(callback=self.callback)
        approved_content = "conteÃºdo autorizado"

        controller.execute("create", "arquivo.txt", approved_content)

        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(
            self.callback_calls[0][2]["content"],
            approved_content,
        )
        self.assertEqual(
            self.service.calls,
            [("create", "arquivo.txt", approved_content)],
        )

    def test_autonomous_mode_blocks_ungranted_edit(self):
        controller = self.make_controller(
            mode="autonomo",
            permissions={"create"},
        )

        with self.assertRaises(AuthorizationError):
            controller.execute("edit", "arquivo.txt", "novo conteÃºdo")

        self.assertEqual(self.service.calls, [])

    def test_autonomous_mode_allows_only_granted_create(self):
        controller = self.make_controller(
            mode="autonomo",
            permissions={"create"},
        )

        result = controller.execute("create", "arquivo.txt", "conteÃºdo")

        self.assertEqual(result, "criado")
        self.assertEqual(
            self.service.calls,
            [("create", "arquivo.txt", "conteÃºdo")],
        )
        self.assertEqual(self.callback_calls, [])

    def test_invalid_action_does_not_call_callback_or_service(self):
        controller = self.make_controller(callback=self.callback)

        with self.assertRaises(AuthorizationError):
            controller.execute("execute_command", "arquivo.txt")

        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.service.calls, [])

    def test_invalid_path_does_not_call_callback_or_service(self):
        controller = self.make_controller(callback=self.callback)

        with self.assertRaises(AuthorizationError):
            controller.execute("create", "../fora.txt", "conteÃºdo")

        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.service.calls, [])

    def test_delete_requires_permission_in_autonomous_mode(self):
        controller = self.make_controller(
            mode="autonomo",
            permissions={"create"},
        )

        with self.assertRaises(AuthorizationError):
            controller.execute("delete", "arquivo.txt")

        self.assertEqual(self.service.calls, [])

    def test_granted_delete_uses_confirmed_service_call(self):
        controller = self.make_controller(
            mode="autonomo",
            permissions={"delete"},
        )

        result = controller.execute("delete", "arquivo.txt")

        self.assertEqual(result, "excluÃ­do")
        self.assertEqual(
            self.service.calls,
            [("delete", "arquivo.txt", True)],
        )

    def test_rejects_real_service_with_different_project_root(self):
        from infrastructure.filesystem.project_file_service import (
            ProjectFileService,
        )

        with tempfile.TemporaryDirectory() as other_temp:
            other_root = Path(other_temp)

            with self.assertRaises(AuthorizationError):
                FileOperationController(
                    self.root,
                    file_service=ProjectFileService(other_root),
                )


if __name__ == "__main__":
    unittest.main()

