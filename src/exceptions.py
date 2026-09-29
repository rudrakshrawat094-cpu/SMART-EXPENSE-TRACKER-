"""Custom exception hierarchy so callers can handle errors precisely."""


class ExpenseTrackerError(Exception):
    """Base class for all application errors."""


class ValidationError(ExpenseTrackerError, ValueError):
    """User supplied invalid input."""


class AuthError(ExpenseTrackerError):
    """Authentication or registration failed."""


class NotFoundError(ExpenseTrackerError):
    """Requested record does not exist (or belongs to someone else)."""


class DuplicateError(ExpenseTrackerError):
    """A unique constraint was violated."""


class DatabaseError(ExpenseTrackerError):
    """Unexpected storage-layer failure."""
