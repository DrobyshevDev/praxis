"""Имя дистрибутива — не то же самое, что имя импорта.

`praxis[agent]` требовал `glia>=0.8`, потому что импорт выглядит как
`from glia import Agent`. Но на PyPI имя `glia` занято чужим пакетом (Glial
Engines, последняя версия 0.1.0.dev6), а библиотека этой организации
публикуется как `glia-agents`. То есть установка extra либо падала на
разрешении версий, либо — появись однажды под тем именем версия 0.8 —
молча тянула бы чужой код в юридического ассистента.

Разница видна только тому, кто держит в голове оба имени сразу, поэтому её
держит тест.
"""

from __future__ import annotations

import pathlib
import tomllib

_PYPROJECT = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"

# Пакеты организации, у которых имя дистрибутива расходится с именем импорта.
_DISTRIBUTION_BY_IMPORT = {"glia": "glia-agents"}


def _requirements() -> list[str]:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    project = data["project"]
    requirements = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        requirements.extend(extra)
    return requirements


def _name_of(requirement: str) -> str:
    """Имя пакета из строки требования, без версии и extras."""
    for separator in ("[", ">", "<", "=", "!", "~", ";", " "):
        requirement = requirement.split(separator, 1)[0]
    return requirement.strip().lower().replace("_", "-")


def test_no_requirement_uses_an_import_name_owned_by_someone_else():
    named = {_name_of(r) for r in _requirements()}
    for import_name, distribution in _DISTRIBUTION_BY_IMPORT.items():
        assert import_name not in named, (
            f"pyproject.toml требует {import_name!r}, но на PyPI под этим именем "
            f"лежит чужой пакет; нужный дистрибутив называется {distribution!r}"
        )


def test_the_agent_extra_pulls_the_organisations_own_glia():
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    agent = data["project"]["optional-dependencies"]["agent"]
    assert any(_name_of(r) == "glia-agents" for r in agent), agent
