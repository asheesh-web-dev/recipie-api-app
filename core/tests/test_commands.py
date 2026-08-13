"""
Test custom Django management commands.
"""

from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg import OperationalError as PsycopgError


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check: MagicMock) -> None:
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
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_delay(
        self, patched_sleep: MagicMock, patched_check: MagicMock
    ):
        """Test waiting for database when errors are raised initially."""
        patched_check.side_effect = [PsycopgError] * 2 + [OperationalError] * 3 + [True]

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
