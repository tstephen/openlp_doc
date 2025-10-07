# OpenLP helpers

This is a monorepo containing multiple OpenLP-related packages:

## Packages

* `packages/openlp_doc/`: Transform OpenLP song and service data into web content and PDFs.
* `packages/openlp_ctrl/`: Client and server to remote control slides

## Development

Each package manages its own dependencies using Poetry. To work on a specific package:

1. Navigate to the package directory
2. Run `poetry install` to install dependencies
3. Use `poetry run <package>` to execute package commands
