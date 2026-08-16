# usnderstanding files and dirs created by `uv run django-admin startproject <project_name> .`

When you run `uv run django-admin startproject <project_name> .`, Django generates a clean, standardized blueprint. Using the trailing dot (.) ensures your management file stays in the main folder rather than nesting inside a duplicate directory.

Here is exactly how that structure looks and what every single file does

---

## The Directory Tree

```text

my_django_project/
│
├── .venv/                 # Isolated Python environment created by uv
├── pyproject.toml         # Project metadata and dependencies managed by uv
├── uv.lock                # Strict dependency lockfile
│
├── manage.py              # The main command-line utility for your project
│
└── myapp/                # The project configuration folder (the "management app")
    ├── __init__.py        # Tells Python this folder is a package
    ├── settings.py        # Central dashboard for all project configurations
    ├── urls.py            # Global routing map for your website URLs
    ├── asgi.py            # Entry-point for asynchronous web servers
    └── wsgi.py            # Entry-point for traditional synchronous web servers

```

---

## Root-Level Files

### `manage.py`

This is your primary control switch. You will never edit this file directly, but you will invoke it constantly via `uv run python manage.py <command>`. It acts as a wrapper around Django's core code, allowing you to run the development server, migrate databases, and create sub-apps.

### `pyproject.toml & uv.lock`

These are not native Django files; they belong to `uv`. `pyproject.toml` tracks high-level settings and lists your core requirements (like Django itself), while `uv.lock` freezes the absolute version of every sub-dependency to prevent project breakage over time.

---

## Inside the `<project_name>` directory (`<project_name>/`)

This directory is named after whatever you typed in your setup command. It contains the operational gears of your website.

### `__init__.py`

An empty file whose sole purpose is to declare this directory as a Python package. It lets Python modules import configurations from this directory smoothly.

### `settings.py`

The most critical configuration file. It controls the entire application ecosystem, containing:

- **`SECRET_KEY`:** A cryptographic key used to secure passwords, cookies, and tokens.
- **`DEBUG = True`:** A toggle that shows descriptive error screens during development (must be `False` in production).
- **`ALLOWED_HOSTS`:** A security list specifying which domain names or IP addresses can serve this website.
- **`INSTALLED_APPS`:** A registry where you must declare your project's custom feature modules / apps so Django recognizes them.
- **`DATABASES`:** Connection settings pointing to SQLite (default), PostgreSQL, MySQL, or other databases.

### `urls.py`

The "traffic controller" or router of your website. It links URL paths (like `://example.com`) to the specific Python code blocks (called Views) meant to process and display that page.

### `wsgi.py` (Web Server Gateway Interface)

The standard setup used to deploy your finished website to traditional web servers like Gunicorn or Apache. It handles synchronous request-response lifecycles.

### `asgi.py` (Asynchronous Server Gateway Interface)

The modern counterpart to WSGI. It provides an entry point for advanced asynchronous servers (like Daphne or Uvicorn) to handle real-time elements like WebSockets, chat systems, and long-lived connection tasks.
