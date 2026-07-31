"""Praxis «скачал и запустил»: поднимает сервер и открывает браузер.

Собирается в один исполняемый файл (PyInstaller, см. scripts/build_desktop.py). Работает
офлайн — без токенов, ключей и GPU — на встроенном корпусе кодексов. Для продового
качества (BGE-M3/reranker/NLI) запускайте из исходников с extra ml и GPU.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

# PyInstaller распаковывает бандл в _MEIPASS; из исходников — корень репозитория.
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
os.environ.setdefault("PRAXIS_CORPUS_DIR", str(BASE / "corpus"))
os.environ.setdefault("PRAXIS_OFFLINE", "1")
sys.path.insert(0, str(BASE / "src"))

HOST, PORT = "127.0.0.1", 8077
URL = f"http://{HOST}:{PORT}"


def _open_when_ready() -> None:
    for _ in range(120):
        try:
            urllib.request.urlopen(f"{URL}/health", timeout=1)  # noqa: S310
            break
        except Exception:
            time.sleep(0.5)
    webbrowser.open(URL)


def main() -> None:
    import uvicorn

    print(f"Praxis запускается… откроется в браузере: {URL}")
    threading.Thread(target=_open_when_ready, daemon=True).start()
    uvicorn.run("praxis.api.app:app", host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
