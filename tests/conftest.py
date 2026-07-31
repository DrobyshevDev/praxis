"""Тесты всегда идут в offline-режиме: детерминированные fallback-компоненты,
без скачивания GPU-моделей и без сети. Реальные модели проверяются отдельным
запуском со снятым PRAXIS_OFFLINE.
"""

import os

os.environ.setdefault("PRAXIS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
