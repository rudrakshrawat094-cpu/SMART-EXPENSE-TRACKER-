import unittest

import _bootstrap  # noqa: F401
from base import DBTestCase
from expense_tracker.auth import AuthService
from expense_tracker.exceptions import AuthError, ValidationError


class AuthTests(DBTestCase):
    def test_login_success(self):
        user = AuthService(self.db).login("alice", "secret123")
        self.assertEqual(user.id, self.user.id)

    def test_wrong_password_and_unknown_user_same_message(self):
        auth = AuthService(self.db)
        with self.assertRaises(AuthError) as a:
            auth.login("alice", "wrong123")
        with self.assertRaises(AuthError) as b:
            auth.login("nobody", "secret123")
        self.assertEqual(str(a.exception), str(b.exception))

    def test_duplicate_username(self):
        with self.assertRaises(AuthError):
            AuthService(self.db).register("alice", "another123")

    def test_password_is_hashed_and_salted(self):
        AuthService(self.db).register("bob", "secret123")
        rows = self.db.query("SELECT password_hash, salt FROM users")
        self.assertNotIn("secret123", rows[0]["password_hash"])
        self.assertNotEqual(rows[0]["password_hash"], rows[1]["password_hash"])  # different salts

    def test_weak_password_rejected(self):
        with self.assertRaises(ValidationError):
            AuthService(self.db).register("carol", "abc")


if __name__ == "__main__":
    import unittest
    unittest.main()
