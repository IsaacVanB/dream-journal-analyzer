# Example Usages

These examples assume the project has been installed in editable mode with
`pip install -e .` as described in the README.

The project-local `data/` directory is reserved for private user data and is
ignored by Git. Put a journal at `data/mock_dream_journal.txt` to use the default
paths. The tracked synthetic journal, parsed corpus, character dictionary, and
retrieval labels are kept separately under `examples/`.

The preferred interface is the installed `dream-analyzer` command. It provides
help at both levels:

```bash
dream-analyzer --help
dream-analyzer parse --help
dream-analyzer index --help
dream-analyzer ask --help
dream-analyzer analyze --help
dream-analyzer stats --help
dream-analyzer trends --help
dream-analyzer cluster --help
dream-analyzer evaluate-retrieval --help
```

The matching scripts under `src/cli/` remain available temporarily for
backward compatibility. Utilities that do not yet have a consolidated
subcommand continue to use their script entry points below.

## `dream-analyzer parse`

Parses the raw dream journal text file into JSON Lines, one JSON object per dream.

```bash
dream-analyzer parse
dream-analyzer parse examples/mock_dream_journal.txt data/sample/dreams.jsonl
dream-analyzer parse other_journal.txt data/other_dreams.jsonl --dream-separator-blank-lines 2
```

Arguments:

- `input`: optional path to the raw journal text file. Defaults to `data/mock_dream_journal.txt`.
- `output`: optional path for parsed JSONL output. Defaults to `data/dreams.jsonl`.
- `--dream-separator-blank-lines`: number of consecutive blank lines that separates dreams. Defaults to auto-detection.

Output fields include `dream_id`, `date`, `year`, `month`, `day`, `date_precision`, `date_sort`, `tags`, `text`, and `word_count`.

The parser validates calendar dates before writing the JSONL file. An impossible
date stops the command and identifies the original value and journal line number
for manual correction. Zero placeholders remain valid for supported partial or
unknown dates: `0/0/YYYY`, `M/0/YYYY`, and `0/0/00` or `0/0/0000`.

## `src/cli/sync_dream_journal.py`

Synchronizes an ongoing append-only journal with an existing parsed JSONL file
and records the new IDs for downstream work:

```bash
python3 src/cli/sync_dream_journal.py path/to/journal.txt --dry-run
python3 src/cli/sync_dream_journal.py path/to/journal.txt
```

Arguments:

- `input`: required path to the append-only raw journal text file.
- `--dreams-path`: parsed dream JSONL file to compare and update. Defaults to
  `data/dreams.jsonl`.
- `--state`: import-state JSON file that records each synchronization and its
  newly introduced IDs. Defaults to `data/dream_imports.json`.
- `--dry-run`: validate and report the proposed synchronization without writing
  the parsed dreams or import state.
- `--minimum-similarity`: minimum similarity accepted for small corrections to
  an existing dream in the old positional prefix. Defaults to `0.9`.
- `--dream-separator-blank-lines`: explicit number of consecutive blank lines
  separating dreams. Defaults to parser auto-detection.

Small corrections to the old positional prefix retain their IDs. Truncation,
reordering, insertion into that prefix, or a substantive edit stops the import.
Use `--minimum-similarity` to adjust the conservative edit threshold and
`--state` to choose a non-default import-state file.

## `src/cli/check_dates.py`

Checks parsed dreams for suspicious years, duplicate dates, and duplicate dream IDs. It is helpful for finding human errors in dream journal dates and does not modify the data. Dates containing `0` placeholders are ignored during date checks, but their dream IDs are still checked for duplicates.

```bash
python3 src/cli/check_dates.py
python3 src/cli/check_dates.py --dreams-path data/other_dreams.jsonl
python3 src/cli/check_dates.py --max-isolated-dates 5 --json
```

Arguments:

- `--dreams-path`: path to parsed dream JSONL records. Defaults to `data/dreams.jsonl`.
- `--max-isolated-dates`: largest surrounded year run to flag. Defaults to `3` dates.
- `--max-year-jump`: largest adjacent year change not flagged. Defaults to `1`.
- `--json`: print machine-readable JSON instead of the text report.

## `dream-analyzer index`

Embeds only each dream's text with Ollama `nomic-embed-text` and saves the vectors to a persistent ChromaDB collection. Dates, tags, and other metadata remain available for display and filtering but do not affect similarity.

```bash
dream-analyzer index
dream-analyzer index --dreams-path data/dreams.jsonl --chroma-path data/chroma_db
dream-analyzer index --embed-model qwen3-embedding --collection-name dreams_qwen3_embedding --batch-size 16
dream-analyzer index --rebuild
dream-analyzer index --prune
```

Arguments:

- `--dreams-path`: path to parsed dream JSONL records. Defaults to `data/dreams.jsonl`.
- `--chroma-path`: directory for the persistent ChromaDB database. Defaults to `data/chroma_db`.
- `--collection-name`: ChromaDB collection to synchronize. Defaults to `dreams_nomic_embed_text`.
- `--embed-model`: Ollama embedding model. Defaults to `nomic-embed-text`.
- `--batch-size`: number of new dream texts sent to Ollama per embedding request. Defaults to `32`.
- `--rebuild`: replace the collection and regenerate every vector. Without it,
  the command adds missing dream IDs and preserves existing embeddings.
- `--prune`: delete indexed IDs absent from the current parsed journal. Exact
  text matches are automatically migrated from an orphaned legacy ID to a new
  corrected ID without generating another embedding.

Requires Ollama running locally at `http://localhost:11434`. After changing the
embedding logic, run this command with `--rebuild` to regenerate the index.

## Retrieval scoring reference

The commands currently use two different scoring paths:

| Command | Score used for retrieval | Score direction |
|---|---|---|
| `src/cli/retrieve_dreams.py` | Chroma distance | Lower is closer. |
| `src/cli/basic_rag.py` | Chroma distance | Lower is closer. |
| `dream-analyzer ask` | Chroma distance | Lower is closer; date bounds optionally filter the ranked search. |
| `src/cli/evaluate_retrieval.py` | Selectable; agent default | Runs the labeled benchmark through the dream agent or direct query embeddings. |
| `src/cli/evaluate_retrieval_llm.py` | Configurable | Chroma distance by default; cosine similarity or both are selectable. |
| `src/cli/compare_models.py rag` | Chroma distance | Lower is closer. |
| `dream-analyzer analyze` with related dreams enabled | Cosine similarity | Higher is more similar. |
| `src/cli/compare_models.py analyze` | Cosine similarity | Higher is more similar. |

Chroma-distance and cosine-similarity scores are not interchangeable and may
produce different rankings.

## `dream-analyzer trends`

Plots dream tag frequency over time and saves the image to `outputs/plots/`.

```bash
dream-analyzer trends
dream-analyzer trends --tags house recurring school --freq M
dream-analyzer trends --tag school --normalize
dream-analyzer trends --freq Y --normalize --output outputs/plots/tags_by_year.png
dream-analyzer trends --start-date 2023-01-01 --end-date 2023-12-31
```

Arguments:

- `--dreams-path`: path to parsed dream JSONL records. Defaults to `data/dreams.jsonl`.
- `--output`: path where the plot image should be saved. Defaults to `outputs/plots/tag_frequency.png`.
- `--tags` / `--tag`: specific tags to plot. Defaults to the top tags.
- `--top-n`: number of top tags to plot when `--tags` is omitted. Defaults to `10`.
- `--freq`: time grouping frequency: `M`, `Q`, or `Y`. Defaults to `M`.
- `--start-date`: only include dreams on or after this date.
- `--end-date`: only include dreams on or before this date.
- `--normalize`: plot percent of dreams per period instead of raw counts.
- `--title`: optional plot title.
- `--show`: display the plot interactively after saving.

## `dream-analyzer stats`

Computes dream counts, tag frequencies, and word-count statistics, then prints and saves JSON.

```bash
dream-analyzer stats
dream-analyzer stats --freq Q --start-date 2023-01-01 --end-date 2023-12-31
dream-analyzer stats --freq Y --output outputs/stats/yearly_stats.json
dream-analyzer stats --common-words 50 --stopwords-path data/stopwords.txt
```

Arguments:

- `--dreams-path`: path to parsed dream JSONL records. Defaults to `data/dreams.jsonl`.
- `--output`: path where JSON stats should be saved. Defaults to `outputs/stats/dream_stats.json`.
- `--freq`: time grouping frequency for entry counts: `M`, `Q`, or `Y`. Defaults to `M`.
- `--start-date`: only include dreams on or after this date.
- `--end-date`: only include dreams on or before this date.
- `--common-words`: number of most common non-trivial words to include. Defaults to `20`.
- `--stopwords-path`: optional text file of additional stopwords, one per line.
- `--min-word-length`: minimum word length for common-word stats. Defaults to `3`.

## `src/cli/retrieve_dreams.py`

Embeds a text query and returns the closest dreams from the ChromaDB collection.

```bash
python3 src/cli/retrieve_dreams.py "hidden room water"
python3 src/cli/retrieve_dreams.py "school anxiety" --top-k 5
```

Arguments:

- `query`: required text query to search for.
- `--top-k`: number of closest dreams to return. Defaults to `10`.
- `--chroma-path`: path to the persistent ChromaDB database. Defaults to `data/chroma_db`.
- `--collection-name`: ChromaDB collection name to query. Defaults to
  `dreams_nomic_embed_text`.
- `--embed-model`: Ollama embedding model. Defaults to `nomic-embed-text`.
- `--preview-chars`: maximum preview length per result. Defaults to `300`.

Requires an existing ChromaDB index and Ollama running locally at `http://localhost:11434`.

## `dream-analyzer cluster`

Clusters embeddings already stored in ChromaDB. It writes a per-dream CSV, an
interactive HTML map, two PNG maps, and a Markdown evidence report under
`outputs/clusters/`. It does not regenerate embeddings.

```bash
dream-analyzer cluster
dream-analyzer cluster --collection-name dreams_qwen3_embedding
dream-analyzer cluster --min-cluster-size 7 --n-neighbors 10
dream-analyzer cluster --label-clusters --label-model qwen3:8b
```

Arguments:

- `--chroma-path`: directory containing the persistent ChromaDB database.
  Defaults to `data/chroma_db`.
- `--collection-name`: stored collection to cluster. Defaults to `dreams`.
- `--output-dir`: directory for CSV, HTML, PNG, and Markdown artifacts. Defaults
  to `outputs/clusters`.
- `--pca-dimensions`: maximum dimensions retained by the optional PCA
  preprocessing step. Defaults to `50`.
- `--n-neighbors`: UMAP neighborhood size. Defaults to `15`.
- `--min-dist`: UMAP minimum distance. Defaults to `0.1`.
- `--min-cluster-size`: smallest grouping HDBSCAN may treat as a cluster.
  Defaults to `5`.
- `--min-samples`: HDBSCAN conservativeness. Defaults to `1`; increasing it
  usually classifies more dreams as noise.
- `--random-state`: random seed used for reproducible dimensionality reduction.
  Defaults to `42`.
- `--top-terms`: number of distinctive TF-IDF terms reported per cluster.
  Defaults to `8`.
- `--top-tags`: number of overrepresented journal tags reported per cluster.
  Defaults to `5`.
- `--representative-dreams`: number of representative dreams included per
  cluster. Defaults to `3`.
- `--label-clusters`: replace automatic evidence-based labels with short labels
  generated by a local Ollama chat model.
- `--label-model`: Ollama chat model used when `--label-clusters` is enabled.
  Defaults to `qwen3:8b`.

The report includes representative dreams, distinctive TF-IDF terms,
overrepresented tags, noise fraction, and non-noise silhouette score.

## `src/cli/basic_rag.py`

Retrieves relevant dreams for a question and asks an Ollama chat model to answer using only those entries.

```bash
python3 src/cli/basic_rag.py "What patterns appear in dreams about hidden rooms?"
python3 src/cli/basic_rag.py "What symbols recur in school dreams?" --top-k 5 --chat-model qwen3:8b
python3 src/cli/basic_rag.py "What patterns appear in dreams about hidden rooms?" --retrieval-query "hidden room hidden hallway secret room"
```

Arguments:

- `question`: required question or prompt to answer.
- `--top-k`: number of dream entries to retrieve. Defaults to `8`.
- `--retrieval-query`: optional focused query to embed for retrieval. If omitted, the chat model generates one from `question`.
- `--chroma-path`: path to the persistent ChromaDB database. Defaults to `data/chroma_db`.
- `--collection-name`: ChromaDB collection name to query. Defaults to
  `dreams_nomic_embed_text`.
- `--embed-model`: Ollama embedding model. Defaults to `nomic-embed-text`.
- `--chat-model`: Ollama chat model. Defaults to `qwen3:8b`.
- `--max-chars-per-dream`: maximum context characters per retrieved dream. Defaults to `2500`.
- `--num-ctx`: Ollama context window option. Defaults to `4096`.
- `--num-predict`: maximum generated tokens. Defaults to `700`.
- `--temperature`: sampling temperature. Defaults to `0.1`.

Requires an existing ChromaDB index and Ollama running locally at `http://localhost:11434`.

## `dream-analyzer ask`

Answers a question with semantic search, date and tag filters, journal
statistics, and optional character data. Answers cite dream IDs and dates.
Multiple tags use AND matching.

```bash
dream-analyzer ask "What patterns appear in dreams about hidden rooms?"
dream-analyzer ask "What are common themes in dreams from last month?"
dream-analyzer ask "How many dreams did I record in 2025?"
dream-analyzer ask "What words occurred most often last year?"
dream-analyzer ask "Did school-tagged dreams become more common during 2025?"
dream-analyzer ask "Who appears most often in my structured dreams?"
dream-analyzer ask "Who is Maya?"
dream-analyzer ask \
  "What are common themes in dreams about school? Use only dreams from last month."
dream-analyzer ask "How do school anxiety dreams appear?" \
  --top-k 5 \
  --chat-model qwen3:8b \
  --embed-model nomic-embed-text \
  --output outputs/agent/school_anxiety.md

dream-analyzer ask "Compare house and school dreams" \
  --max-tool-calls 3 \
  --debug \
  --output outputs/agent/comparison_trace.md
```

Arguments:

- `question`: required question to answer from the journal.
- `--top-k`: maximum results returned by each search call. Defaults to `8` and is capped at `20`.
- `--max-tool-calls`: maximum tool calls permitted for one answer. Defaults to `3`.
- `--max-synthesis-dreams`: maximum unique dreams included in the final answer prompt. Defaults to `10` and is capped at `20`.
- `--max-chars-per-dream`: maximum journal characters per search result returned to the model. The Markdown report still contains the full text. Defaults to `2500`.
- `--output`: optional path for a Markdown report containing the question, settings, searches, citations, full text of every unique retrieved dream, and answer. Repeated dreams are listed in each applicable search table, but their full text appears once and is not added to the model's bounded context.
- `--debug`: print assistant messages and Ollama response diagnostics and include them in the Markdown report.
- `--chroma-path`: persistent ChromaDB directory. Defaults to `data/chroma_db`.
- `--collection-name`: existing ChromaDB collection. Defaults to
  `dreams_nomic_embed_text`.
- `--embed-model`: Ollama model used by the selected collection. Defaults to
  `nomic-embed-text`.
- `--chat-model`: tool-capable Ollama model. Defaults to `qwen3:8b`.
- `--dreams-path`: parsed journal JSONL used for exact and analytical tools.
  Defaults to `data/dreams.jsonl`.
- `--structured-dreams-path`: structured feature JSONL used by
  `get_character_mentions`. Defaults to
  `outputs/structured_dreams/dream_features.jsonl`.
- `--characters-path`: optional manually curated character dictionary used by
  `get_character_context`. Defaults to `data/characters.json`; when the file is
  absent, only that tool is disabled.
- `--num-ctx`: Ollama context window option. Defaults to `8192` so ten
  average-length dreams fit comfortably.
- `--num-predict`: maximum generated tokens per model response. Defaults to
  `700`.
- `--temperature`: sampling temperature. Defaults to `0.1`.

Date wording such as "last month" is resolved relative to the current date and
combined with semantic search terms. Character-mention questions require the
structured file; relationship questions use the character dictionary. Debug
traces can contain private journal text, so protect reports created with
`--debug`.

Requires an existing matching ChromaDB index, a tool-capable chat model, and
Ollama running locally.

## `dream-analyzer analyze`

Loads one dream by ID or accepts dream text directly, then asks an Ollama chat model for a close analysis of its events, dynamics, themes, and possible interpretations.
The analysis is printed and saved under `outputs/analysis/`. Saved files include
the complete target dream, complete retrieved related dreams, and generated
analysis. ID-based filenames use `<dream_id>_<datetime>.txt`; direct-text
filenames use `<datetime>.txt`.

```bash
dream-analyzer analyze dream-2022-1-22-0
dream-analyzer analyze --text "I opened a door and found another kitchen."
dream-analyzer analyze dream-2022-1-22-0 --chat-model qwen3:8b
dream-analyzer analyze dream-2022-1-22-0 --related-dreams 5 --similarity-threshold 0.55
dream-analyzer analyze dream-2022-10-10-0 --related-dreams 5 --start-date 2022-04-10 --end-date 2022-10-10
```

Arguments:

- `dream-id`: positional dream ID to load from JSONL. The legacy `--dream-id`
  option remains available temporarily. Mutually exclusive with `--text`.
- `--text`: dream text to analyze directly. Mutually exclusive with either
  dream-ID form.
- `--dreams-path`: path to parsed dream JSONL records. Defaults to `data/dreams.jsonl`.
- `--chat-model`: Ollama chat model. Defaults to `qwen3:8b`.
- `--related-dreams`: maximum number of similar indexed dreams to use as context. Defaults to `0` (disabled).
- `--similarity-threshold`: minimum cosine similarity for related dreams. Defaults to `0.5`.
- `--start-date`: earliest reference dream date to include, in `YYYY-MM-DD` format.
- `--end-date`: latest reference dream date to include, in `YYYY-MM-DD` format.
- `--chroma-path`: path to the persistent ChromaDB database. Defaults to `data/chroma_db`.
- `--collection-name`: ChromaDB collection name. Defaults to
  `dreams_nomic_embed_text`.
- `--embed-model`: Ollama embedding model. Defaults to `nomic-embed-text`.
- `--max-chars-per-related-dream`: maximum context characters per related dream. Defaults to `1500`.
- `--output-dir`: directory where analysis files are saved. Defaults to `outputs/analysis`.
- `--num-ctx`: Ollama context window option. Defaults to `8192`.
- `--num-predict`: maximum generated tokens. Defaults to `2500`.
- `--temperature`: sampling temperature. Defaults to `0.2`.

Related-dream context requires an existing ChromaDB index. Ollama must be running locally.

## `src/cli/compare_models.py`

Runs the same task across these four combinations:

- `qwen3:8b` with `nomic-embed-text`
- `gemma3:12b` with `nomic-embed-text`
- `qwen3:8b` with `qwen3-embedding`
- `gemma3:12b` with `qwen3-embedding`

It expects collections named `dreams_nomic_embed_text` and
`dreams_qwen3_embedding`. Retrieval is performed once per embedding model and
the exact retrieved context is reused for both chat models. Results are saved
as JSON and Markdown under `outputs/model_comparisons/`. Analyze-mode reports
include the complete target dream, and both modes include complete retrieved
dream texts.

Compare RAG answers. A fixed retrieval query is required so chat models do not
generate different search queries:

```bash
python3 src/cli/compare_models.py rag \
  "What patterns appear in dreams about hidden rooms?" \
  --retrieval-query "hidden room hallway extra room concealed door behind wall"
```

RAG arguments:

- `question`: required question answered by every model combination.
- `--retrieval-query`: required fixed text embedded by both embedding models.
  Keeping this fixed ensures the chat models receive comparable retrievals.
- `--chroma-path`: directory containing both expected ChromaDB collections.
  Defaults to `data/chroma_db`.
- `--output-dir`: directory for JSON and Markdown comparison reports. Defaults
  to `outputs/model_comparisons`.
- `--top-k`: number of dreams retrieved from each embedding index. Defaults to
  `8`.
- `--max-chars-per-dream`: maximum context characters included per retrieved
  dream. Defaults to `2500`.
- `--num-ctx`: Ollama context window option. Defaults to `4096`.
- `--num-predict`: maximum generated tokens per answer. Defaults to `700`.
- `--temperature`: sampling temperature used by every chat model. Defaults to
  `0.0`.

Compare analysis of one dream with five related dreams:

```bash
python3 src/cli/compare_models.py analyze \
  --dream-id dream-2022-1-22-0 \
  --related-dreams 5
```

Analyze arguments:

- `--dream-id`: load the target dream from the parsed journal by exact ID.
  Mutually exclusive with and required instead of `--text`.
- `--text`: analyze supplied dream text directly. Mutually exclusive with and
  required instead of `--dream-id`.
- `--dreams-path`: parsed dream JSONL used by `--dream-id`. Defaults to
  `data/dreams.jsonl`.
- `--chroma-path`: directory containing both expected ChromaDB collections.
  Defaults to `data/chroma_db`.
- `--output-dir`: directory for JSON and Markdown comparison reports. Defaults
  to `outputs/model_comparisons`.
- `--related-dreams`: maximum related dreams retrieved from each embedding
  index. Defaults to `5`.
- `--similarity-threshold`: minimum cosine similarity for a related dream.
  Defaults to `0.5`.
- `--start-date`: earliest related-dream date to include, in `YYYY-MM-DD`
  format. By default there is no lower date bound.
- `--end-date`: latest related-dream date to include, in `YYYY-MM-DD` format.
  By default there is no upper date bound.
- `--max-chars-per-related-dream`: maximum context characters included per
  related dream. Defaults to `1500`.
- `--num-ctx`: Ollama context window option. Defaults to `8192`.
- `--num-predict`: maximum generated tokens per analysis. Defaults to `2500`.
- `--temperature`: sampling temperature used by every chat model. Defaults to
  `0.0`.

## `src/cli/evaluate_retrieval.py`

Runs a labeled query suite in `agent`, `embedding`, `bm25`, or `hybrid` mode and
writes JSON and Markdown reports with precision, recall, R-precision, timing,
errors, and category averages.

Like the other commands, evaluation defaults to the user's ignored `data/`
files: `dreams.jsonl`, `characters.json`, `retrieval_eval_queries.json`, and
`chroma_db`. A user who supplies those files can run the same commands without
path arguments:

```bash
python3 src/cli/evaluate_retrieval.py
python3 src/cli/evaluate_retrieval.py --retrieval-mode embedding
python3 src/cli/evaluate_retrieval.py \
  --collection-name dreams_qwen3_embedding \
  --embed-model qwen3-embedding
```

To run the repository's tracked synthetic benchmark without touching personal
data, build a separate index and pass the reference paths explicitly:

```bash
dream-analyzer index \
  --dreams-path examples/dreams.jsonl \
  --chroma-path data/benchmark/chroma_db

python3 src/cli/evaluate_retrieval.py \
  --queries-path examples/retrieval_eval_queries.json \
  --dreams-path examples/dreams.jsonl \
  --structured-dreams-path data/benchmark/structured_dreams.jsonl \
  --characters-path examples/characters.json \
  --chroma-path data/benchmark/chroma_db

python3 src/cli/evaluate_retrieval.py \
  --retrieval-mode bm25 \
  --queries-path examples/retrieval_eval_queries.json \
  --dreams-path examples/dreams.jsonl
```

Agent retrieval is the default. `embedding` searches Chroma directly, `bm25`
searches only the JSONL supplied by `--dreams-path`, and `hybrid` combines the
direct embedding and BM25 rankings.

Arguments:

- `--queries-path`: labeled retrieval-query JSON file. Defaults to
  `data/retrieval_eval_queries.json`.
- `--retrieval-mode`: retrieval implementation to benchmark: `agent`,
  `embedding`, `bm25`, or `hybrid`. Defaults to `agent`.
- `--dreams-path`: parsed dream JSONL used by the agent, BM25, hybrid,
  validation, and corpus fingerprinting. In `bm25` mode, this file is the
  complete searchable corpus. Defaults to `data/dreams.jsonl`.
- `--structured-dreams-path`: structured feature JSONL used by the agent's
  character-mention tool. Defaults to
  `outputs/structured_dreams/dream_features.jsonl`.
- `--characters-path`: optional manually curated character dictionary used by
  the agent. Defaults to `data/characters.json`.
- `--chroma-path`: persistent ChromaDB directory used by modes with semantic
  retrieval. Defaults to `data/chroma_db`.
- `--collection-name`: ChromaDB collection to query. Defaults to
  `dreams_nomic_embed_text`.
- `--embed-model`: Ollama model associated with that collection. Defaults to
  `nomic-embed-text`.
- `--chat-model`: tool-capable Ollama model used in `agent` mode. Defaults to
  `qwen3:8b`.
- `--top-k`: maximum results returned by each agent search call. Defaults to
  `10`; `agent` mode requires a value from `10` through `20` so metrics at 10
  remain defined.
- `--max-tool-calls`: maximum calls available to the planner for each query.
  Defaults to `3`.
- `--max-chars-per-dream`: maximum characters per dream exposed to the planner.
  Defaults to `2500`.
- `--num-ctx`: Ollama planner context window option. Defaults to `8192`.
- `--num-predict`: maximum generated planner tokens. Defaults to `700`.
- `--temperature`: planner sampling temperature. Defaults to `0.1`.
- `--output-dir`: directory for benchmark reports and leaderboard artifacts.
  Defaults to `outputs/retrieval_evaluations`.
- `--leaderboard-name`: filename stem for the leaderboard artifacts. For
  example, `--leaderboard-name personal_results` writes
  `personal_results.json` and `personal_results.md`. Defaults to `leaderboard`.
- `--experiment-name`: optional short label shown in the leaderboard.
- `--experiment-note`: optional note describing the experiment change.
- `--rebuild-leaderboard`: rebuild leaderboard JSON and Markdown from existing
  benchmark reports without running a new evaluation.
- `--regenerate-markdown`: regenerate every `benchmark_*.md` file from its
  corresponding JSON artifact, then rebuild the leaderboard without running a
  new evaluation.
- `--recalculate-metrics`: replace relevance labels in reports whose complete
  query set matches `--queries-path`, recalculate metrics from their stored
  ranked dream IDs, and rebuild their Markdown and the leaderboard without
  rerunning retrieval.

Every completed run updates the JSON and Markdown leaderboards in
`outputs/retrieval_evaluations/`. Use `--rebuild-leaderboard` to regenerate them
from existing benchmark reports.

To regenerate all benchmark Markdown reports after changing their renderer:

```bash
dream-analyzer evaluate-retrieval --regenerate-markdown
```

After correcting relevant dream IDs in an evaluation query file, recalculate
all matching reports from their stored rankings:

```bash
dream-analyzer evaluate-retrieval \
  --recalculate-metrics \
  --queries-path data/retrieval_eval_queries.json
```

Reports for other query sets are skipped. Matching JSON reports are updated in
place along with their Markdown files and the leaderboard. If a correction
increases the relevance count beyond a stored baseline's ranking depth, the
command stops and identifies the report that must be rerun.

## `src/cli/evaluate_retrieval_llm.py`

Embeds one retrieval prompt with both `nomic-embed-text` and
`qwen3-embedding`, retrieves the top-k dreams from their matching collections,
and asks `gemma3:12b` to score every result from 1 (irrelevant) to 5 (directly
relevant). The judge sees the prompt and dream content but not the embedding
model name. JSON and Markdown reports are saved under
`outputs/retrieval_evaluations/`.

```bash
python3 src/cli/evaluate_retrieval_llm.py \
  "hidden room hallway extra room concealed door behind wall" \
  --top-k 8
```

Compare the current Chroma-distance and explicit-cosine retrieval paths for
both embedding models:

```bash
python3 src/cli/evaluate_retrieval_llm.py \
  "hidden room hallway extra room concealed door behind wall" \
  --retrieval-metric both \
  --top-k 8
```

In `both` mode, the report compares Chroma and cosine results for each embedding
model, including overlap and mean judged relevance.

Use the complete text of an existing dream as the retrieval and relevance
target. The target dream itself is excluded from the results:

```bash
python3 src/cli/evaluate_retrieval_llm.py \
  --dream-id dream-2022-1-22-0 \
  --retrieval-metric both \
  --top-k 8
```

For a long or multi-scene dream, specify which part should control the LLM's
relevance judgment:

```bash
python3 src/cli/evaluate_retrieval_llm.py \
  --dream-id dream-2022-1-22-0 \
  --focus "discovering a hidden room that reveals a disturbing family secret" \
  --top-k 8
```

Alternatively, use an exact passage from the dream or generate an evaluation
focus:

```bash
python3 src/cli/evaluate_retrieval_llm.py \
  --dream-id dream-2022-1-22-0 \
  --focus-passage "I opened the concealed door behind the wall"

python3 src/cli/evaluate_retrieval_llm.py \
  --dream-id dream-2022-1-22-0 \
  --generate-focus
```

In dream-ID mode, retrieval always uses the complete target dream. Focus options
change only the relevance criterion used by the judge.

Arguments:

- `retrieval_prompt`: retrieval text and judging target. Required unless
  `--dream-id` is supplied and mutually exclusive with it.
- `--dream-id`: use the complete text of an existing dream as the retrieval
  input and judging target. Mutually exclusive with `retrieval_prompt`.
- `--dreams-path`: parsed dream JSONL used by `--dream-id`. Defaults to
  `data/dreams.jsonl`.
- `--focus`: manual description of the important event, conflict, or motif for
  judging. Available only with `--dream-id` and mutually exclusive with the
  other focus options.
- `--focus-passage`: exact passage from the target dream to use as the judging
  focus. Available only with `--dream-id` and mutually exclusive with the other
  focus options.
- `--generate-focus`: ask the judge model to derive a distinctive focus from
  the target dream. Available only with `--dream-id` and mutually exclusive
  with the other focus options.
- `--top-k`: results retrieved for each embedding-model and metric combination.
  Defaults to `8`.
- `--retrieval-metric`: `chroma`, `cosine`, or `both`. Defaults to `chroma`.
- `--chroma-path`: directory containing the `dreams_nomic_embed_text` and
  `dreams_qwen3_embedding` collections. Defaults to `data/chroma_db`.
- `--judge-model`: Ollama model used to generate a focus when requested and to
  score candidates. Defaults to `gemma3:12b`.
- `--max-chars-per-dream`: maximum candidate-dream characters sent to the
  judge. Defaults to `2500`.
- `--max-target-chars`: maximum target-dream characters sent to the judge.
  Defaults to `6000`.
- `--judge-batch-size`: maximum unique candidates judged in one call. Defaults
  to `12`.
- `--num-ctx`: Ollama context window option for judging. Defaults to `16384`.
- `--output-dir`: directory for JSON and Markdown reports. Defaults to
  `outputs/retrieval_evaluations`.

## `src/cli/structure_dreams.py`

Uses structured Ollama output to extract grounded, descriptive fields from
every dream and saves one JSON object per line to
`outputs/structured_dreams/dream_features.jsonl`:

```bash
python3 src/cli/structure_dreams.py
```

Process or regenerate one dream:

```bash
python3 src/cli/structure_dreams.py --dream-id dream-2022-1-22-0
python3 src/cli/structure_dreams.py --dream-id dream-2022-1-22-0 --overwrite
python3 src/cli/structure_dreams.py --scope new
```

Arguments:

- `--dream-id`: process only the dream with this exact ID. Only one ID is
  accepted per invocation; omit it to process every dream in scope.
- `--dreams-path`: parsed dream JSONL input. Defaults to `data/dreams.jsonl`.
- `--output`: structured JSONL destination and resume source. Defaults to
  `outputs/structured_dreams/dream_features.jsonl`.
- `--model`: Ollama model used for structured extraction. Defaults to
  `gemma3:12b`.
- `--num-ctx`: Ollama context window option. Defaults to `8192`.
- `--overwrite`: reprocess selected records even when the output already
  contains their current schema version.
- `--scope`: `pending` processes all selected records that are missing or use
  an older schema; `new` additionally limits that set to IDs recorded by a
  journal import. Defaults to `pending`.
- `--import-state`: journal import-state JSON used by `--scope new`. Defaults to
  `data/dream_imports.json`.
- `--import-id`: import entry used by `--scope new`. Defaults to `latest`.

`--scope new` reads `data/dream_imports.json` and processes only IDs introduced
by the latest append-oriented journal import. Select another import entry with
`--import-id`, or another state file with `--import-state`.

Existing dream IDs with current feature-group versions are skipped unless
`--overwrite` is supplied. When a schema change affects only one feature group,
only that group is sent to the model and its result is merged into the existing
record. Source-text changes, model changes, and `--overwrite` regenerate every
group. Records from schema version 13 are migrated to group-version metadata
without unnecessary model calls when their source and model are unchanged.
Successful records are saved after each update so a long run can be resumed.

Each record stores `feature_group_versions` and per-group model/timestamp data in
`feature_provenance`. Increment the corresponding entry in
`FEATURE_GROUP_VERSIONS` when extraction semantics change. Fields in the same
group, including `lucidity` and `lucidity_level`, are always regenerated
together. Increment `EXTRACTION_VERSION` for a global prompt or extraction-policy
change that should regenerate all groups. `SCHEMA_VERSION` now versions the
record envelope and does not by itself trigger model calls.

Retrieval quality is model-rated through four independent integer components
from `0` to `4`: specificity, coherence, distinctiveness, and evidence density.
The record retains these values in `retrieval_quality_components`. The
application computes the stored `retrieval_quality` deterministically as their
equally weighted sum divided by `16`, producing values from `0.0` to `1.0` in
increments of `0.0625`. It is stored for future reranking but is not currently
used by retrieval.

## `src/cli/build_character_lookup.py`

Aggregates `named_characters` from structured dream records and creates a
fillable lookup without making any additional LLM calls:

```bash
python3 src/cli/build_character_lookup.py
```

Add date-bounded relationship templates when a relationship may change over
time:

```bash
python3 src/cli/build_character_lookup.py --temporal-context
```

Arguments:

- `--input`: structured dream-feature JSONL. Defaults to
  `outputs/structured_dreams/dream_features.jsonl`.
- `--output`: destination character dictionary. Defaults to
  `data/characters.json`.
- `--temporal-context`: create date-bounded `relationship_history` templates
  instead of one `relationship` and `context` pair per character.
- `--overwrite`: replace an existing lookup, including any manual edits. By
  default the command refuses to overwrite an existing output file.

Each entry includes the detected name, aliases, mention count, first and last
mention dates, and contributing dream IDs. With temporal context, fill in or
duplicate entries under
`relationship_history`, using inclusive `start_date` and `end_date` values in
`YYYY-MM-DD` format. Null boundaries mean open-ended. Without temporal context,
fill in the single `relationship` and `context` fields.
