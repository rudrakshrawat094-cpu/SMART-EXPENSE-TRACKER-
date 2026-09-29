"""Pure input-validation helpers. Every function returns a cleaned value or raises ValidationError."""
import math
import re
from datetime import date, datetime

from .config import (CATEGORIES, DATE_FORMAT, MAX_AMOUNT, MAX_DESCRIPTION_LEN,
                     MIN_PASSWORD_LEN, MONTH_FORMAT)
from .exceptions import ValidationError

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


def validate_username(username: str) -> str:
    username = (username or "").strip()
    if not _USERNAME_RE.match(username):
        raise ValidationError("Username must be 3-20 characters: letters, digits or underscore.")
    return username


def validate_password(password: str) -> str:
    password = password or ""
    if len(password) < MIN_PASSWORD_LEN:
        raise ValidationError(f"Password must be at least {MIN_PASSWORD_LEN} characters.")
    if not (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
        raise ValidationError("Password must contain at least one letter and one digit.")
    return password


def validate_amount(value) -> float:
    try:
        amount = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        raise ValidationError("Amount must be a number.") from None
    if math.isnan(amount) or math.isinf(amount):
        raise ValidationError("Amount must be a finite number.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if amount > MAX_AMOUNT:
        raise ValidationError(f"Amount cannot exceed {MAX_AMOUNT:,}.")
    return round(amount, 2)


def validate_date(value: str) -> str:
    try:
        parsed = datetime.strptime((value or "").strip(), DATE_FORMAT).date()
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format.") from None
    if parsed > date.today():
        raise ValidationError("Date cannot be in the future.")
    return parsed.strftime(DATE_FORMAT)


def validate_month(value: str) -> str:
    try:
        return datetime.strptime((value or "").strip(), MONTH_FORMAT).strftime(MONTH_FORMAT)
    except ValueError:
        raise ValidationError("Month must be in YYYY-MM format.") from None


def validate_category(value: str) -> str:
    cleaned = (value or "").strip().title()
    if cleaned not in CATEGORIES:
        raise ValidationError(f"Category must be one of: {', '.join(CATEGORIES)}.")
    return cleaned


def validate_description(value: str) -> str:
    value = (value or "").strip()
    if len(value) > MAX_DESCRIPTION_LEN:
        raise ValidationError(f"Description must be at most {MAX_DESCRIPTION_LEN} characters.")
    return value
