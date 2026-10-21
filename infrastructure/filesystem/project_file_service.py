from pathlib import Path, PureWindowsPath
import os
import shutil
import tempfile
from datetime import datetime


class FileOperationError(Exception):
    """Erro controlado em uma opera??o de arquivo."""


class ProjectFileService:
    """Executa opera??es de arquivo limitadas ? raiz autorizada."""

    def __init__(self, project_root, backup_root=None):
        self.project_root = Path(project_root).resolve()

        if not self.project_root.is_dir():
            raise FileOperationError(
                "A pasta autorizada n?o existe ou n?o ? um diret?rio."
            )

        if backup_root is None:
            backup_root = self.project_root / ".iafordev_backups"

        self.backup_root = Path(backup_root).resolve()

        if (
            self.backup_root == self.project_root
            or not self.backup_root.is_relative_to(self.project_root)
        ):
            raise FileOperationError(
                "A pasta de backup precisa ficar dentro do projeto, "
                "em uma pasta separada da raiz."
            )

    def _resolve_target(self, relative_path):
        raw_path = str(relative_path)
        relative = Path(raw_path)
        windows_path = PureWindowsPath(raw_path)

        if (
            not raw_path
            or relative.is_absolute()
            or relative.drive
            or relative.root
            or windows_path.drive
            or windows_path.root
            or ":" in raw_path
        ):
            raise FileOperationError(
                "Caminho absoluto ou caminho com unidade n?o permitido."
            )

        if not relative.parts or any(
            part in ("..", ".") for part in relative.parts
        ):
            raise FileOperationError("Caminho relativo inv?lido.")

        target = self.project_root / relative

        # N?o seguir links simb?licos em nenhum componente do caminho.
        current = self.project_root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise FileOperationError(
                    "Opera??o bloqueada: links simb?licos n?o s?o permitidos."
                )

        resolved = target.resolve(strict=False)

        if not resolved.is_relative_to(self.project_root):
            raise FileOperationError(
                "Opera??o bloqueada: caminho fora do projeto autorizado."
            )

        if (
            resolved == self.backup_root
            or self.backup_root in resolved.parents
        ):
            raise FileOperationError(
                "Opera??es diretas na pasta de backup n?o s?o permitidas."
            )

        return target

    def _backup(self, target):
        if not target.is_file() or target.is_symlink():
            raise FileOperationError(
                "N?o ? poss?vel criar backup desse arquivo."
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        relative = target.relative_to(self.project_root)
        destination = self.backup_root / timestamp / relative

        try:
            destination.parent.mkdir(parents=True, exist_ok=False)
            shutil.copy2(target, destination)
        except OSError as error:
            raise FileOperationError(
                f"N?o foi poss?vel criar o backup: {error}"
            ) from error

        return destination

    def read_file(self, relative_path):
        target = self._resolve_target(relative_path)

        if not target.is_file():
            raise FileOperationError("O arquivo n?o existe.")

        try:
            return target.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise FileOperationError(
                f"N?o foi poss?vel ler o arquivo: {error}"
            ) from error

    def create_file(self, relative_path, content):
        target = self._resolve_target(relative_path)

        if target.exists() or target.is_symlink():
            raise FileOperationError(
                "O arquivo j? existe. A cria??o n?o sobrescreve arquivos."
            )

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="") as file:
                file.write(content)
        except (OSError, UnicodeError) as error:
            raise FileOperationError(
                f"N?o foi poss?vel criar o arquivo: {error}"
            ) from error

        return target

    def edit_file(self, relative_path, content):
        target = self._resolve_target(relative_path)

        if not target.is_file():
            raise FileOperationError(
                "S? ? poss?vel editar arquivos existentes."
            )

        backup = self._backup(target)
        temporary_path = None

        try:
            # Escreve em arquivo tempor?rio e s? depois substitui o original.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=target.parent,
                prefix=".iafordev_tmp_",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(content)
                temporary.flush()
                os.fsync(temporary.fileno())

            os.replace(temporary_path, target)
            temporary_path = None

        except (OSError, UnicodeError) as error:
            restoration_error = None
            try:
                shutil.copy2(backup, target)
            except OSError as restore_error:
                restoration_error = restore_error

            message = (
                f"Falha ao editar. Backup preservado em {backup}. "
                f"Erro: {error}"
            )
            if restoration_error:
                message += (
                    f" ATEN??O: tamb?m falhou a restaura??o autom?tica: "
                    f"{restoration_error}"
                )

            raise FileOperationError(message) from error

        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

        return backup

    def delete_file(self, relative_path, confirmed=False):
        if confirmed is not True:
            raise FileOperationError(
                "Exclus?o bloqueada: confirma??o expl?cita necess?ria."
            )

        target = self._resolve_target(relative_path)

        if not target.is_file():
            raise FileOperationError(
                "S? ? poss?vel excluir arquivos existentes."
            )

        backup = self._backup(target)

        try:
            target.unlink()
        except OSError as error:
            raise FileOperationError(
                f"Falha ao excluir. Backup preservado em {backup}: {error}"
            ) from error

        return backup
