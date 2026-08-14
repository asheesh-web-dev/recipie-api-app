"""
Test custom Django management commands.
"""

from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg import OperationalError as PsycopgError


@patch("core.management.commands.wait_for_db.connections")
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(
        self, patched_check: MagicMock, patched_connections: MagicMock
    ) -> None:
        """Test waiting for database if database ready.

        How it works:
            1. The Test Runner: the test runner calls the method and the patch wrapper automatically injects
               the MagicMock object into your arguments.
            2. patched_check represents the check method itself.
              1. The Mock is the Function: The @patch decorator intercepts the check method
                 and swaps it out entirely. So, patched_check is the actual function replacement.
            3. Setting the Return Value: Because patched_check is the function,
               you write patched_check.return_value = True. This tells Python:
               "Whenever someone calls this function inside the management command, make it return True."
            4. The Execution: When call_command("wait_for_db") runs, your command internally executes
               self.check(databases=['default']). Because of the patch, it is actually calling your mock function,
               which immediately spits out True.
            5. The Assertion: Yes, assert_called_once_with verifies that the command executed that specific method
               exactly once and passed databases=["default"] to it.
        """
        patched_connection = MagicMock()
        patched_get_item = MagicMock()
        patched_ensure_connection = MagicMock()
        patched_connections.__getitem__ = patched_get_item
        patched_get_item.return_value = patched_connection
        patched_connection.ensure_connection = patched_ensure_connection

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])
        patched_get_item.assert_called_once_with("default")
        patched_ensure_connection.assert_called_once()

    @patch("time.sleep")
    def test_wait_for_db_delay(
        self,
        patched_sleep: MagicMock,
        patched_check: MagicMock,
        patched_connections: MagicMock,
    ):
        """Test waiting for database when errors are raised initially."""
        patched_connection = MagicMock()
        patched_get_item = MagicMock()
        patched_ensure_connection = MagicMock()
        patched_connections.__getitem__ = patched_get_item
        patched_get_item.return_value = patched_connection
        patched_connection.ensure_connection = patched_ensure_connection

        patched_ensure_connection.side_effect = (
            [PsycopgError] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        patched_check.assert_called_with(databases=["default"])
        self.assertEqual(patched_check.call_count, 6)
        patched_get_item.assert_called_with("default")
        self.assertEqual(patched_ensure_connection.call_count, 6)
