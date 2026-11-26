# Configuration defaults

Every knob lives in [`docs/manuscript/config.yaml`](manuscript/config.yaml). The
defaults shown below are the values that ship with the bundled config —
they are **CI-safe / offline by default** so a fresh clone can render the
manuscript with no network and no Ollama server. Switching to live search
or enabling the LLM stage is a one-line edit (see [`docs/quickstart.md`](quickstart.md)).

The committed `data/corpus.json` is a deterministic workflow fixture. Reports
generated from the default local source carry an explicit fixture-scope notice;
their paper counts and summaries are not empirical literature findings. Use a
live provider source and retain its provenance before making substantive claims.

### `project_config.search:` (single-query pipeline)

| Key | Default | Meaning |
|---|---|---|
| `query` | `"reproducible research optimization"` | Free-text topic passed to every backend. |
| `max_results` | `100` | Per-backend cap; aggregator dedupes and re-applies year filters. |
| `year_min` / `year_max` | `null` | Optional inclusive year filter. |
| `sources` | `[local]` | Subset of `arxiv`, `crossref`, `local`, `paperclip`. |
| `local_corpus` | `data/corpus.json` | Path (relative to project root) consumed when `sources` includes `local`. |
| `crossref_mailto` | `you@example.org` | Polite-pool identifier sent to Crossref. |
| `paperclip` | `false` | Reserved flag for future per-source toggles. |
| `cache_dir` | `output/search/cache` | Deterministic JSON cache directory. |
| `cache_ttl_seconds` | `null` | Disable cache TTL (entries never expire). |

### `project_config.enrichment:`

| Key | Default | Meaning |
|---|---|---|
| `fetch_abstracts` | `false` | Network-backed abstract retrieval is opt-in; local fixture metadata remains offline. |
| `fetch_fulltext` | `false` | Use `FulltextFetcher` (needs the optional `pypdf` dependency). |
| `abstract_cache_dir` | `output/cache/abs` | Per-paper `<safe_id>.txt` cache. |
| `fulltext_cache_dir` | `output/cache/pdf` | Per-paper `<safe_id>.{pdf,txt}` cache. |
| `max_fulltext_chars` | `400000` | Hard cap on the fulltext block fed to the LLM (≈ 100 k tokens for `gemma3:4b`). |

### `llm:` (Ollama-local synthesis; opt-in)

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `false` | Skip the LLM stage entirely when `false` (CI-safe default). |
| `model` | `gemma3:4b` | Ollama model name. |
| `temperature` | `0.0` | Pinned for reproducibility. |
| `seed` | `42` | Pinned for reproducibility. |
| `per_paper` | `true` | Run `synthesise_per_paper` on every result. |
| `corpus_synthesis` | `true` | Run `synthesise_corpus` over the deduplicated set. |
| `output_dir` | `output/llm` | Where `synthesis.md` and `per_paper/<safe_id>.md` are written. |
| `context_window` | `131072` | Ollama context window passed to `LLMClient`. |
| `long_max_tokens` | `16384` | `query_long` token cap so multi-section reading notes are not truncated. |
| `max_input_length` | `600000` | Per-call input character cap. |
| `review_timeout` | `600.0` | Per-call timeout (seconds). |

### `report:`

| Key | Default | Meaning |
|---|---|---|
| `output_path` | `output/reading_report.md` | Final assembled markdown report. |
| `include_per_paper` | `true` | Include per-paper LLM notes in the final report. |
| `include_corpus_synthesis` | `true` | Include the corpus-level synthesis section. |

### `project_config.deep_search:` (multi-keyword fan-out; opt-in)

| Key | Default | Meaning |
|---|---|---|
| `enabled` | `false` | Skip the live/deep-search stage unless explicitly enabled. |
| `keywords` | `[convex optimization, stochastic gradient descent, reproducible research]` | One `SearchQuery` per keyword. |
| `max_results_per_keyword` | `100` | Per-keyword cap honoured by the aggregator. |
| `sources` | `[]` | No backend is selected by default. Add a provenance-backed source explicitly; `paperclip` also requires `PAPERCLIP_API_KEY`. |
| `year_min` / `year_max` | `null` | Optional inclusive year filter. |
| `crossref_mailto` | `you@example.org` | Polite-pool identifier. |
| `fetch_abstracts` | `false` | Network-backed abstract enrichment is opt-in. |
| `fetch_fulltext` | `false` | Network-backed PDF enrichment is opt-in. |
| `max_fulltext_chars` | `400000` | Hard cap fed to the per-paper LLM block. |
| `llm_per_paper` | `false` | Generate seven-section reading notes only when local LLM use is explicitly enabled. |
| `llm_model` | `gemma3:4b` | Ollama model. |
| `llm_seed` / `llm_temperature` | `42` / `0.0` | Pinned for reproducibility. |
| `llm_context_window` / `llm_long_max_tokens` / `llm_max_input_length` / `llm_review_timeout` | `null` | Per-stage Ollama overrides; `null` inherits from the `llm:` block. |
| `output_dir` | `output/deep_search` | Where per-keyword and aggregate outputs land. |
| `abstract_cache_dir` / `fulltext_cache_dir` / `search_cache_dir` | `output/cache/abs`, `output/cache/pdf`, `output/search/cache` | Shared with the standard pipeline so a single corpus is never refetched. |
| `write_unified_bibtex` | `true` | Emit the deduplicated unified bibliography. |
| `unified_bibtex_path` | `docs/manuscript/references_deep.bib` | Where that bibliography is written. |

### `project_config` direct keys

| Key | Default | Meaning |
|---|---|---|
| `references_path` | `docs/manuscript/references.bib` | Where `run_search_pipeline.py` writes its (auto-populated) BibTeX. |
