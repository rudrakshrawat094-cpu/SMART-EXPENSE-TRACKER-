"""User management: registration and login with salted PBKDF2 password hashing."""
import hashlib
import hmac
import os

from .config import PBKDF2_ITERATIONS
from .database import Database
from .exceptions import AuthError, DuplicateError
from .logger import get_logger
from .models import User
from .validators import validate_password, validate_username

log = get_logger("auth")


def hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS).hex()


class AuthService:
    def __init__(self, db: Database):
        self.db = db

    def register(self, username: str, password: str) -> User:
        username = validate_username(username)
        password = validate_password(password)
        salt = os.urandom(16)
        try:
            cur = self.db.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, hash_password(password, salt), salt.hex()))
        except DuplicateError:
            raise AuthError("That username is already taken.") from None
        log.info("Registered user '%s'", username)
        return User(cur.lastrowid, username)

    def login(self, username: str, password: str) -> User:
        row = self.db.query_one("SELECT * FROM users WHERE username = ?", ((username or "").strip(),))
        # Same generic message for unknown user / wrong password (no user enumeration)
        if row is None:
            log.warning("Failed login for unknown user")
            raise AuthError("Invalid username or password.")
        candidate = hash_password(password or "", bytes.fromhex(row["salt"]))
        if not hmac.compare_digest(candidate, row["password_hash"]):
            log.warning("Failed login for user '%s'", row["username"])
            raise AuthError("Invalid username or password.")
        log.info("User '%s' logged in", row["username"])
        return User(row["id"], row["username"])
