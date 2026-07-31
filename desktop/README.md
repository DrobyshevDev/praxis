# Desktop-клиент

Тонкий десктоп-клиент поверх API-ядра: нативное окно с тем же веб-UI и встроенным
сервером. Та же архитектура, что у web и будущего mobile — вся логика в API.

## Запуск

```bash
pip install -e ".[api,desktop]"
python desktop/app.py
```

Открывается нативное окно, внутри — локальный Praxis на `127.0.0.1:8077`. Корпус берётся
из `./corpus`. Для продового качества (BGE-M3 / reranker / NLI) добавьте extra `ml` и GPU.

## Сборка в исполняемый файл

Для распространения «скачал и запустил» упаковывается через PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "corpus:corpus" --add-data "src/praxis:praxis" desktop/app.py
```

Стек — pywebview (нативный webview ОС), без Electron/Node, минимальный вес.
