"""ASGI entry point for mlango_eval.

What a production server points at. `manage.py runserver` is for development:
one process, autoreload, no worker management.

    uvicorn mlango_eval.asgi:application --host 0.0.0.0 --port 8000 --workers 4
    gunicorn mlango_eval.asgi:application -k uvicorn.workers.UvicornWorker -w 4

The module-level `application` is built once per worker at import, so the
registry is populated and every declared model is resolvable before the first
request arrives rather than during it.
"""

import os

from mlango.serve import create_app

os.environ.setdefault("MLANGO_SETTINGS_MODULE", "mlango_eval.settings")

application = create_app()
