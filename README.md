# OpenLP helpers

This is a monorepo containing multiple OpenLP-related Poetry packages:

## Packages

* `packages/openlp_doc/`: Transform OpenLP song and service data into web content and PDFs.
* `packages/openlp_ctrl/`: Client and server to remotely control slides.
* `packages/openlp_slides/`: Reserved for the OpenLP export plugin; add it under this directory when available.

## Development

The repository has a root Poetry environment with editable path dependencies for the packages.

```bash
poetry install --with dev
poetry run pytest packages/openlp_ctrl/tests packages/openlp_doc/tests
poetry build
```

To build or test an individual package, run its commands from that package directory:

```bash
cd packages/openlp_ctrl
poetry install --with dev
poetry run test
poetry build
```

The GitHub Actions workflow tests and builds every package that contains a `pyproject.toml`.
