# OpenLP helpers

This is a monorepo containing multiple OpenLP-related projects:

## Projects

* `projects/openlp_doc/`: Transform OpenLP song and service data into web content and PDFs.
* `projects/openlp_ctrl/`: Client and server to remote control slides

## Development

Each project manages its own dependencies using Poetry. To work on a specific project:

1. Navigate to the project directory
2. Run `poetry install` to install dependencies
3. Use `poetry run <project>` to execute project commands
