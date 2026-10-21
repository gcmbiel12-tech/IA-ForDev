import os
from pathlib import Path

from app.config import (
    MAX_FILES,
    MAX_FILE_BYTES,
    MAX_TOTAL_CHARS,
    IGNORED_DIRS,
    IGNORED_FILES,
    TEXT_EXTENSIONS,
)


def read_project(root):
    """L? arquivos de texto respeitando os limites da configura??o."""
    root = Path(root)
    inventory = []
    contents = []
    skipped = 0
    total_chars = 0

    if not root.is_dir():
        raise RuntimeError("A pasta selecionada n?o est? dispon?vel.")

    for current, dirs, files in os.walk(root):
        dirs[:] = [
            name for name in dirs
            if name not in IGNORED_DIRS and not name.startswith(".")
        ]

        current_path = Path(current)

        for name in sorted(files):
            path = current_path / name
            relative = path.relative_to(root)

            if name.lower() in IGNORED_FILES or name.startswith("."):
                skipped += 1
                continue

            if path.suffix.lower() not in TEXT_EXTENSIONS:
                skipped += 1
                continue

            try:
                size = path.stat().st_size
            except OSError:
                skipped += 1
                continue

            inventory.append(f"{relative} ({size} bytes)")

            if len(contents) >= MAX_FILES or size > MAX_FILE_BYTES:
                skipped += 1
                continue

            if total_chars >= MAX_TOTAL_CHARS:
                skipped += 1
                continue

            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                skipped += 1
                continue

            text = text[:MAX_TOTAL_CHARS - total_chars]
            total_chars += len(text)
            contents.append(
                f"\n--- ARQUIVO: {relative} ---\n{text}\n"
            )

    inventory_text = "\n".join(inventory[:300]) or (
        "(nenhum arquivo de texto reconhecido)"
    )

    context = (
        f"CAMINHO DO PROJETO: {root}\n"
        f"ARQUIVOS IDENTIFICADOS: {len(inventory)}\n"
        f"ARQUIVOS COM CONTE?DO LIDO: {len(contents)}\n"
        f"ITENS IGNORADOS OU N?O LIDOS: {skipped}\n\n"
        f"INVENT?RIO:\n{inventory_text}\n\n"
        "CONTE?DO DOS ARQUIVOS LIDOS:\n"
        + "\n".join(contents)
    )

    return context, len(inventory), len(contents), skipped
