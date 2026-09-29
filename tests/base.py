import unittest

import _bootstrap  # noqa: F401
from expense_tracker.auth import AuthService
from expense_tracker.database import Database


class DBTestCase(unittest.TestCase):
    """Gives each test a fresh in-memory database and a registered user."""

    def setUp(self):
        self.db = Database(":memory:")
        self.user = AuthService(self.db).register("alice", "secret123")

    def tearDown(self):
        self.db.close()
