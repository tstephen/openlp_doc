# Copilot Instructions for openlp_doc Repository

## Project Structure
This is a **Python monorepo** managed with **Poetry 2.x** containing multiple packages:
- `packages/openlp_ctrl/` - Control interface for OpenLP
- `packages/openlp_doc/` - Documentation tools for OpenLP
- `packages/openlp_slides/` - Slides plugin for OpenLP

## Build System Requirements

### DO NOT use pip directly
- ❌ `pip install -e .`
- ❌ `pip install pytest`
- ❌ `python -m pip install`

### DO use Poetry
- ✅ `poetry install` - Install all dependencies including dev dependencies
- ✅ `poetry install --no-dev` - Install only production dependencies
- ✅ `poetry add <package>` - Add new dependency
- ✅ `poetry run pytest` - Run tests
- ✅ `poetry build` - Build package
- ✅ `poetry shell` - Activate virtual environment

### Python Version
- Minimum Python: 3.11 (see `requires-python` in package pyproject.toml)
- Root project supports: Python ^3.8

### Running Commands
Always prefix commands with `poetry run` when executing tools:
- `poetry run pytest` instead of `pytest`
- `poetry run black .` instead of `black .`
- `poetry run mypy` instead of `mypy`

### GitHub Actions / CI/CD
When creating workflows:
1. Use `actions/setup-python@v5` with Python 3.11+
2. Install Poetry: `pip install poetry>=2.0`
3. Configure Poetry cache with `actions/setup-python` using `cache: 'poetry'`
4. Install dependencies: `poetry install`
5. Run tests: `poetry run pytest`
6. Build packages: `poetry build`

### Docker
For Dockerfile:
- Install Poetry in the container
- Use `poetry install --no-dev` for production
- Or use `poetry build` + `pip install dist/*.whl` for smaller images

## Testing
- Test framework: pytest
- Test location: `tests/` directory in each package
- Run tests: `poetry run pytest` (from package directory)
- Coverage: `poetry run pytest --cov=<package_name>`

## Code Quality Tools
- Formatter: black
- Linter: flake8
- Type checker: mypy
- Pre-commit hooks configured

## Monorepo Navigation
- Each package in `packages/` has its own `pyproject.toml`
- Root `pyproject.toml` defines workspace dependencies
- Always specify working directory when running commands in specific packages
