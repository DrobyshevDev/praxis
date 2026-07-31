"""Датасет над golden set Praxis — вопросы с эталонными статьями."""

from mlango.core import fields
from mlango.data import Dataset, PythonSource

from praxis.eval.golden import GOLDEN


def _cases():
    for index, gc in enumerate(GOLDEN):
        yield {
            "id": index,
            "question": gc.question,
            "expected": " ".join(sorted(gc.relevant)),  # номера эталонных статей
        }


class GoldenCases(Dataset):
    """Юридические вопросы с эталонными статьями (из praxis.eval.golden)."""

    id = fields.IntegerField()
    question = fields.TextField()
    expected = fields.TextField()

    class Meta:
        source = PythonSource(_cases, count=len(GOLDEN))
        primary_key = "id"
