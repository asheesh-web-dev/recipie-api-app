"""
Django command to wait for the database to be available.
"""

import time

from django.core.management import CommandParser
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg import OperationalError as PsycopgError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: object, **options: object):
        """Entrypoint for command."""
        self.stdout.write("waiting for database...")
        while True:
            try:
                # Django system checks
                # it doesn't check actual connection. it only checks if all configurations are correct.
                self.check(databases=["default"])

                # Actual database connection
                connections["default"].ensure_connection()
                break
            except PsycopgError, OperationalError:
                self.stdout.write("Database unavaiable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)
