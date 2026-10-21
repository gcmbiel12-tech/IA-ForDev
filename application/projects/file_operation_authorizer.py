from pathlib import Path, PureWindowsPath


class AuthorizationError(Exception):
    """Opera??o n?o autorizada."""


class FileOperationAuthorizer:
    SUPERVISED = "supervisionado"
    AUTONOMOUS = "autonomo"

    ACTIONS = {"read", "create", "edit", "delete"}

    def __init__(self, project_root, mode=SUPERVISED,
                 autonomous_permissions=None):
        self.project_root = Path(project_root).resolve()

        if not self.project_root.is_dir():
            raise AuthorizationError("Projeto autorizado inv?lido.")

        if mode not in {self.SUPERVISED, self.AUTONOMOUS}:
            raise AuthorizationError("Modo de autoriza??o inv?lido.")

        self.mode = mode
        self.autonomous_permissions = set(autonomous_permissions or ())

        if not self.autonomous_permissions <= self.ACTIONS:
            raise AuthorizationError("Permiss?o desconhecida.")

    def _validate_path(self, relative_path):
        raw = str(relative_path)
        path = Path(raw)
        win_path = PureWindowsPath(raw)

        if (
            not raw or path.is_absolute() or path.drive or path.root
            or win_path.drive or win_path.root or ":" in raw
            or any(part in ("..", ".") for part in path.parts)
        ):
            raise AuthorizationError("Caminho inv?lido ou n?o permitido.")

        target = self.project_root / path
        current = self.project_root

        for part in path.parts:
            current = current / part
            if current.is_symlink():
                raise AuthorizationError(
                    "Links simb?licos n?o s?o permitidos."
                )

        resolved = target.resolve(strict=False)

        if not resolved.is_relative_to(self.project_root):
            raise AuthorizationError("Caminho fora do projeto.")

        reserved = self.project_root / ".iafordev_backups"
        if resolved == reserved or reserved in resolved.parents:
            raise AuthorizationError("Pasta de backup protegida.")

        return target

    def authorize(self, action, relative_path, user_approved=False):
        if action not in self.ACTIONS:
            raise AuthorizationError("Tipo de operação não permitido.")

        self._validate_path(relative_path)

        # Leitura dentro do projeto não altera arquivos.
        if action == "read":
            return True

        # No modo autônomo, a permissão configurada é obrigatória.
        # A aprovação individual não pode ampliar essas permissões.
        if self.mode == self.AUTONOMOUS:
            if action in self.autonomous_permissions:
                return True
            raise AuthorizationError(
                "Operação não autorizada no modo autônomo."
            )

        # No modo supervisionado, exige aprovação explícita.
        if user_approved is True:
            return True

        raise AuthorizationError(
            "Aprovação do usuário necessária para esta operação."
        )
