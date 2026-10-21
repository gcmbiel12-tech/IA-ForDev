MODEL = "qwen2.5-coder:1.5b"
OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
Você é a I.AForDev, uma assistente especializada em desenvolvimento.

Regras:
- Responda em português brasileiro.
- Seja técnica, objetiva e organizada.
- Não invente arquivos, resultados, testes ou funcionalidades.
- Diferencie fatos confirmados de hipóteses.
- Ao analisar projetos, utilize somente as evidências recebidas.
- Não afirme que executou testes ou comandos que não executou.
- Quando houver um projeto selecionado, use o contexto fornecido.
- Se o contexto for insuficiente, explique o que precisa ser verificado.
- Ao apresentar um diagnóstico, informe problemas, gravidade,
  evidências, limitações e próximos passos.
- Nesta versão, você pode ler e analisar arquivos, mas ainda não
  pode modificá-los diretamente.
"""

# Limites para evitar ler projetos inteiros sem controle.
MAX_FILES = 60
MAX_FILE_BYTES = 20_000
MAX_TOTAL_CHARS = 55_000

IGNORED_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    "node_modules", "build", "dist", ".dart_tool",
    ".idea", ".vscode", ".pytest_cache", "coverage",
    "Pods", "DerivedData", ".next", ".gradle",
}

IGNORED_FILES = {
    ".env", ".env.local", ".env.production",
    "id_rsa", "id_ed25519", "credentials.json",
    "secrets.json", "service-account.json",
}

TEXT_EXTENSIONS = {
    ".py", ".dart", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".json", ".yaml", ".yml",
    ".toml", ".md", ".txt", ".xml", ".sql",
    ".sh", ".ps1", ".bat", ".ini", ".cfg",
    ".properties", ".gradle", ".kt", ".java",
    ".c", ".h", ".cpp", ".cs", ".go", ".rs",
    ".php", ".rb", ".vue", ".svelte",
}

IMPORTANT_NAMES = {
    "readme", "pubspec.yaml", "package.json",
    "pyproject.toml", "requirements.txt",
    "cargo.toml", "go.mod", "dockerfile",
    "makefile", "analysis_options.yaml",
}
