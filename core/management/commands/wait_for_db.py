"""
Django command to wait for the database to be available.
"""

import time

from django.core.management import CommandParser
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg import OperationalError as PsycopgError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: object, **options: object):
        """Entrypoint for command."""
        self.stdout.write("waiting for database...")
        while True:
            try:
                self.check(databases=["default"])
                break
            except PsycopgError, OperationalError:
                self.stdout.write("Database unavaiable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)
