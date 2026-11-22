# Multi-stage wheel-only build: Poetry builds the package in a temporary builder,
# then the slim runtime installs the wheel and contains neither Poetry nor source code.
# Use Python 3.11 slim image as base
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir "poetry>=2.0,<3.0"

WORKDIR /build
COPY pyproject.toml README.md ./
COPY openlp_ctrl ./openlp_ctrl

RUN poetry build --format wheel

# Runtime stage: install the wheel directly, with no Poetry or source tree
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=builder /build/dist /tmp/dist

RUN pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist \
    && useradd --create-home --uid 10001 --shell /bin/bash app

USER app
WORKDIR /app

EXPOSE 8000

CMD ["openlp_ctrl", "--host", "0.0.0.0", "--port", "8000"]
