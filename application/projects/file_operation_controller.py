from pathlib import Path

from infrastructure.filesystem.project_file_service import (
    ProjectFileService,
)
from application.projects.file_operation_authorizer import (
    AuthorizationError,
    FileOperationAuthorizer,
)


class FileOperationController:
    """Coordena autorizaÃ§Ã£o e execuÃ§Ã£o de operaÃ§Ãµes em arquivos."""

    def __init__(
        self,
        project_root,
        mode=FileOperationAuthorizer.SUPERVISED,
        autonomous_permissions=None,
        approval_callback=None,
        file_service=None,
    ):
        self.authorizer = FileOperationAuthorizer(
            project_root,
            mode,
            autonomous_permissions,
        )

        if file_service is None:
            self.service = ProjectFileService(
                self.authorizer.project_root
            )
        else:
            self.service = file_service

            service_root = getattr(self.service, "project_root", None)

            # ServiÃ§os reais precisam declarar a raiz que operam.
            if isinstance(self.service, ProjectFileService):
                if service_root is None:
                    raise AuthorizationError(
                        "O serviÃ§o de arquivos nÃ£o declarou a raiz."
                    )

                try:
                    normalized_service_root = Path(
                        service_root
                    ).resolve(strict=True)
                except (OSError, RuntimeError, TypeError, ValueError) as error:
                    raise AuthorizationError(
                        "NÃ£o foi possÃ­vel validar a raiz do serviÃ§o."
                    ) from error

                if normalized_service_root != self.authorizer.project_root:
                    raise AuthorizationError(
                        "A raiz do serviÃ§o difere da raiz autorizada."
                    )

        self.approval_callback = approval_callback

    def execute(self, action, relative_path, content=None):
        if (
            not isinstance(action, str)
            or action not in FileOperationAuthorizer.ACTIONS
        ):
            raise AuthorizationError(
                "Tipo de operaÃ§Ã£o nÃ£o permitido."
            )

        if not isinstance(relative_path, str) or not relative_path:
            raise AuthorizationError(
                "O caminho deve ser um texto vÃ¡lido."
            )

        if action in {"create", "edit"}:
            if not isinstance(content, str):
                raise AuthorizationError(
                    "CriaÃ§Ã£o e ediÃ§Ã£o exigem conteÃºdo em texto."
                )

            approved_content = content
        else:
            if content is not None:
                raise AuthorizationError(
                    "Esta operaÃ§Ã£o nÃ£o aceita conteÃºdo."
                )

            approved_content = None

        # Validar o caminho antes de solicitar aprovaÃ§Ã£o.
        self.authorizer._validate_path(relative_path)

        approved = False

        if action != "read":
            if self.authorizer.mode == FileOperationAuthorizer.SUPERVISED:
                if self.approval_callback is None:
                    raise AuthorizationError(
                        "AprovaÃ§Ã£o do usuÃ¡rio necessÃ¡ria."
                    )

                approval_details = (
                    {"content": approved_content}
                    if action in {"create", "edit"}
                    else {}
                )

                approved = (
                    self.approval_callback(
                        action,
                        relative_path,
                        approval_details,
                    )
                    is True
                )

                if not approved:
                    raise AuthorizationError(
                        "OperaÃ§Ã£o recusada pelo usuÃ¡rio."
                    )

            elif action not in self.authorizer.autonomous_permissions:
                raise AuthorizationError(
                    "OperaÃ§Ã£o nÃ£o autorizada no modo autÃ´nomo."
                )

        self.authorizer.authorize(
            action,
            relative_path,
            user_approved=approved,
        )

        if action == "read":
            return self.service.read_file(relative_path)

        if action == "create":
            return self.service.create_file(
                relative_path,
                approved_content,
            )

        if action == "edit":
            return self.service.edit_file(
                relative_path,
                approved_content,
            )

        if action == "delete":
            return self.service.delete_file(
                relative_path,
                confirmed=True,
            )

        raise AuthorizationError(
            "OperaÃ§Ã£o nÃ£o permitida."
        )
