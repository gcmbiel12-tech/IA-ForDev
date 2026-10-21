import json
import urllib.request

from app.config import MODEL, OLLAMA_URL


def send_chat_request(messages):
    """Envia mensagens ao Ollama e devolve o texto da resposta."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data.get("message", {}).get("content", "").strip()
