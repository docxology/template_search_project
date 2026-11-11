# template_search_project TODO

This backlog is future-only. Completed validation and dated review evidence are preserved in
[`docs/maintenance/exemplar-backlog-history.md`](../../../docs/maintenance/exemplar-backlog-history.md)
or in source-owned generated receipts. Each active row must retain a stable ID, size, dependency,
next action, proving artifact, acceptance command, and negative control; absence of an owner or external receipt
keeps a capability blocked rather than silently promoting it.

## Backlog operating rules

- Keep deterministic and offline defaults unchanged unless an upcoming row explicitly scopes an opt-in.
- Do not close a row until its producer, artifact, consumer, gate, and failing negative control are present.
- Treat unavailable network, LLM, container, formal-tool, and publication paths as explicit skips
  or blockers.
- Re-derive counts and receipts from live source data; never copy measurements into this planning file.

## Integrity and template-status gaps

- The bundled `data/corpus.json` is marked as a deterministic fixture in
  README, AGENTS, manuscript prose, and generated reports; fixture-backed
  synthesis is rejected when it uses high-confidence empirical assertion
  language. Keep this boundary intact when adding claim templates.
- Keep manuscript numbers (`RESULT_NUM_PAPERS`, `RESULT_WITH_ABSTRACT`,
  `RESULT_WITH_DOI`, etc.) sourced only from `output/run_summary.json` and
  `output/data/manuscript_variables.json`, never hand-typed.
- `output/deep_search/run_summary.json`, `aggregate_report.md`,
  `composition_summary.json`, and the self-contained dashboard now use
  `<repo-root>`-relative paths. Puppeteer metadata still records its cache
  executable as `<home>/.cache/puppeteer/...`; this is renderer-owned metadata
  and requires a shared infrastructure normalization rather than a project
  output edit.

## Configurable-surface gaps

- Retargeting the query, sources, and deep-search keywords should remain
  entirely `manuscript/config.yaml`-owned; avoid hard-coding search terms in
  `src/`.
- Keep the Ollama budget knobs (`context_window`, `long_max_tokens`,
  `max_input_length`, `review_timeout`) explicit in config rather than
  falling back silently to client defaults.

## Documentation and signposting gaps

- Keep README, AGENTS.md, and `docs/_generated/exemplar_roster.md`
  synchronized through the generator.
- Keep `docs/quickstart.md` and `docs/troubleshooting.md` aligned with the
  qualified project name `templates/template_search_project`.

## Test and validator gaps

- Keep `src/review_report.py` above the project coverage floor with no-mock
  tests for subprocess environment policy, syntax-error handling, import
  boundaries, and explicit skipped/disabled/not-materialised statuses.
- Retrieval-coverage claims remain bounded by the bundled offline corpus; any
  widening requires a scoped row, source-bound corpus, and negative control.
- Keep fixture-honesty validation and the explicit `evidence_scope` field in
  `output/run_summary.json`; extend assertion vocabulary only with a focused
  negative-control test.
- Keep the byte-identical-across-reruns test
  (`tests/test_pipeline.py::TestRunLiteraturePipeline::test_bibtex_byte_identical_across_reruns`)
  in sync as new pipeline stages are added.
- Keep `manuscript/references_deep.bib` derived from the committed deep-search
  aggregate and fail when citation keys or source revisions drift.

## Minor upcoming

| ID | Status | Size | Dependency | Next action / unblock condition | Proving artifact | Acceptance command | Negative control |
| --- | --- | --- | --- | --- | --- | --- | --- |
No active rows are currently scoped at this size.

## Medium upcoming

| ID | Status | Size | Dependency | Next action / unblock condition | Proving artifact | Acceptance command | Negative control |
| --- | --- | --- | --- | --- | --- | --- | --- |
No active rows are currently scoped at this size.

## Major upcoming

| ID | Status | Size | Dependency | Next action / unblock condition | Proving artifact | Acceptance command | Negative control |
| --- | --- | --- | --- | --- | --- | --- | --- |
No active rows are currently scoped at this size.

## Backlog status

Rows remain active until the acceptance command and negative control pass in the same source revision.
A blocked row is a deliberate boundary, not a skipped success.

## Workflowz review — 2026-11-10

- [ ] **WF-20261110-001** · P1 · Standalone-clone `_repo_root` resolution in entry-point scripts

  **Evidence:** `scripts/run_search_pipeline.py:28-33` and `scripts/run_deep_search.py:28-33` both compute `_repo_root = _project_root.parents[2]`, which assumes the project lives at `projects/templates/<name>/` inside a monorepo. In a standalone clone (where `_project_root` *is* the repository root, per `README.md:83-87` and `pyproject.toml:12-15`), `parents[2]` resolves to an unrelated directory (potentially `/`), inserting a wrong path into `sys.path` and breaking `infrastructure.*` imports.

  **Observable outcome:** Running `python scripts/run_search_pipeline.py --no-llm` from a standalone clone with `infrastructure/` as a sibling directory completes the pipeline (or fails with a clear "infrastructure not found" message), rather than producing an opaque ImportError caused by `sys.path` containing `/` or another unrelated directory.

  **Acceptance probe (from repo root):** Create a temporary standalone layout by copying the project to a flat directory with a sibling `infrastructure/` directory, then run:
  ```bash
  cp -r . /tmp/standalone_test/template_search_project
  cp -r ../infrastructure /tmp/standalone_test/infrastructure  # if available
  cd /tmp/standalone_test/template_search_project
  python scripts/run_search_pipeline.py --no-llm 2>&1 | head -20
  ```
  The command should not produce `ModuleNotFoundError: No module named 'infrastructure'` caused by incorrect `sys.path` entries. If `infrastructure/` is missing, the error message should clearly indicate where it was looked for.

  **Dependencies/constraints:** Must preserve monorepo behavior (the common case per `pyproject.toml:5-10`). Fix should detect whether `infrastructure/` exists at the computed `_repo_root` and, if not, check the project root's parent (sibling layout) or skip insertion. Do not change the public CLI interface or add new required arguments.

  **Negative control:** Verify that in monorepo layout (`projects/templates/template_search_project/`), the existing `_repo_root` computation still works — run `python scripts/run_search_pipeline.py --help` from the monorepo project root and confirm exit code 0.
