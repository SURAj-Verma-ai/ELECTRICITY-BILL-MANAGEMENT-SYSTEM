"""Input validation rules for auth (username, email, password).

Kept as plain functions returning (is_valid, error_message) so both the
Flask routes and any future API layer can reuse them without a framework
dependency.
"""

import re
from datetime import datetime

from src.info.billing import MIN_UNITS, MAX_UNITS

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
PASSWORD_SPECIAL_CHARS = r"""!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?"""
_PASSWORD_SPECIAL_PATTERN = re.compile(f"[{re.escape(PASSWORD_SPECIAL_CHARS)}]")

EMAIL_MAX_LENGTH = 254
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SECURITY_ANSWER_MIN_LENGTH = 2
SECURITY_ANSWER_MAX_LENGTH = 100

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 50

ADDRESS_MIN_LENGTH = 5
ADDRESS_MAX_LENGTH = 100

SUBJECT_MIN_LENGTH = 5
SUBJECT_MAX_LENGTH = 100

DESCRIPTION_MIN_LENGTH = 10
DESCRIPTION_MAX_LENGTH = 1000

BILLING_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


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


def validate_name(name: str):
    # this is just a basic lenght check which check lenght 
    if not name:
        return False, "Name is required."
    name = name.strip()
    if len(name) < NAME_MIN_LENGTH or len(name) > NAME_MAX_LENGTH:
        return False, f"Name must be {NAME_MIN_LENGTH}-{NAME_MAX_LENGTH} characters."
    return True, ""


def validate_address(address: str):
    # just a quick length check for address
    if not address:
        return False, "Address is required."
    address = address.strip()
    if len(address) < ADDRESS_MIN_LENGTH or len(address) > ADDRESS_MAX_LENGTH:
        return False, f"Address must be {ADDRESS_MIN_LENGTH}-{ADDRESS_MAX_LENGTH} characters."
    return True, ""


def validate_units(units_raw: str):
    # check units is a number in range
    try:
        units = int(units_raw)
    except (TypeError, ValueError):
        return False, "Units must be a whole number.", None
    if units < MIN_UNITS or units > MAX_UNITS:
        return False, f"Units must be {MIN_UNITS}-{MAX_UNITS}.", None
    return True, "", units


def validate_billing_month(month: str):
    # check month is in yyyy-mm format
    if not month or not BILLING_MONTH_PATTERN.match(month.strip()):
        return False, "Billing month must be in YYYY-MM format."
    return True, ""


def validate_due_date(due_date: str):
    # check the date is actually valid
    try:
        datetime.strptime(due_date.strip(), "%Y-%m-%d")
    except (TypeError, ValueError, AttributeError):
        return False, "Enter a valid due date."
    return True, ""


def validate_subject(subject: str):
    # quick length check for subject line
    if not subject:
        return False, "Subject is required."
    subject = subject.strip()
    if len(subject) < SUBJECT_MIN_LENGTH or len(subject) > SUBJECT_MAX_LENGTH:
        return False, f"Subject must be {SUBJECT_MIN_LENGTH}-{SUBJECT_MAX_LENGTH} characters."
    return True, ""


def validate_description(description: str):
    # quick length check for the description
    if not description:
        return False, "Description is required."
    description = description.strip()
    if len(description) < DESCRIPTION_MIN_LENGTH or len(description) > DESCRIPTION_MAX_LENGTH:
        return False, f"Description must be {DESCRIPTION_MIN_LENGTH}-{DESCRIPTION_MAX_LENGTH} characters."
    return True, ""
