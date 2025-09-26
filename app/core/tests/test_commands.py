"""
Test custom Django management commands.
"""

from unittest.mock import patch, MagicMock
from psycopg2 import OperationalError as Psycopg2OperationalError
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


class CommandTests(SimpleTestCase):
    """Test commands."""

    @patch("django.db.utils.ConnectionHandler.__getitem__")
    def test_wait_for_db_ready(self, mocked_getitem):
        """Test waiting for database if database is ready."""

        mocked_getitem.return_value.cursor.return_value = True

        call_command("wait_for_db")

        mocked_getitem.assert_called_once_with("default")

    @patch("django.db.utils.ConnectionHandler.__getitem__")
    @patch("time.sleep")
    def test_wait_for_db_delay(self, mocked_sleep, mocked_getitem):
        """Test waiting for database when getting OperationalError"""

        mocked_getitem.side_effect = (
            [Psycopg2OperationalError] * 2 + [OperationalError] * 3 + [MagicMock()]
        )

        call_command("wait_for_db")

        self.assertEqual(mocked_getitem.call_count, 6)
        mocked_sleep.assert_called_with(1)
