# Praxis

**A legal assistant for Russian law.** It answers a question and cites the specific
provisions the answer rests on — each citation checked separately by a model. When the
law does not support a claim, it says so instead of producing plausible text.

```bash
docker compose up app     # → http://localhost:8077, no API keys required
```

## Why

A lawyer working on Russian law has three options today, each awkward in its own way.
General-purpose models invent: they cite articles that do not exist, confuse revisions,
and are confidently wrong. Commercial reference systems search documents rather than
answer, and are expensive. Search engines return forums, superseded revisions and SEO
noise.

Nothing sits between them: no tool answers at the speed of a model with references you
can open and check. That is the gap Praxis fills.

## How it works

The question goes through an agent that plans the search. Retrieval is hybrid over the
corpus of provisions — BM25 plus dense embeddings — a reranker selects the best, and
provisions connected by cross-reference are pulled in through an article-to-article
graph. The generator assembles an answer in which every claim is bound to a provision,
and the Citation Verifier checks every binding.

**Citation Verifier.** A separate NLI model checks each reference for entailment: does
the text of the provision actually support this specific claim? What is not confirmed is
not presented as fact.

**Agentic self-RAG.** The agent decomposes a complex question into sub-queries, searches
again and reformulates until it has enough grounding. The chain of reasoning is visible
in the answer.

**GraphRAG.** Provisions reference each other ("in accordance with article 15"). That is
a ready-made graph: a question about damages surfaces article 393, and the graph pulls in
article 15 that it names.

**Extractive by default.** Without an LLM key Praxis does not compose text — it quotes
the applicable provisions verbatim with references, and an answer like that cannot
hallucinate. Synthesis through Claude is enabled by a key and passes the same
per-sentence citation check.

## Quality

The eval harness over the golden set (12 questions, `praxis-eval`):

| Metric | Real models (RTX 4060) | Offline fallback |
|---|---|---|
| recall@5 | 1.00 | 1.00 |
| MRR | 1.00 | 0.90 |
| hit-rate | 1.00 | 1.00 |
| mean confidence | 0.88 | 0.63 |
| citation precision | 0.29 | 0.40 |

Real models: BGE-M3 for embeddings, bge-reranker-v2-m3 for reranking, rubert-NLI for
citation checking, all on GPU. The needed provision always reaches the top of the
results. Citation precision is understated because the golden set has one reference
article per question while the system also returns adjacent relevant provisions.

On the full Civil Code corpus (4,717 provisions, an 18-question golden set) the real
models hold recall@5 0.92, MRR 0.94, hit-rate 1.0 and confidence 0.80. The offline
fallback drops to recall 0.64 at that size — on real data the real models are not
optional.

## Data

Codes and federal laws are published in machine-readable form at pravo.gov.ru, and the
repository contains a parser for the official text (`statute_parser`). The full text of
the Civil Code is already extracted (`corpus/gk-rf.json` — 1,712 articles, 4,717
provisions, all four parts) and is loaded through `PRAXIS_CORPUS_DIR`. The revision in
force should always be checked against the official source.

There is no open structured corpus of Russian judicial practice comparable to the
Caselaw Access Project; that is the next pipeline rather than something already shipped.

## Next

- [Public API](API.md) — the `/v1` endpoints, the response format, the Python client.
- [Development](DEVELOPMENT.md) — running it locally and what CI checks.
- [Comparison](COMPETITIVE.md) — where Praxis wins and where it does not.
- [Architecture](https://github.com/DrobyshevDev/praxis/blob/master/ARCHITECTURE.md) — layers and data flow.

!!! warning "Not legal advice"
    Praxis surfaces provisions and checks that a citation supports a claim. It does not
    assess your situation, does not account for procedural context, and does not replace
    a lawyer. Always verify the revision in force against the official source.
