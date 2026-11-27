# template_search_project/docs — Agent guide

## Purpose

Project-local agent-facing documentation. This is the operational rulebook for AI agents and contributors working inside the literature-discovery exemplar. Repo-wide literature references live under [`docs/modules/`](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/modules) and [`docs/guides/`](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/guides); manuscript-syntax canon lives at [`docs/guides/manuscript-semantics.md`](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/guides/manuscript-semantics.md).

## File Inventory

| File | Purpose |
|---|---|
| [`README.md`](README.md) | Quick navigation by audience |
| [`AGENTS.md`](AGENTS.md) | This index |
| [`agent_instructions.md`](agent_instructions.md) | Behavioural constraints for AI agents (read-first priority) — 7 rules + verification checklist |
| [`architecture.md`](architecture.md) | Two-layer compliance, module-responsibilities table, idempotency contract |
| [`testing_philosophy.md`](testing_philosophy.md) | Zero-mock + LLM-as-callable; live counts in [`docs/_generated/COUNTS.md`](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/_generated/COUNTS.md) |
| [`rendering_pipeline.md`](rendering_pipeline.md) | Five-phase flow (search → compose → figures+vars → PDF → review); `config.yaml` controls; troubleshooting |
| [`style_guide.md`](style_guide.md) | 7 rules: zero-mock, infrastructure delegation, thin orchestrator, show-not-tell, explicit paths, dataclass standards, error messages |
| [`syntax_guide.md`](syntax_guide.md) | Pandoc-crossref labels, `{{TOKEN}}` registry from `src/manuscript_variables.py`, two-bibliography citation rule |
| [`faq.md`](faq.md) | Architecture, testing, search, LLM, manuscript, common-pitfall answers |
| [`quickstart.md`](quickstart.md) | Six-step first-run walkthrough |
| [`output_conventions.md`](output_conventions.md) | Producer / consumer mapping for every artifact |
| [`troubleshooting.md`](troubleshooting.md) | Symptom-driven diagnostic recipes (with mermaid flowchart) |

## Reading Order

This sequence is intentional. Each document provides context the next assumes:

1. [`agent_instructions.md`](agent_instructions.md) — start here; 7 hard rules and the verification checklist.
2. [`architecture.md`](architecture.md) — layer boundaries before touching any file.
3. [`testing_philosophy.md`](testing_philosophy.md) — zero-mock policy and the LLM-as-callable corollary before writing or modifying any test.
4. [`rendering_pipeline.md`](rendering_pipeline.md) — the five-phase flow before editing manuscript or output paths.
5. [`style_guide.md`](style_guide.md) — coding style before editing `src/`, `tests/`, or `scripts/`.
6. [`syntax_guide.md`](syntax_guide.md) — `{{TOKEN}}` registry and figure-label registry before editing any manuscript `.md` file.
7. [`faq.md`](faq.md) — design rationale and pitfall answers when in doubt.

## Key Conventions

**Read-first protocol.** Skipping `agent_instructions.md` is the most common source of errors: agents who skip it tend to introduce mocks (violating Rule 1 of `style_guide.md`), import `infrastructure.rendering` or `infrastructure.scientific` from `src/` (violating Rule 3 of `agent_instructions.md`), or hardcode numbers in manuscript prose (violating Rule 4 of `style_guide.md`).

**Architecture isolation.** `src/pipeline.py` and `src/deep_search.py` are the only modules that touch `infrastructure.search.*`. `src/synthesis.py` takes a duck-typed `llm: Callable[[str], str]` argument so tests pass deterministic local functions and runtime callers pass the adapter from `src/llm_runtime.py`. Every other `src/` module is pure.

**Zero-mock enforcement.** No `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec` anywhere in `tests/`. The LLM is tested by passing a Python function — never a mock — to `synthesise_per_paper` / `synthesise_corpus`.

**Show-not-tell.** Manuscript prose must reference concrete file paths and APIs. A reader of `02_methodology.md` should be able to open `src/pipeline.py` and find the named function within seconds.

**Two bibliographies.** `docs/manuscript/references.bib` (single-query) and `docs/manuscript/references_deep.bib` (deep-search) coexist; Pandoc `--natbib` merges every `docs/manuscript/*.bib` at render time.

**Alphabetical script order.** `run_*` < `s_*` < `y_*` < `z_*` < `zz_*` is enforced by `tests/test_script_order.py`. The composer must run before the resolver.

## Verification Commands

Follow the [offline quick start](quickstart.md) from the registered checkout for the native coverage gate. Check that tests avoid mocks and that `src/` avoids shared rendering, reporting, and scientific imports. Use `uv run --no-sync python scripts/review --list` to inspect the review stages from that checkout.

## Contracts

- Prefer linking to [`manuscript/config.yaml`](manuscript/config.yaml) as the single configuration reference.
- Project-local commands run from the registered checkout. The quick start identifies commands that run from the separate Template checkout.
- Cross-references inside this directory use relative links.

## Cross-References

- [`README.md`](README.md) — audience-targeted entry points.
- [`../AGENTS.md`](../AGENTS.md) — project-level overview.
- [`../pyproject.toml`](../pyproject.toml) — coverage-gate settings (`fail_under = 90`, `branch = true`).
- [`../tests/conftest.py`](../tests/conftest.py) — `sys.path` setup and `MPLBACKEND=Agg`.
- [`manuscript/AGENTS.md`](manuscript/AGENTS.md) — manuscript-directory protocol.
- [`manuscript/SYNTAX.md`](manuscript/SYNTAX.md) — project-local Pandoc syntax overlay.
- [`../src/AGENTS.md`](../src/AGENTS.md) — `src/` module-level guide.
- [Template agent guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/AGENTS.md) — root template documentation.
