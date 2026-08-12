# set up `psycopg[c]` driver

## for `alpine linux`

- **Django Driver Choice:** Use **`psycopg3`** (packaged as `psycopg`) for [Django](https://www.djangoproject.com/) 4.2+; `psycopg2` is legacy and eventual deprecation target.
- **Benefits of psycopg3:** Native async support, up to 2x higher throughput, native connection pooling (`psycopg_pool`), and pipeline mode for concurrent queries.
- **`psycopg[binary]` vs `psycopg[c]`:**
  - `psycopg[binary]`: Bundles pre-compiled `libpq`; no compiler needed; great for quick dev/Docker containers, but isolated from OS security updates.
  - `psycopg[c]`: Compiles against system `libpq`; requires a C compiler and links dynamically to OS-level OpenSSL/security patches.
- **Alpine Docker Build Requirements:**
  - **Builder Stage:** Needs a C compiler and development headers (`gcc`, `musl-dev`, `postgresql-dev`) to compile the C-extensions during `uv sync`.
  - **Runtime/Dev Stage:** Needs the clean runtime library (`postgresql-libs` for `libpq`) so the dynamic linker can run the compiled package without build bloat.

### `Dockerfile` updates

```dockerfile

# --- Stage 1: Build & Dependency Installation
FROM python:3.14-alpine3.23 AS builder

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

################################################################
################################################################
# Install build dependencies required to compile psycopg[c] from source
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev
################################################################
################################################################

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
    openssh-client \

################################################################
################################################################
# Install runtime dependencies for psycopg[c] (libpq) and dev tools
RUN apk add --no-cache \
    postgresql-libs \
    postgresql-client
# `postgresql-client` is just to access the postgresql service.
################################################################
################################################################

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

```

## Note

When you install `psycopg[c]` in the builder stage, it compiles only the **Python wrapper code** into a binary extension file (called a wheel or `.so` file). It **does not compile or bundle `libpq` itself**.

Instead, the compilation process checks the host system for `libpq` and creates a **dynamic pointer** inside the Python extension that says: _"When running, look for `libpq.so` inside the standard system library directories."_

Because of how Linux shared libraries work, copying `libpq` manually from stage to stage is not recommended for two major reasons:

### 1. `libpq` has its own complex web of system dependencies

The `libpq` library isn't a single isolated file; it depends on other operating system libraries to function, such as:

- **`libcrypto.so`** (for encryption)
- **`libssl.so`** (for secure OpenSSL connections)
- **`libgssapi_krb5.so`** (for Kerberos authentication, if compiled in)

If you only copy the raw `libpq.so` file from the builder stage, Python will crash on startup because libpq won't be able to find its own dependencies (like SSL) in the clean runtime image.

### 2. Linux Package Managers Handle Security Patches

By running `apk add postgresql-libs` in the final stage, Alpine's package manager handles installing libpq along with all its required security dependencies automatically. It places them exactly where the operating system's dynamic linker (`ld`) expects them to be, ensuring your database connections remain stable and secure.

### Summary

- The Builder Stage needs postgresql-dev to get the blueprints (header files) to compile the Python-to-C bridge.
- The Final Stage needs postgresql-libs to provide the actual runtime library (libpq) and its underlying security modules.
