# template_search_project/tests — Agent guide

## Purpose

Offline, no-mocks coverage of `src/`: config, pipeline (local backend + temp dirs), synthesis, report, figures, manuscript variables, and script smoke paths. Infrastructure HTTP behaviour is covered in `tests/infra_tests/`; this suite focuses on project orchestration.

## Running

Use the tests and coverage command in the [offline quick start](../docs/quickstart.md) from the registered project's root.

## Conventions

- Use `tmp_path`, real JSON/corpus snippets, and deterministic LLM callables.
- Subprocess tests invoke project-local `scripts/*.py` with explicit `--project-root` when isolating outputs.

## See also

- [`../AGENTS.md`](../AGENTS.md)
- [`README.md`](../docs/reference/tests.md)
