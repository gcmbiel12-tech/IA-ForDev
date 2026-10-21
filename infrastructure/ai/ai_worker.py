import urllib.error

from PySide6.QtCore import QThread, Signal
from app.config import MODEL
from infrastructure.ai.ollama_client import send_chat_request


class AIWorker(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            answer = send_chat_request(self.messages)

            if not answer:
                self.failed.emit("O modelo retornou uma resposta vazia.")
            else:
                self.succeeded.emit(answer)

        except urllib.error.URLError as error:
            self.failed.emit(
                "Não foi possível conectar ao Ollama.\n\n"
                "Verifique se o Ollama está funcionando e se o modelo "
                f"{MODEL} está instalado.\n\nDetalhes: {error}"
            )
        except Exception as error:
            self.failed.emit(f"Erro de comunicação com o modelo:\n{error}")
