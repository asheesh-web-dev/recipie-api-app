# custom management commands

Yes. In Django, **custom management commands** are basically your own commands that you can run through `manage.py`.

For example, Django already provides commands like:

```bash
python manage.py runserver
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
```

You can create your own:

```bash
python manage.py wait_for_db
python manage.py seed_data
python manage.py cleanup_users
```

## What are custom commands?

A custom management command is a Python class that Django exposes through:

```bash
python manage.py <command_name>
```

They are useful when you have some **reusable backend task** that you want to execute manually, automatically, or from Docker/CI/CD.

Common examples:

* Wait for a database to become available
* Create initial/seed data
* Import data from a CSV
* Export data
* Send emails
* Delete old records
* Recalculate statistics
* Run scheduled maintenance
* Create test/demo users
* Perform one-time migrations or data transformations

---

## How do you create one?

Suppose you have a Django app called `users`.

The structure is:

```text
users/
├── __init__.py
├── models.py
├── views.py
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── create_demo_users.py
```

The important structure is:

```text
<django_app>/
└── management/
    └── commands/
        └── <command_name>.py
```

The app containing the command must be in `INSTALLED_APPS`.

### 1. Create the command file

For:

```text
create_demo_users.py
```

Django will make the command available as:

```bash
python manage.py create_demo_users
```

### 2. Create the `Command` class

```python
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create demo users."""

    def handle(self, *args: object, **options: object) -> None:
        """Create demo users."""
        self.stdout.write("Creating demo users...")

        # Your logic here.

        self.stdout.write(
            self.style.SUCCESS("Demo users created!")
        )
```

The important part is the class name:

```python
class Command(BaseCommand):
```

Django looks for this class inside the command module.

And `handle()` is where your command's logic goes.

---

## Running the command

You run:

```bash
python manage.py create_demo_users
```

Django discovers:

```text
users/management/commands/create_demo_users.py
```

and effectively calls:

```python
Command().handle(...)
```

You don't need to manually register the command.

---

## Example: `wait_for_db` command

Check if db is available before running the server.

the structure 

```text
core/
└── management/
    └── commands/
        └── wait_for_db.py
```

And:

```python
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg import OperationalError as PsycopgError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: object, **options: object) -> None:
        """Wait for the database to become available."""
        self.stdout.write("Waiting for database...")

        while True:
            try:
                self.check(databases=["default"])
                break
            except (PsycopgError, OperationalError):
                self.stdout.write(
                    "Database unavailable, waiting 1 second..."
                )
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS("Database available!")
        )
```

Then:

```bash
python manage.py wait_for_db
```

This is especially useful with **Docker**.

For example, your application container might start before PostgreSQL is ready:

```text
Docker starts
    ↓
PostgreSQL container starts
    ↓
Django container starts
    ↓
Django tries to connect
    ↓
PostgreSQL isn't ready yet ❌
```

Instead, you can do:

```text
Docker starts
    ↓
PostgreSQL container starts
    ↓
Django container starts
    ↓
python manage.py wait_for_db
    ↓
Database unavailable → wait
    ↓
Database unavailable → wait
    ↓
Database available ✅
    ↓
Start Django
```

That's why `wait_for_db` is a common custom management command in Django Docker projects.

---

## Commands can also accept arguments

This is where custom commands become even more useful.

For example:

```bash
python manage.py create_users 10
```

You can define an argument:

```python
from django.core.management import CommandParser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create users."""

    def add_arguments(self, parser:CommandParser) -> None:
        parser.add_argument(
            "count",
            type=int,
        )

    def handle(self, *args: object, **options: object) -> None:
        count = options["count"]

        self.stdout.write(f"Creating {count} users...")
```

Now:

```bash
python manage.py create_users 10
```

would give your command:

```python
options["count"]  # 10
```

You can also create optional flags:

```bash
python manage.py create_users --count 10 --admin
```

---

## Why use a management command instead of a Python script?

You could technically write:

```python
# create_users.py
```

and execute it directly, but a Django management command gives you Django's environment automatically.

That means you can directly use:

```python
from myapp.models import User
```

and Django already knows about:

* settings
* database configuration
* installed apps
* Django ORM
* models
* authentication
* migrations
* other Django infrastructure

So instead of doing something like:

```bash
python my_script.py
```

you have:

```bash
python manage.py my_command
```

and Django initializes the application for you.

### In short

Think of a custom management command as:

> **A reusable Python script that runs inside Django's environment and is exposed as a `manage.py` command.**

The basic recipe is:

```text
1. Have a Django app
       ↓
2. Create management/
       ↓
3. Create commands/
       ↓
4. Create my_command.py
       ↓
5. Create Command(BaseCommand)
       ↓
6. Put your logic in handle()
       ↓
7. Run: python manage.py my_command
```

And importantly, **`core` is just an app name**. It could be `users`, `products`, `common`, `api`, `tasks`, etc.
