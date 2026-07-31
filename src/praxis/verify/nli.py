"""Реальный NLI-верификатор (three-way entailment). Extra `ml`, GPU.

premise = текст нормы, hypothesis = тезис ответа. entailment → SUPPORTS,
contradiction → CONTRADICTS, neutral → UNRELATED. По умолчанию русская модель
`cointegrated/rubert-base-cased-nli-threeway`; для мультиязычного корпуса можно
подменить на multilingual DeBERTa-NLI. Ленивая загрузка.
"""

from __future__ import annotations

from ..core.models import Citation, Verdict, VerifiedClaim


class NLIVerifier:
    """Реализует протокол `verify.base.CitationVerifier`."""

    def __init__(
        self,
        model_name: str = "cointegrated/rubert-base-cased-nli-threeway",
        device: str | None = None,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._tok = None
        self._model = None
        self._torch = None

    def _ensure(self):
        if self._model is None:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self._torch = torch
            self._device = self._device or ("cuda" if torch.cuda.is_available() else "cpu")
            self._tok = AutoTokenizer.from_pretrained(self._model_name)
            self._model = (
                AutoModelForSequenceClassification.from_pretrained(self._model_name)
                .to(self._device)
                .eval()
            )
        return self._model

    def verify(self, claim: str, citation: Citation) -> VerifiedClaim:
        model = self._ensure()
        torch = self._torch
        inputs = self._tok(
            citation.provision.text,
            claim,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self._device)
        with torch.no_grad():
            probs = torch.softmax(model(**inputs).logits[0], dim=-1)

        id2label = {i: str(lbl).lower() for i, lbl in model.config.id2label.items()}
        scores = {id2label[i]: float(probs[i]) for i in range(len(probs))}
        ent = scores.get("entailment", 0.0)
        con = scores.get("contradiction", 0.0)
        neu = scores.get("neutral", 0.0)

        if ent >= max(con, neu):
            return VerifiedClaim(claim, citation, Verdict.SUPPORTS, ent)
        if con >= max(ent, neu):
            return VerifiedClaim(claim, citation, Verdict.CONTRADICTS, con)
        return VerifiedClaim(claim, citation, Verdict.UNRELATED, neu)
