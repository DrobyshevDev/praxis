"""Desktop-клиент Praxis: нативное окно поверх локального API (pywebview).

Тонкий клиент — поднимает встроенный сервер и открывает окно с тем же веб-UI. Логика
живёт в API-ядре, десктоп остаётся тонким (та же архитектура, что web/mobile).

    pip install -e ".[api,desktop]"
    python desktop/app.py

По умолчанию берёт корпус из ./corpus. Для продового качества добавьте extra ml (GPU).
Заметка: GUI-окно не запускается в headless-окружении — только на десктопе с дисплеем.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("PRAXIS_CORPUS_DIR", str(ROOT / "corpus"))

HOST, PORT = "127.0.0.1", 8077


def _serve() -> None:
    import uvicorn

    uvicorn.run("praxis.api.app:app", host=HOST, port=PORT, log_level="warning")


def _wait_ready(timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://{HOST}:{PORT}/health", timeout=1)  # noqa: S310
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main() -> None:
    import webview

    threading.Thread(target=_serve, daemon=True).start()
    _wait_ready()
    webview.create_window(
        "Praxis — юридический ассистент",
        f"http://{HOST}:{PORT}",
        width=920,
        height=820,
    )
    webview.start()


if __name__ == "__main__":
    main()
