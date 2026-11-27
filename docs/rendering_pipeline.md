# Rendering Pipeline: Configuration → Search → Manuscript → PDF

The `docs/manuscript/` directory contains the narrative components of the search project. The full pipeline takes a `docs/manuscript/config.yaml` and `data/corpus.json` (or live API responses) and produces a publication-ready combined PDF. This document describes every phase, what it produces, which scripts run it, and how to troubleshoot failures.

## Run the pinned renderer

Complete the [offline quickstart](quickstart.md) first. Install Pandoc
3.14, the matching [pandoc-crossref filter](https://github.com/lierdakil/pandoc-crossref/releases/tag/v0.3.26b),
XeLaTeX with the packages in the
[template run guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md),
and Mermaid CLI 12.2.0 with a Chrome headless shell for the inline diagrams.
Put the renderer binaries on `PATH`. If Chrome is installed outside its
usual location, set `PUPPETEER_EXECUTABLE_PATH` to its executable.

Run from the pinned template checkout:

```sh
env -u NODE_PATH -u NODE_OPTIONS uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/template_search_project
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/template_search_project
```

The combined PDF, HTML index, slides, and reports appear in the working
project's `output/pdf/`, `output/web/`, `output/slides/`, and
`output/reports/`. The renderer uses the hydrated copy in
`output/manuscript/`. Maintain the source under
[docs/manuscript/](manuscript/README.md).

## The Five-Phase Flow

The commands below use two roots from the quickstart. Run project scripts from the detached `search_project` checkout and shared pipeline stages from the pinned Template checkout. The full pipeline orders project scripts by filename. The offline fixture reuses the committed deep-search material.

### Phase 1 — Search and Enrichment

**Scripts**:
- `scripts/run_deep_search.py` (alphabetically first when enabled)
- `scripts/run_search_pipeline.py`

**Commands**:
```bash
MPLBACKEND=Agg uv run --no-sync python scripts/run_search_pipeline.py --no-llm
```

For a separately configured deep-search run, run `uv run --no-sync python scripts/run_deep_search.py` first from the project root. The bundled offline configuration keeps that phase disabled.

**Inputs**: `docs/manuscript/config.yaml` (`project_config.search`, `project_config.enrichment`, root `llm`, and `project_config.deep_search`) plus `data/corpus.json` when `project_config.search.sources` includes `local`.

**`run_deep_search.py` outputs**:

| File | Location | Producer |
|---|---|---|
| `aggregate.json` | `output/deep_search/` | `src/deep_search.py::run_deep_search` |
| `aggregate_report.md` | `output/deep_search/` | same |
| `run_summary.json` | `output/deep_search/` | same |
| `<keyword_slug>/papers.json` | `output/deep_search/` | same |
| `<keyword_slug>/reading_report.md` | `output/deep_search/` | same |
| `<keyword_slug>/per_paper/<safe_id>.md` | `output/deep_search/` | LLM stage when enabled |
| `references_deep.bib` | `docs/manuscript/` | `src/deep_search.py` |

**`run_search_pipeline.py` outputs**:

| File | Location | Producer |
|---|---|---|
| `results.json` | `output/search/` | `src/pipeline.py::run_literature_pipeline` |
| `cache/search_<hash>.json` | `output/search/` | `infrastructure.search.literature.SearchCache` |
| `corpus.json` | `output/` | `infrastructure.search.literature.write_corpus` |
| `enrichment_log.json` | `output/` | `src/pipeline.py` |
| `reading_report.md` | `output/` | `src/report.py::write_reading_report` |
| `run_summary.json` | `output/` | `src/pipeline.py` |
| `references.bib` | `docs/manuscript/` | `src/pipeline.py` (via `infrastructure.reference.citation.paper_to_bibentry`) |
| `llm/synthesis.md`, `llm/per_paper/<safe_id>.md` | `output/` | `src/synthesis.py` (when `config.llm.enabled`) |

### Phase 2 — Compose the Literature Review

**Script**: `scripts/s_compose_literature_review.py`

**Command**:
```bash
uv run --no-sync python scripts/s_compose_literature_review.py
```

**Inputs**: `output/deep_search/aggregate.json` + per-keyword `papers.json` + per-paper notes.

**Output**: `docs/manuscript/S01_literature_review.md` — a multi-section narrative grouped by deep-search keyword, with citations into `references_deep.bib`. The composer also writes `output/deep_search/composition_summary.json` for downstream tooling.

The composer runs **between** the search runners (`run_*`) and the variable resolver (`z_*`) so the freshly composed S01 reaches the manuscript-mirroring stage. This ordering is enforced by `tests/test_script_order.py`.

### Phase 3 — Figures and Manuscript Variables

**Scripts**:
- `scripts/y_generate_search_figures.py`
- `scripts/z_generate_manuscript_variables.py`

**Commands**:
```bash
uv run --no-sync python scripts/y_generate_search_figures.py
uv run --no-sync python scripts/z_generate_manuscript_variables.py
```

**Inputs**: `output/search/results.json` (figures) + `docs/manuscript/config.yaml` + `output/deep_search/aggregate.json` when present (variables).

**`y_generate_search_figures.py` outputs**:

| File | Generator (in `src/figures.py`) |
|---|---|
| `output/figures/papers_per_source.png` | `plot_papers_per_source` |
| `output/figures/year_histogram.png` | `plot_year_histogram` |
| `output/figures/score_distribution.png` | `plot_score_distribution` |

**`z_generate_manuscript_variables.py` outputs**:

| File | Content |
|---|---|
| `output/data/manuscript_variables.json` | `{ field: value }` mapping from `ManuscriptVariables` |
| `output/manuscript/*.md` | Resolved copies of `docs/manuscript/*.md` (every `{{TOKEN}}` substituted) |
| `output/manuscript/config.yaml` | Copy of `docs/manuscript/config.yaml` |
| `output/manuscript/*.bib` | Copies of every `docs/manuscript/*.bib` (sorted) |

**Critical**: every `{{TOKEN}}` defined in the field set of `src/manuscript_variables.py::ManuscriptVariables` must resolve before Phase 4. If a token is unresolved, the literal `{{TOKEN_NAME}}` will appear in the rendered PDF. The `variables_resolved` review stage detects this; the `<deep-search not run>` sentinel is the exception (it is intentionally written when no aggregate exists).

### Phase 4 — Render the Combined PDF

**Script**: `scripts/pipeline/stage_03_render.py` at the **repository root** (not inside `projects/`).

**Command**:
```bash
env -u NODE_PATH -u NODE_OPTIONS uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/template_search_project
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/template_search_project
```

**Inputs**: `output/manuscript/*.md` (resolved) + `docs/manuscript/config.yaml` + `docs/manuscript/preamble.md` + every `docs/manuscript/*.bib`.

**Infrastructure modules involved**:

| Module | Role |
|---|---|
| `infrastructure/rendering/pdf_renderer.py` | Orchestrates Pandoc → XeLaTeX |
| `infrastructure/rendering/pipeline.py` | Resolves the manuscript root (prefers `output/manuscript/`) |
| `infrastructure/rendering/manuscript_discovery.py` | Orders `*.md` files lexically (`S01_*` lands after `99_*`) |
| `infrastructure/core/config/loader.py` | Reads `config.yaml` for title, authors, metadata |

`PDFRenderer.render_combined` invokes Pandoc with `--natbib`, emits one LaTeX document, and runs BibTeX over `\bibliography{stem1,stem2,...}` built from every `docs/manuscript/*.bib` (sorted). Citations resolve uniformly across `references.bib` ∪ `references_deep.bib`.

**Outputs**:
- `output/pdf/template_search_project_combined.pdf` — final publication PDF
- `output/pdf/` — LaTeX intermediates (`.tex`, `.aux`, `.log`)
- `output/slides/` — per-section Beamer PDFs
- `output/web/` — HTML versions

### Refresh the current HTML reader

Use the offline quickstart and the pinned render and validation above. The
standard query supplies `references.bib`. The retained supplemental review
comes from `S01_literature_review.md` and `references_deep.bib`, so the combined
reader needs both files in the hydrated manuscript directory even with live
deep search disabled. The HTML writer passes the two files to Pandoc
citeproc. The PDF writer passes the same pair to BibTeX.

To refresh the current reader, run the following from the source checkout.
Set `search_project` to the detached checkout where output validation passed.

```sh
cp "$search_project/output/web/index.html" "$search_project/output/web/favicon.ico" docs/reader/web/
cp "$search_project/output/web/assets/source-web-fonts.js" docs/reader/web/assets/
for image in papers_per_source year_histogram score_distribution; do
  cp "$search_project/output/figures/$image.png" docs/reader/figures/
done
uv run --no-sync pytest tests/test_current_reader.py -q
```

The test verifies that each cited bibliography entry really exists and has
rendered text. It also checks that the supplement's authored citation keys
reach the current reader. The original `output/` snapshot stays in place.

### Phase 5 — Promote, Review, and Report

**Optional artifact copy**, from the disposable Template checkout:

```bash
uv run --no-sync python scripts/pipeline/stage_05_copy.py --project working/template_search_project
```

**Review aggregation**, from the detached project root after the local review stages have produced their reports:

```bash
uv run --no-sync python scripts/zz_generate_review_report.py
```

**Outputs**:
- `output/working/template_search_project/template_search_project_combined.pdf` under the Template checkout — the promoted artifact (used by CI artifact upload and the multi-project executive report).
- `output/review/stage_*.json`, `output/review/summary.json` — per-stage review outputs from `scripts/review`.
- `output/review/REVIEW_REPORT.md` — human-readable aggregation written by `zz_generate_review_report.py`.

The review CLI (`scripts/review`) reads `review_config.yaml` to enable / disable stages. Available stages:

| Stage | Backend |
|---|---|
| `prerender_validation` | `infrastructure.validation.cli prerender` |
| `markdown_links` | `infrastructure.validation.cli links` |
| `bibtex_validation` | `infrastructure.reference.citation.cli validate` |
| `bibliography_completeness` | `src/analysis.py::validate_bibliography_completeness` |
| `variables_resolved` | `src/analysis.py::validate_variables_resolved` |
| `output_integrity` | `infrastructure.validation.cli integrity` |
| `test_suite_health` | pytest + coverage subprocess |
| `infrastructure_usage` | `src/analysis.py::audit_infrastructure_imports` (subprocess) |
| `determinism_check` | `src/analysis.py::check_determinism_artifacts` — inspects cache/run_summary/seed/temperature (no re-run) |

## `config.yaml` Controls

| YAML Key | Controls | Consumed by |
|---|---|---|
| `paper.title` | PDF title page and headers | `infrastructure/core/config/loader.py` → `pdf_renderer.py` |
| `paper.version` | Title page metadata | same |
| `authors[*]` | Author list | same |
| `project_config.search.query` | Single-query search string; bound to `{{CONFIG_QUERY}}` | `src/pipeline.py`, `src/manuscript_variables.py` |
| `project_config.search.sources` | Backends invoked (`arxiv`, `crossref`, `paperclip`, `local`); bound to `{{CONFIG_SOURCES}}` | same |
| `project_config.search.year_min` / `year_max` | Defensive year filtering at search and aggregation | `src/pipeline.py` |
| `project_config.search.max_results` | Cap on returned papers | `src/pipeline.py` |
| `project_config.search.local_corpus` | Path to JSON corpus when `sources` includes `local` | `src/pipeline.py` |
| `project_config.search.cache_dir`, `cache_ttl_seconds` | `SearchCache` location and TTL | `infrastructure.search.literature.SearchCache` |
| `project_config.enrichment.fetch_abstracts`, `fetch_fulltext` | Per-paper enrichment toggles | `src/pipeline.py` |
| `project_config.enrichment.abstract_cache_dir`, `fulltext_cache_dir`, `max_fulltext_chars` | Cache locations and truncation | `AbstractFetcher`, `FulltextFetcher` |
| `llm.enabled` | Whether `synthesise_per_paper` and `synthesise_corpus` run | `scripts/run_search_pipeline.py` |
| `llm.model`, `seed`, `temperature` | LLM determinism knobs | `src/llm_runtime.py::build_llm_callable` |
| `llm.context_window`, `long_max_tokens`, `max_input_length`, `review_timeout` | Ollama runtime budgets | same |
| `report.output_path`, `include_per_paper`, `include_corpus_synthesis` | Reading-report assembly | `src/report.py::write_reading_report` |
| `project_config.deep_search.enabled` | Whether `run_deep_search.py` performs work (exits 2 when disabled) | `scripts/run_deep_search.py` |
| `project_config.deep_search.keywords`, `max_results_per_keyword`, `sources` | Fan-out parameters | `src/deep_search.py` |
| `project_config.deep_search.write_unified_bibtex`, `unified_bibtex_path` | `references_deep.bib` controls | same |
| `project_config.references_path` | Override the standard BibTeX output path | `src/pipeline.py` |

## Troubleshooting

### Unresolved `{{TOKEN}}` appears in PDF

**Symptom**: literal `{{TOKEN_NAME}}` in the PDF.

**Cause**: Phase 3 did not run, the token is not declared in `src/manuscript_variables.py::ManuscriptVariables`, or `output/manuscript/` is stale.

**Fix**:
```bash
ls output/data/manuscript_variables.json
uv run --no-sync python scripts/z_generate_manuscript_variables.py
grep -rn "{{[A-Z_]*}}" output/manuscript/
```

### Undefined citation key, but the key is in `references_deep.bib`

**Symptom**: `BIBTEX.UNDEFINED_KEY` errors during `prerender_validation`, even though `references_deep.bib` contains the key.

**Cause**: `s_compose_literature_review.py` ran *after* `z_generate_manuscript_variables.py`, so `output/manuscript/references_deep.bib` is stale.

**Fix**: From the detached project root, re-run the composer in Phase 2 **before** the resolver in Phase 3. The pre-render gate unions every `docs/manuscript/*.bib`; a missing or stale second file means deep-only keys fail.

### LLM stage produced no output

**Symptom**: `output/llm/` is missing or empty, even though `config.llm.enabled: true`.

**Cause / fix**: `infrastructure.llm` could not be imported, or Ollama is unreachable. Both `run_search_pipeline.py` and `run_deep_search.py` log a warning and skip the synthesis stage entirely — they do **not** write a fake placeholder. Verify with `ollama list`, `ollama pull gemma3:4b`, and `uv sync --group llm`. See [`troubleshooting.md`](troubleshooting.md#llm-stage-produced-no-output).

### `SearchCache` returns stale results

**Symptom**: a config change to `project_config.search.year_min` / `year_max` / `query` has no effect.

**Cause**: cache is keyed on canonical query identity; two callers with the same key share the cache.

**Fix**: pass `--no-cache` to the script, or delete `output/search/cache/`, or set `project_config.search.cache_ttl_seconds` to expire entries.

### Missing figure in PDF

**Symptom**: broken image or missing figure reference.

**Cause / fix**: Phase 3 did not run, or `output/search/results.json` is absent (`y_generate_search_figures.py` exits 2 when there is no input). Run `run_search_pipeline.py` first.

```bash
ls output/figures/*.png
```
