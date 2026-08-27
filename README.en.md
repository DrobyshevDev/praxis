# Praxis

[Русский](README.md) · **English** · [Documentation](https://drobyshevdev.github.io/praxis/)

[![CI](https://github.com/DrobyshevDev/praxis/actions/workflows/ci.yml/badge.svg)](https://github.com/DrobyshevDev/praxis/actions/workflows/ci.yml)
[![CodeQL](https://github.com/DrobyshevDev/praxis/actions/workflows/codeql.yml/badge.svg)](https://github.com/DrobyshevDev/praxis/actions/workflows/codeql.yml)
[![Licence: Apache-2.0](https://img.shields.io/badge/licence-Apache--2.0-blue)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)

A legal assistant for Russian law. It answers a question and cites the specific
provisions the answer rests on — each citation checked separately by a model. When the
law does not support a claim, it says so.

<img width="2048" height="1152" alt="Praxis answering a question with verified citations" src="https://github.com/user-attachments/assets/cd75be1d-3944-4d3f-bbbd-dba4c4d1c12f" />

## Run it

```bash
git clone https://github.com/DrobyshevDev/praxis.git
cd praxis
docker compose up app
```

Open http://localhost:8077. No keys, no GPU, no network: the image installs the `api`
extra, sets `PRAXIS_OFFLINE=1` and carries the corpus inside itself, so the
deterministic components run without a single outbound request and the default answer
is extractive — the text of the provisions themselves.

That is the downloaded-and-ran slice, not production quality. Dense retrieval, the
reranker and NLI citation checking need the `ml` extra and prefer a GPU;
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) covers bringing those up. The synthesising
mode is wired through `ANTHROPIC_API_KEY` and stays optional — retrieval works without
it.

The HTTP API and the Python client — [docs/API.md](docs/API.md).

## The problem

A lawyer has three options today, and each is awkward in its own way.

ChatGPT and other general-purpose models invent: they cite articles that do not exist,
confuse revisions, and are confidently wrong. That cannot be trusted in practice, where
the price of a mistake is a lost case or a financial loss.

KonsultantPlyus and Garant give you a document search, not an answer. Matching the
provisions and drawing the conclusion is still the lawyer's job, and the subscription is
expensive.

Search engines return forums, superseded revisions and SEO noise.

Nothing sits between these options. No tool answers a question at the speed of a model
but with references you can open and check. That is the space Praxis occupies.

## Who it is for

Lawyers and in-house counsel at small and medium businesses without access to expensive
reference systems. Accountants and HR staff with questions about the Tax, Labour and
Administrative Offences Codes. Sole traders and founders. Individuals with everyday
disputes.

The Russian market comes first because the data is available, the audience is legible and
the problems are concrete. The same architecture transfers to EU and US law, where open
data is even more plentiful (EUR-Lex, CourtListener, the Caselaw Access Project).

## How it works

The question goes through an agent that plans the search. Retrieval is hybrid over the
corpus of provisions (BM25 plus dense embeddings), a reranker selects the best, and
cross-referenced provisions are pulled in through an article-to-article graph. The
generator assembles an answer in which every claim is bound to a provision, and the
Citation Verifier checks every binding.

What separates Praxis from a wrapper around chat-with-PDF:

**Citation Verifier.** A separate NLI model checks each reference for entailment: does
the text of the provision support this specific claim? What is not confirmed is not
presented as fact.

**Agentic self-RAG.** The agent breaks a complex question into sub-queries, searches again
and reformulates until it has enough grounding. The chain of reasoning is visible in the
answer.

**GraphRAG.** Provisions reference each other ("in accordance with article 15"). That is a
ready-made graph: a question about damages surfaces article 393, and the graph pulls in
article 15 that it names.

**Extractive by default.** Without an LLM key Praxis does not compose text — it quotes the
applicable provisions verbatim with references, and such an answer cannot hallucinate.
Synthesis through Claude is enabled by a key and passes the same per-sentence citation
check.

**Measured quality.** recall@k, MRR and citation precision are computed on a golden set,
not judged by eye.

## Legal tools

On top of search, practical tasks that turn an answer into action. Everything is grounded in
the law: documents quote the provisions found verbatim, and calculators and checklist items
each carry a link to the article they rest on.

- **Trust layer.** Every provision has a "verify against the current revision" link
  (zakonrf.info) and the act's details (federal-law number and date). On low confidence it
  says "no direct answer was found" instead of a stretched answer.
- **Pre-court claim and statement of claim** (`/v1/claim`, `/v1/lawsuit`), assembled from the
  cited provisions; demands, jurisdiction and the court fee are statutory blocks.
- **Calculators** with a link to the norm (`/v1/penalty`, `/v1/fee`, `/v1/interest`): consumer
  penalty (art. 23 / 28 ZoZPP), court fee (art. 333.19 / 333.36 of the Tax Code), interest
  under art. 395 of the Civil Code.
- **Contract checklist** (`/v1/contract`) — a transparent check of essential terms and risky
  clauses against the law: explicit rules, each with a link, not "AI analysis".

The Consumer Protection Act (`corpus/zozpp.json`) was added to the corpus. The calculators and
the checklist run entirely in the browser — try them without installing at
**[drobyshevdev.github.io/praxis/try](https://drobyshevdev.github.io/praxis/try/)**. Endpoints
and examples — [docs/API.md](docs/API.md).

## Data

The statutory data is available. Codes and federal laws are published in machine-readable
form at pravo.gov.ru, and that is what the main path is built on: the repository contains
a parser for the official text (`statute_parser`) and a sample corpus of the Civil Code;
the full corpus is loaded the same way.

Six codes ship in the repository and are loaded through `PRAXIS_CORPUS_DIR`:

| File | Code |
|---|---|
| `corpus/gk-rf.json` | Civil — 1,712 articles, 4,717 provisions, all four parts |
| `corpus/nk-rf.json` | Tax |
| `corpus/koap-rf.json` | Administrative offences |
| `corpus/uk-rf.json` | Criminal |
| `corpus/tk-rf.json` | Labour |
| `corpus/zhk-rf.json` | Housing |

All six are transcriptions from Wikisource, as the `edition` field in each file states.
The revision in force has to be checked against pravo.gov.ru — which is what the parser
for the official text is in the repository for.

The texts of the codes are official documents and, under article 1259(6) of the Civil
Code, are not subject to copyright. Apache-2.0 in this repository covers the code, the
parser, the cross-reference graph and the corpus markup, not the texts of the laws
themselves.

Judicial practice is harder. There is no open structured corpus for Russia comparable to
the Caselaw Access Project, and kad.arbitr and the GAS "Pravosudie" system give up their
data reluctantly. That is the next stage, as a separate pipeline.

## Quality

A run of the eval harness over the golden set (12 questions, `praxis-eval`):

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
article per question while the system also returns adjacent relevant provisions. That is
fixed by labelling several correct articles per question.

On the full Civil Code corpus (4,717 provisions, an 18-question golden set) the real
models hold recall@5 0.92, MRR 0.94, hit-rate 1.0 and confidence 0.80. The offline
fallback drops to recall 0.64 at that size — on real data, real models are not optional.

## Roadmap

- v0. Skeleton, domain models, legal-aware chunking, BM25 baseline. Done.
- v1. Hybrid retrieval and reranking, Citation Verifier, self-RAG, eval, FastAPI and a web
  UI. Done. Every ML component has a real implementation on GPU or through Claude, and a
  deterministic offline fallback.
- v2. Real ingestion of the official text, GraphRAG over cross-references, a GPU run. Done.
- v3. The full corpus of codes and federal laws from pravo.gov.ru, judicial practice and a
  provision-to-case graph, span-level citation highlighting in the UI, an expanded golden
  set.
- v4. The full Civil Code extracted into the repository, a public API (`/v1`) with CORS and
  a Python client, competitive analysis. Desktop and mobile on the same API are next.

How to run it — [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Stack and ecosystem

Python 3.12, FastAPI, Docker. Retrieval: BM25 and BGE-M3 dense embeddings,
bge-reranker-v2-m3 as the reranker. Citation checking: NLI on GPU.

The dense index is held in memory and cached to disk (`PRAXIS_CACHE_DIR`), with a pure
standard-library fallback — which is why the offline image and CI run without numpy at
all. A Postgres index with pgvector is designed and not wired:
`src/praxis/index/schema.sql` is in the repository, a retriever for it is not.

The LLM is plugged in through a provider. Claude for synthesis and a deterministic mock
for tests are implemented; the provider contract is `src/praxis/llm/base.py`. Russian
providers (GigaChat, YandexGPT) for data-residency scenarios are the next step, not
something that can be switched on today.

The project uses two libraries from the same organisation:
[glia](https://github.com/DrobyshevDev/glia) for the agent loop in LLM mode (search is
exposed as a glia tool, and the trace comes from its trajectory), and
[mlango](https://github.com/DrobyshevDev/mlango) for a tracked golden eval through its
evals subsystem (`integrations/mlango_eval`, `manage.py evaluate`).

Architecture — [ARCHITECTURE.md](ARCHITECTURE.md).

## Openness and clients

Everything is open (Apache-2.0) and runs locally without third-party tokens. The core
functionality — search, citation checking, answers — needs neither keys nor paid services:
local models download from HuggingFace for free, and the default answer is extractive, the
verbatim text of the provisions. Claude is an optional path to synthesis, not a condition
of the system working. Paid features and a subscription are for later.

A single API core (`/v1`) serves every client: the web UI now, desktop and mobile as thin
clients on the same API later. For ML practitioners there is a public API with CORS, an
OpenAPI schema and a Python client — [docs/API.md](docs/API.md).

Competitive analysis and where the project wins —
[docs/COMPETITIVE.md](docs/COMPETITIVE.md).

---

**Not legal advice.** Praxis surfaces provisions and checks that a citation supports a
claim. It does not assess your situation, does not account for procedural context, and
does not replace a lawyer.
