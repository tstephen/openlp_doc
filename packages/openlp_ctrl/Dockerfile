# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=2.0.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN pip install --no-cache-dir "poetry>=${POETRY_VERSION}"

# Copy all package files
COPY pyproject.toml README.md ./
COPY openlp_ctrl/ ./openlp_ctrl/

# Install the package and its dependencies (excluding dev dependencies)
RUN poetry install --only main

# Expose the default port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "openlp_ctrl", "--host", "0.0.0.0", "--port", "8000"]
