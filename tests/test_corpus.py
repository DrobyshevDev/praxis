import json

from praxis.ingest import load_sample_provisions
from praxis.ingest.corpus import load_corpus_dir


def _write_act(dirpath):
    (dirpath / "nk.json").write_text(
        json.dumps(
            {
                "id": "nk-rf-1",
                "kind": "кодекс",
                "title": "Налоговый кодекс РФ",
                "short_title": "НК РФ",
                "articles": [
                    {"number": "3", "title": "Основные начала", "text": "Каждый обязан платить налоги."}
                ],
            }
        ),
        encoding="utf-8",
    )


def test_load_corpus_dir(tmp_path):
    _write_act(tmp_path)
    acts = load_corpus_dir(tmp_path)
    assert len(acts) == 1
    assert acts[0].short_title == "НК РФ"


def test_load_sample_provisions_uses_env_corpus(tmp_path, monkeypatch):
    _write_act(tmp_path)
    monkeypatch.setenv("PRAXIS_CORPUS_DIR", str(tmp_path))
    provisions = load_sample_provisions()
    assert provisions
    assert all(p.act.short_title == "НК РФ" for p in provisions)
    assert any(p.citation == "ст. 3 НК РФ" for p in provisions)


def test_default_corpus_without_env():
    # без PRAXIS_CORPUS_DIR — образец ГК
    provisions = load_sample_provisions()
    assert any(p.act.short_title == "ГК РФ" for p in provisions)
