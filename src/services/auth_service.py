"""Registration, login, password change, and password recovery logic.

This file is the "brain" of auth: routes collect form data and call
functions here, functions here call the models (User, SecurityAnswer) to
talk to the database. Nothing in this file knows about Flask, forms, or
HTML, that keeps it easy to test and easy to read top to bottom.
"""

import bcrypt

from src.models.user import User, DuplicateUserError
from src.models.security_answer import SecurityAnswer
from src.content.security_questions import QUESTIONS, MIN_SECURITY_ANSWERS
from src.utils.validators import (
    validate_username,
    validate_email,
    validate_password,
    validate_security_answer,
)

_VALID_QUESTION_IDS = {q["id"] for q in QUESTIONS}


class AuthError(Exception):
    """Raised for any validation/auth failure; the message is shown to the user as-is."""


def _hash_password(password: str) -> str:
    # Turn a plain-text password into a one-way hash. We store this, never
    # the real password, so even we can't see what someone's password is.
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, password_hash: str) -> bool:
    # Check a freshly typed password against a stored hash from before.
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _clean_security_answers(security_answers: dict) -> dict:
    # Take whatever the form sent us, drop blanks, drop unknown question
    # ids, and check each remaining answer is a sane length. Returns the
    # cleaned-up dict of {question_id: answer_text} that is safe to save.
    cleaned = {}
    for question_id, answer in (security_answers or {}).items():
        if question_id not in _VALID_QUESTION_IDS:
            continue
        answer = (answer or "").strip()
        if not answer:
            continue
        ok, msg = validate_security_answer(answer)
        if not ok:
            raise AuthError(msg)
        cleaned[question_id] = answer

    if len(cleaned) < MIN_SECURITY_ANSWERS:
        raise AuthError(f"Please answer at least {MIN_SECURITY_ANSWERS} security questions.")

    return cleaned


def register_user(
    username: str, email: str, password: str, confirm_password: str, security_answers: dict
) -> User:
    """Create a new account. Checks every field, then saves the user and
    their chosen security-question answers (used later for recovery)."""
    username = (username or "").strip()
    email = (email or "").strip().lower()

    ok, msg = validate_username(username)
    if not ok:
        raise AuthError(msg)

    ok, msg = validate_email(email)
    if not ok:
        raise AuthError(msg)

    ok, msg = validate_password(password)
    if not ok:
        raise AuthError(msg)

    if password != confirm_password:
        raise AuthError("Passwords do not match.")

    # Do this validation before touching the database, so a bad answer
    # doesn't leave us with a half-created account.
    cleaned_answers = _clean_security_answers(security_answers)

    if User.username_exists(username):
        raise AuthError("That username is already taken.")

    if User.email_exists(email):
        raise AuthError("An account with that email already exists.")

    password_hash = _hash_password(password)
    try:
        user_id = User.create(username, email, password_hash)
    except DuplicateUserError as e:
        # Safety net for the race between the exists-checks above and this
        # insert (e.g. a double-submitted form), same messages as above.
        if e.field == "username":
            raise AuthError("That username is already taken.") from e
        if e.field == "email":
            raise AuthError("An account with that email already exists.") from e
        raise AuthError("Could not create account. Please try again.") from e

    SecurityAnswer.save_answers(user_id, cleaned_answers)

    return User(id=user_id, username=username, email=email, password_hash=password_hash)


def login_user(username_or_email: str, password: str) -> User:
    """Check a username/email + password pair and return the matching user."""
    identifier = (username_or_email or "").strip()

    # A basic length guard: nobody's username or email is 1000 characters,
    # no reason to let a request that large reach the database.
    if not identifier or len(identifier) > 254 or not password:
        raise AuthError("Invalid credentials.")

    user = User.find_by_email(identifier.lower()) if "@" in identifier else User.find_by_username(identifier)

    if not user or not _check_password(password, user.password_hash):
        raise AuthError("Invalid credentials.")

    if not user.is_active:
        raise AuthError("This account has been deactivated.")

    User.update_last_login(user.id)
    return user


def change_password(user_id: int, old_password: str, new_password: str, confirm_password: str) -> None:
    """Let a logged-in user set a new password. They must type their
    current password correctly first, this is NOT the forgot-password flow."""
    user = User.find_by_id(user_id)
    if not user:
        raise AuthError("Account not found.")

    if not _check_password(old_password, user.password_hash):
        raise AuthError("Your current password is incorrect.")

    ok, msg = validate_password(new_password)
    if not ok:
        raise AuthError(msg)

    if new_password != confirm_password:
        raise AuthError("New passwords do not match.")

    if _check_password(new_password, user.password_hash):
        raise AuthError("New password must be different from your current password.")

    User.update_password(user_id, _hash_password(new_password))


def find_user_for_recovery(identifier: str) -> User:
    """Step 1 of forgot-password: look up the account by username or
    email. Raises if nothing matches."""
    identifier = (identifier or "").strip()
    if not identifier or len(identifier) > 254:
        raise AuthError("No account matches that username or email.")

    user = User.find_by_email(identifier.lower()) if "@" in identifier else User.find_by_username(identifier)
    if not user:
        raise AuthError("No account matches that username or email.")

    return user


def get_recovery_questions(user_id: int) -> list:
    """Step 2 setup: figure out which questions THIS user answered at
    signup, so we only ask them those, in the same wording as QUESTIONS."""
    answered_ids = set(SecurityAnswer.question_ids_for_user(user_id))
    questions = [q for q in QUESTIONS if q["id"] in answered_ids]

    if not questions:
        raise AuthError("No recovery questions are set up for this account.")

    return questions


def verify_recovery_answers(user_id: int, submitted_answers: dict) -> bool:
    """Step 2 check: does every answer the user just typed match what they
    saved at signup? All of them must be correct, not just some."""
    required_ids = SecurityAnswer.question_ids_for_user(user_id)
    if not required_ids:
        return False

    for question_id in required_ids:
        typed_answer = submitted_answers.get(question_id, "")
        if not SecurityAnswer.verify_answer(user_id, question_id, typed_answer):
            return False

    return True


def reset_password(user_id: int, new_password: str, confirm_password: str) -> None:
    """Step 3: set a brand new password after recovery has been verified.
    Unlike change_password, this does NOT ask for the old password, that
    is the whole point of "forgot" password recovery."""
    ok, msg = validate_password(new_password)
    if not ok:
        raise AuthError(msg)

    if new_password != confirm_password:
        raise AuthError("Passwords do not match.")

    User.update_password(user_id, _hash_password(new_password))
