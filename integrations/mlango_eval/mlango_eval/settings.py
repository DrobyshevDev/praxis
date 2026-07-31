"""Settings for the mlango_eval project.

Every available setting and its default lives in
``mlango.conf.global_settings`` — override here only what differs.
"""

import os
import sys
from pathlib import Path

# Everything relative (the SQLite file, artifacts, data files) resolves from here.
BASE_DIR = Path(__file__).resolve().parent.parent

# Praxis лежит рядом (integrations/mlango_eval -> praxis/src). Eval гоняет его пайплайн.
sys.path.insert(0, str(BASE_DIR.parent.parent / "src"))
os.environ.setdefault("PRAXIS_OFFLINE", "1")  # детерминированный прогон без GPU/сети

# Keep this out of version control in production. The environment wins, so a
# deployment sets MLANGO_SECRET_KEY and never edits this file.
SECRET_KEY = os.environ.get("MLANGO_SECRET_KEY", "Wq5C2sTPgbNIxB0jQDrn5SnoGZHUj7dKTYX9WD558eq3G8qrQRzAkg9PGzmckkc7")

DEBUG = os.environ.get("MLANGO_DEBUG", "1") == "1"

# Apps whose datasets, models, agents, evals and admin are loaded at startup.
INSTALLED_APPS = [
    "demo",
]

# Runs, metrics, artifacts, dataset/model versions and agent traces live here.
# SQLite needs no setup and is right for one process. DATABASE_URL takes over
# when there is one, which is what compose.yaml sets and what a team sharing the
# project wants: more than one worker writing runs needs a real database.
METASTORE = {
    "URL": os.environ.get("DATABASE_URL", "sqlite:///mlango.db"),
}

# Where checkpoints and materialised datasets are written.
STORAGE = {
    "BACKEND": "mlango.storage.local.LocalStorage",
    "ROOT": "artifacts",
}

# Module holding `urlpatterns` for the inference API.
ROOT_ROUTECONF = "mlango_eval.routes"

# "echo" is a deterministic offline provider: agents work with no API key, so a
# fresh checkout runs and the test suite stays free. Switch to "anthropic" and
# export ANTHROPIC_API_KEY when you want a real model.
DEFAULT_PROVIDER = "echo"
DEFAULT_AGENT_MODEL = "claude-opus-5"

# Applied to every training run. Metric recording is built in, so this list is
# purely additive.
DEFAULT_CALLBACKS = [
    "mlango.training.callbacks.ProgressBar",
]

SEED = 1337
LOG_LEVEL = "INFO"
