# Run the bundled offline fixture

The bundled configuration uses the local corpus. Live backends,
network enrichment, and LLM synthesis require explicit configuration.
The [configuration reference](configuration.md) lists the defaults.

## Set up the pinned template and project

From a clean checkout of this project:

```sh
search_source="$PWD"
git clone https://github.com/docxology/template.git ../search-renderer
cd ../search-renderer
git checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
uv sync --locked --no-dev
mkdir -p projects/working
search_project="$PWD/projects/working/template_search_project"
git -C "$search_source" worktree add --detach "$search_project" HEAD
cd "$search_project"
uv sync --locked --python 3.14 --extra dev --extra rendering --extra llm
```

The working project lives inside the pinned checkout because the runner
executes its manuscript hydration script in a confined project directory.

## Analyze the local corpus and prepare the manuscript

From the detached project directory:

```sh
mv output ../template_search_project_snapshot
mkdir -p output
cp -a ../template_search_project_snapshot/deep_search output/
MPLBACKEND=Agg uv run --no-sync python scripts/run_search_pipeline.py --no-llm
MPLBACKEND=Agg uv run --no-sync python scripts/y_generate_search_figures.py
uv run --no-sync python scripts/z_generate_manuscript_variables.py
```

These commands regenerate the single-query results, bibliography, and
plots. The committed deep-search material supplies the evidence behind
the supplemental review. The deep-search pipeline is disabled by default.
The original checkout retains its tracked publication snapshot.

To verify the native code from the detached project directory:

```sh
MPLBACKEND=Agg uv run --no-sync pytest tests --cov=src --cov-fail-under=90 -q
```

The [rendering guide](rendering_pipeline.md) explains how to turn the
resolved manuscript and figures into PDF, HTML, and slide decks.
