# Devlog 0001: FluxLine Project Bootstrap

---

## Objective

First I established a reproducible Python project foundation for FluxLine before implementing any domain specific data engineering functionality.

The initial goals were to:

* initialise the project using `uv`
* use Python 3.12
* adopt a `src/` package layout
* make `fluxline` importable as an installed Python package
* confirm that the application can be packaged successfully
* initialise Git development practices

## Initial Structure

The application source code is stored beneath:

```text
src/
└── fluxline/
    └── __init__.py
```

This separates application code from project level resources such as tests, documentation, infrastructure and build configuration so everything is distinctly organised and neat.

## Packaging Issue

After the initial project bootstrap, the following package import failed:

```bash
uv run python -c "import fluxline"
```

The repository contained a `src/fluxline` directory, but the project did not have an explicitly configured Python build system.

A source directory alone does not cause a Python project to be installed into its environment.

## Resolution

Setuptools was configured as the project build backend:

```toml
[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"
```

Package discovery was configured to search beneath the `src` directory:

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

This allows setuptools to discover the `fluxline` package and install it into the project's Python environment.

Yes, I could have used hatchling but setuptools is fine for now.

## Validation

The package installation was verified using:

```bash
uv sync
uv run python -c "import fluxline; print(fluxline.__file__)"
```

The project's ability to produce distributable Python artefacts was then tested using:

```bash
uv build
```

This successfully generated:

```text
dist/fluxline-0.1.0.tar.gz
dist/fluxline-0.1.0-py3-none-any.whl
```

## What These Artefacts Represent

The `.tar.gz` file is a source distribution containing the source required to build the package.

The `.whl` file is a Python wheel, a built distribution that can be installed into compatible Python environments.

These artefacts are generated outputs and are therefore excluded from Git.

## Key Lesson

A Python source directory and an installed Python package are different concepts.

The build system defines how application source code becomes an installable package.

For FluxLine:

```text
src/fluxline
      ->
setuptools
      ->
Python package
      ->
installed environment / wheel
```

For CICD and Databricks later, this is pretty important so I am making this distinction very clear early on.

## Current State

The Python packaging foundation is operationally sound.

FluxLine can:

* create a reproducible environment using `uv`
* install its own application package
* be imported from that environment
* build both source and wheel distributions

No application dependencies or domain functionality have yet been introduced which is intended, this is just the very start of development.

## Next Step

Define the FluxLine project charter, the specific business problem, system boundaries and initial engineering requirements before implementing any data sources.
