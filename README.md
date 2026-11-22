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

## Controller releases

The `openlp_ctrl` package version in `packages/openlp_ctrl/pyproject.toml` is the source of truth for semantic image tags. Follow SemVer: bump the patch version for fixes, minor for features, and major for breaking changes.

Controller images are tagged with:

- `sha-<full commit SHA>` for immutable deployments;
- `vX.Y.Z` for the exact package version;
- `latest` for the current default-branch release.

Main pushes publish and deploy. Pull requests and manual runs build and test without publishing or deploying. A weekly schedule checks on the last Saturday of each month and, if no deployment has occurred recently, rebuilds and deploys the current `main` commit for a monthly refresh.
