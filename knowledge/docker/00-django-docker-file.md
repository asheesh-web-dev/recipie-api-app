# `Dockerfile` for django

we can write `Dockerfile` in different ways

## first-approach

```dockerfile
# --- Stage 1: Build & Dependecy installation ---
FROM python:3.14-alpine3.23 AS builder

LABEL maintainer="asheesh"

# Install uv from the official Astral image repository
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set critical environment variables for uv and Python buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
# PYTHONDONTWRITEBYTECODE=1
# What it does: Prevents Python from writing .pyc files (compiled bytecode) to disk.
# Why it matters in Docker: It keeps your container image smaller and cleaner. In a container, source code rarely changes during runtime, so caching bytecode on disk provides no benefit and just wastes storage space.
#
# PYTHONUNBUFFERED=1
# What it does: Forces Python to send stdout and stderr streams straight to the terminal without buffering them in memory.
# Why it matters in Docker: It ensures your application logs (like Django crash traces or incoming request logs) appear in real-time when you run docker logs. Without this, logs might get stuck in a memory buffer, leaving you in the dark if the app hangs.
#
# UV_COMPILE_BYTECODE=1
# What it does: Tells Astral's uv package manager to pre-compile all installed Python packages into .pyc bytecode during the build phase.
# Why it matters in Docker: It speeds up your container startup time. While PYTHONDONTWRITEBYTECODE stops your application code from generating bytecode at runtime, UV_COMPILE_BYTECODE compiles the heavy third-party dependencies ahead of time during the Docker build. This means packages like Django load instantly when the container starts.
#
# UV_LINK_MODE=copy
# What it does: Forces uv to physically copy files from its global cache into your project's virtual environment, instead of creating hardlinks or symlinks.
# Why it matters in Docker: It is required for multi-stage Docker builds. By default, uv uses hardlinks to save disk space on your local machine. However, hardlinks cannot cross the boundary between Docker build stages. Using copy ensures that when Stage 2 copies /app/.venv from Stage 1, all the actual dependency files are physically present and intact.

WORKDIR /app

# Install dependencies using cache mounts for instant rebuilds
# This runs 'uv sync' BEFORE copying code, optimizing the Docker layer cache
RUN --mount=type=cache,target=/root/.cache/uv \
--mount=type=bind,source=uv.lock,target=uv.lock \
--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
uv sync --frozen --no-install-project
#--frozen
# What it does: Forces uv to read the uv.lock file exactly as it is, without updating it, checking for newer versions online, or modifying it.
# The Docker benefit: It guarantees a completely predictable and reproducible build. If a dependency releases a broken update today, your Docker build won't break because --frozen locks you strictly to the exact versions you tested locally.
#
# --no-install-project
# What it does: Tells uv to install all the third-party dependencies (like Django, Celery, etc.), but do not install your actual local application code as an editable package.
# The Docker benefit: This is the secret to fast Docker rebuilds. In your Dockerfile, you run this command before running COPY . /app/. Because your source code isn't copied yet, Docker caches this layer. When you edit your application code later, Docker skips this heavy installation step entirely, rebuilding your container in less than a second.

# --- Stage 2: Development Runtime --
FROM python:3.14-alpine3.23 AS development

WORKDIR /app

RUN adduser --disabled-password --no-create-home django-user
# --disabled-password
# What it does: Disables password login for this account.
# Why it matters in Docker: It prevents anyone from trying to log into this user via SSH or a login prompt. The user account exists purely to own and run the background Python process, not for a human to log in with a password.
#
# --no-create-home
# What it does: Prevents the system from creating a /home/django-user directory.
# Why it matters in Docker: It keeps the container filesystem lightweight and clean. Since your application lives and runs entirely inside the /app directory, a separate home directory is completely unnecessary waste.

# Copy virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY . /app/

# Change ownership of the app dir to the non-root user
RUN chown -R django-user:django-user /app
# -R
# What it does: Short for Recursive.
# Why it matters in Docker: It applies the ownership change to the /app folder and every single file, subfolder, and virtual environment file hidden inside it. Without -R, only the top-level folder changes ownership, leaving the files inside locked.

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
# PATH="/app/.venv/bin:$PATH"
# What it does: Puts the virtual environment's executable folder at the very beginning of the search list.
# Why it matters: Linux searches the PATH from left to right. By placing /app/.venv/bin first, you guarantee that whenever the container runs python, pip, gunicorn, or django-admin, it uses the exact versions inside your virtual environment, completely ignoring the global system Python.

USER django-user

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

```

## second-approach

```dockerfile

# --- Stage 1: Build & Dependency Installation
FROM python:3.14-alpine3.23 AS builder

# Install uv from the official image
COPY -from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set env varialbes to prevent uv from creating virtual env
ENV PYTHONUSERBASE=/deps \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1
# PYTHONUSERBASE
# What it is:a built-in Python environment variable. It lets you change the destination path for packages installed via the Python User Install feature (typically triggered by using pip install --user or uv sync --user).
# By default, when you don't use a virtual environment and run a user installation, Python puts packages into a hidden folder in the user's home directory (e.g., ~/.local/).
# Setting PYTHONUSERBASE=/deps overrides that default behavior. It forces Python to treat the /deps folder as its home for user-installed packages instead.
# Why it is used in this Dockerfile
# Using PYTHONUSERBASE=/deps solves three major problems in multi-stage Docker builds when you don't want a virtual environment:
# 1. It groups everything into one predictable folderInstead of packages spreading out across various system folders (like /usr/local/lib/... or /usr/local/bin/...), Python is forced to create a clean, predictable structure inside a single folder:
# Libraries: /deps/lib/python3.14/site-packages/
# Binaries: /deps/bin/

# Copy config files first to leverage docker caching
COPY pyproject.toml uv.lock ./

# Install dependecies without installing the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --system


# --- Stage 2: runner stage
FROM python:3.14-alpine3.23 AS runner

WORKDIR /app

# Set Python & uv env variables
ENV PYTHONUSERBASE=/deps \
    PATH="/deps/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
# Because PYTHONUSERBASE=/deps is set, the Python interpreter automatically looks inside /deps/lib/python3.14/site-packages whenever your code runs an import statement. Adding /deps/bin to the system PATH ensures you can run CLI tools installed by your dependencies (like black, pytest, or gunicorn) directly from the terminal.

# Copy only the dedicated dependency directory
COPY --from=builder /deps /deps

# Copy rest of app code
COPY . .

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]

```

## third-approach

```dockerfile

# --- Stage 1: Build & Dependency Installation
FROM python:3.14-alpine3.23 AS builder

# Install uv from the official image
COPY -from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy config files first to leverage docker caching
COPY pyproject.toml uv.lock ./

# Install dependecies without installing the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


# --- Stage 2: Development stage
FROM python:3.14-alpine3.23 AS development

# Install uv from the official image
COPY -from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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
