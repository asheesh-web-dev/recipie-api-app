# --- Stage 1: Build & Dependency Installation
FROM python:3.14-alpine3.23 AS builder

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1 

# Install build dependencies required to compile psycopg[c] from source
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev

# Copy config files first to leverage docker caching
COPY pyproject.toml uv.lock ./

# Install dependecies without installing the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project 


# --- Stage 2: Development stage
FROM python:3.14-alpine3.23 AS development

# install development tools
RUN apk add --no-cache \
    git \
    openssh-client

# Install runtime dependencies for psycopg[c] (libpq) and dev tools
# `postgresql-client` is just to access the postgresql service.
RUN apk add --no-cache \
    postgresql-libs \
    postgresql-client

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Set Python & uv env variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy the entire virtual env from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy rest of app code
COPY . .

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]