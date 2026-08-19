"""Input validation rules for auth (username, email, password).

Kept as plain functions returning (is_valid, error_message) so both the
Flask routes and any future API layer can reuse them without a framework
dependency.
"""

import re

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
PASSWORD_SPECIAL_CHARS = r"""!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?"""
_PASSWORD_SPECIAL_PATTERN = re.compile(f"[{re.escape(PASSWORD_SPECIAL_CHARS)}]")

EMAIL_MAX_LENGTH = 254  # practical upper bound from the email spec (RFC 5321)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SECURITY_ANSWER_MIN_LENGTH = 2
SECURITY_ANSWER_MAX_LENGTH = 100


def validate_username(username: str):
    if not username:
        return False, "Username is required."

    username = username.strip()

    if len(username) < USERNAME_MIN_LENGTH:
        return False, f"Username must be at least {USERNAME_MIN_LENGTH} characters."

    if len(username) > USERNAME_MAX_LENGTH:
        return False, f"Username must be at most {USERNAME_MAX_LENGTH} characters."

    if not USERNAME_PATTERN.match(username):
        return False, "Username can only contain letters, numbers, and underscores."

    return True, ""


def validate_email(email: str):
    if not email:
        return False, "Email is required."

    email = email.strip()

    if len(email) > EMAIL_MAX_LENGTH:
        return False, f"Email must be at most {EMAIL_MAX_LENGTH} characters."

    if not EMAIL_PATTERN.match(email):
        return False, "Enter a valid email address."

    return True, ""


def validate_password(password: str):
    if not password:
        return False, "Password is required."

    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters."

    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password must be at most {PASSWORD_MAX_LENGTH} characters."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."

    if not _PASSWORD_SPECIAL_PATTERN.search(password):
        return False, "Password must contain at least one special character (e.g. !@#$%)."

    if re.search(r"\s", password):
        return False, "Password cannot contain spaces."

    return True, ""


def validate_security_answer(answer: str):
    """Check one security-question answer is a sane length before we hash
    it. Same idea as validate_username/validate_password above."""
    if not answer:
        return False, "Answer cannot be empty."

    answer = answer.strip()

    if len(answer) < SECURITY_ANSWER_MIN_LENGTH:
        return False, f"Answer must be at least {SECURITY_ANSWER_MIN_LENGTH} characters."

    if len(answer) > SECURITY_ANSWER_MAX_LENGTH:
        return False, f"Answer must be at most {SECURITY_ANSWER_MAX_LENGTH} characters."

    return True, ""
