[![CI](https://github.com/IsaacVanB/dream-journal-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/IsaacVanB/dream-journal-analyzer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-red)

# Dream Journal Analyzer

A privacy-first local AI system for searching, analyzing, and exploring a long-running dream journal.

Dream Journal Analyzer combines local LLMs, dense and keyword retrieval, agentic tool use, and longitudinal analysis to answer natural-language questions about a personal dream journal without sending journal contents to external AI services.

The project is also an experimental platform for evaluating retrieval strategies—including semantic search, BM25, hybrid retrieval, and LLM-directed search—on a labeled synthetic benchmark.

## What it does

- **Natural-language journal exploration** through a tool-calling local LLM agent
- **Semantic search** with Ollama embeddings and ChromaDB
- **BM25 keyword search** for names, places, exact phrases, and rare terms
- **Hybrid retrieval** using reciprocal-rank fusion
- **Evidence-grounded responses** with retrieved dream IDs and dates
- **Structured filtering** by tags and date ranges
- **Journal statistics and longitudinal tag trends**
- **Recurring-theme discovery** with UMAP + HDBSCAN clustering
- **Structured dream feature extraction**
- **Incremental index synchronization** without rebuilding unchanged data
- **Retrieval benchmarking** across fixed and agent-driven strategies

All model inference and journal processing can run locally through [Ollama](https://ollama.com/).

## Quick start

Requires Python 3.10+ and a local [Ollama](https://ollama.com/) installation.

```bash
git clone https://github.com/IsaacVanB/dream-journal-analyzer.git
cd dream-journal-analyzer

python -m pip install --editable ".[dev]"

ollama pull nomic-embed-text
ollama pull qwen3:8b
```

The `examples/` directory contains a synthetic journal with 176 dreams from
2022–2026, its parsed corpus, character dictionary, and labeled retrieval suite,
so the complete pipeline can be tested without providing personal data.

```bash
dream-analyzer parse \
  examples/mock_dream_journal.txt \
  data/sample/dreams.jsonl
dream-analyzer index \
  --dreams-path data/sample/dreams.jsonl \
  --chroma-path data/sample/chroma_db

dream-analyzer ask \
  "What patterns appear in dreams about hidden rooms?" \
  --dreams-path data/sample/dreams.jsonl \
  --chroma-path data/sample/chroma_db
```

To work with your own journal, copy it to the default private path and run the
parsing and indexing commands without path arguments:

```bash
mkdir -p data
cp path/to/journal.txt data/mock_dream_journal.txt
dream-analyzer parse
dream-analyzer index
```

The entire `data/` directory is ignored by Git. It is reserved
for private source journals, parsed records, character notes, import state, and
the local Chroma index, so pulls cannot replace those files. Back up this
directory separately; cloning the repository does not restore it. Commands
still accept explicit paths when a different location is preferred.

See [`example_usages.md`](example_usages.md) for detailed command options and workflows.

## CLI

```text
dream-analyzer parse               Parse journal text into structured JSONL
dream-analyzer index               Build or synchronize the retrieval index
dream-analyzer ask                 Ask a natural-language question
dream-analyzer analyze             Analyze an individual dream
dream-analyzer stats               Compute journal statistics
dream-analyzer trends              Analyze and plot tag trends
dream-analyzer cluster             Discover recurring themes
dream-analyzer evaluate-retrieval  Benchmark retrieval strategies
```

Run `dream-analyzer <command> --help` for command-specific options.

## Architecture

```text
                     ┌── Semantic search ── ChromaDB + embeddings ─┐
                     │                                             │
Journal → Parser ────┼── BM25 search ───── lexical index ─────────┼──→ Tools
                     │                                             │      │
                     ├── Tags / dates / statistics ───────────────┤      ▼
                     │                                             │   Local LLM
                     └── Embeddings ── UMAP + HDBSCAN ────────────┘      │
                                                                         ▼
                                                               Grounded response
```

The system separates reusable retrieval and analytical services from CLI and agent orchestration. The LLM can choose among search and deterministic analysis tools rather than attempting to answer every question directly from model context.

## Retrieval evaluation

Retrieval is evaluated on labeled benchmarks covering topical, lexical, entity,
compositional, temporal, and low-overlap queries. Scores should be compared
within each table rather than across the two datasets.

### Synthetic journal (56 queries)

These results use the 176 dreams from the included sample journal, which was generated by GPT-5.6. It was prompted to reproduce features commonly found in real dream journals, including recurring themes, imagery and characters; tagged dreams; typos; and varying levels of coherence and detail. Entries range from streams of consciousness to complete sentences and bulleted lists. The word count ranges from 8 to 77 words.

The benchmark includes 56 queries across different categories, including proper names, rare objects, exact places, inflected variants, separated phrase terms, mixed entity/concept queries, and queries with little or no lexical overlap. The queries were also generated by GPT-5.6.

| Strategy | Embedding model | Chat model | R@5 | R@10 | R-precision | Time/query |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Agent | qwen3-embedding | gemma4:12b | **0.676** | 0.763 | **0.608** | 50.793 s |
| Agent | nomic-embed-text | qwen3:8b | 0.659 | **0.783** | 0.537 | 9.920 s |
| Agent | nomic-embed-text | gemma4:12b | 0.656 | 0.716 | 0.554 | 24.840 s |
| Agent | qwen3-embedding | qwen3:8b | 0.652 | 0.746 | 0.574 | 16.389 s |
| Fixed hybrid | nomic-embed-text | — | 0.636 | 0.736 | 0.434 | 0.103 s |
| BM25 baseline | — | — | 0.602 | 0.677 | 0.596 | **<0.001 s** |
| Fixed hybrid | qwen3-embedding | — | 0.589 | 0.680 | 0.444 | 0.359 s |
| Semantic baseline | nomic-embed-text | — | 0.411 | 0.469 | 0.416 | 0.094 s |
| Semantic baseline | qwen3-embedding | — | 0.403 | 0.445 | 0.357 | 0.458 s |

On the synthetic benchmark, the `qwen3-embedding` and `gemma4:12b` agent has the highest R-precision and R@5,
while the `nomic-embed-text` and `qwen3:8b` agent has the highest R@10. BM25 remains
the fastest strategy and has the second-highest R-precision.

See [`leaderboard.md`](outputs/retrieval_evaluations/leaderboard.md) for more detailed synthetic-journal evaluation results.

### Two-month sample of a real journal (39 queries)

These results use 91 dreams from a two-month section of my personal dream journal. The entries contain recurring themes, imagery, characters, tags, and typos, with varying levels of coherence and detail. They range from streams of consciousness and bulleted lists (including detailed or typo-riddled nonsense) to single words or names. The word count ranges from 1 to 542 words.

The benchmark includes 39 queries across the same categories seen in the AI-generated benchmark. The queries and their corresponding relevant dreams were compiled manually, a particularly time-consuming process.

| Strategy | Embedding model | Chat model | R@5 | R@10 | R-precision | Time/query |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Agent | nomic-embed-text | qwen3:8b | **0.721** | **0.852** | 0.580 | 9.987 s |
| Agent | nomic-embed-text | gemma4:12b | 0.710 | 0.811 | **0.662** | 33.530 s |
| Agent | qwen3-embedding | qwen3:8b | 0.666 | 0.757 | 0.513 | 19.206 s |
| Agent | qwen3-embedding | gemma4:12b | 0.659 | 0.765 | 0.566 | 35.966 s |
| Fixed hybrid | nomic-embed-text | — | 0.634 | 0.831 | 0.565 | 0.083 s |
| BM25 baseline | — | — | 0.599 | 0.732 | 0.586 | **<0.001 s** |
| Fixed hybrid | qwen3-embedding | — | 0.582 | 0.719 | 0.414 | 0.363 s |
| Semantic baseline | nomic-embed-text | — | 0.578 | 0.703 | 0.497 | 0.217 s |
| Semantic baseline | qwen3-embedding | — | 0.340 | 0.481 | 0.211 | 0.615 s |

On the real-journal benchmark, the `nomic-embed-text` and `qwen3:8b` agent has the highest recall at both cutoffs, while the `nomic-embed-text` and `gemma4:12b` agent has the highest R-precision. BM25 remains the fastest strategy.

### Evaluation details

For both experiments, temperature was set to 0. Both sets of retrieval queries used the same categories. When making the retrieval set for my dreams, I tried to match (or exceed) the “difficulty” of the AI-generated queries.

Recall@k measures how much of the known relevant set is recovered within the first k results. R-precision evaluates precision after retrieving exactly R results, where R is the number of known relevant dreams for that query, making it useful when queries have different numbers of relevant results.

In both cases, agents outperformed the BM25, semantic-search, and fixed-hybrid baselines, but the optimal embedding and chat models differed. Using `nomic-embed-text` for embedding and `qwen3:8b` for chat gave good results for both journals, with the fastest average query time among the four agent configurations. This combination may be a good default, but the best model combination will likely vary by user. Because the models run locally, users must consider hardware constraints when choosing them; response times exceeding 30 seconds per query may be impractical.

Differences in performance are likely due to variations in writing style, vocabulary, content, and length. These factors vary from person to person. In these samples, real dreams were more chaotic than AI-generated dreams, and their recurring themes were subtler.

In this project's experiments, `nomic-embed-text` performed better on short queries like those in the evaluation sets, whereas `qwen3-embedding` performed better on longer queries, such as requests to find dreams similar to a supplied dream.

```bash
dream-analyzer evaluate-retrieval \
  --retrieval-mode hybrid \
  --experiment-name "hybrid baseline" \
  --experiment-note "Verbatim semantic and BM25 retrieval fused with RRF" \
  --leaderboard-name personal_results
```

## Tech stack

- Runtime: Python 3.10+, Ollama, ChromaDB, NumPy, Pandas, scikit-learn,
  UMAP, HDBSCAN, Matplotlib, and Plotly
- Retrieval and AI: local LLMs and embeddings, RAG, tool calling, an in-project
  BM25 implementation, and reciprocal-rank fusion
- Development: pytest, Ruff, and GitHub Actions

The project uses a `src` package layout with automated tests, linting, and CI.
