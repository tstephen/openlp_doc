# OpenLP Doc

Transform OpenLP song and service data into web content and PDFs.

## Installation

```bash
poetry install
```

## Usage

Transform a service file into HTML and PDF:

```bash
poetry run openlp_doc service_file.osz
```

Generate slides view:

```bash
poetry run openlp_doc --slides service_file.osz
```

### Options

- `--verbose, -v`: Increase output verbosity
- `--slides`: Output as slides instead of standard format

## Example

```bash
poetry run openlp_doc tests/resources/Service\ 2024-01-20\ 23-43.osz
```

This will generate:
- `Service 2024-01-20 23-43.html` - HTML version
- `Service 2024-01-20 23-43.pdf` - PDF version (unless `--slides` is used)

## Templates

The package uses Jinja2 templates located in `openlp_doc/templates/`:
- `service.html` - Main service template
- `serviceitem.html` - Individual song/item template
- `slides.html` - Slides presentation template
