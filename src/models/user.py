"""User data access: raw SQL against MySQL, kept intentionally simple."""

from src.data.database import get_cursor, IntegrityError


class DuplicateUserError(Exception):
    """Raised when a UNIQUE constraint (username or email) is violated.

    This is the safety net for the check-then-insert race: two requests can
    both pass `username_exists`/`email_exists` before either commits, so the
    database's own constraint is the real source of truth.
    """

    def __init__(self, field: str):
        self.field = field  # "username", "email", or "unknown"
        super().__init__(field)


class User:
    def __init__(self, id, username, email, password_hash, is_active=True, **_extra):
        # **_extra swallows other columns (created_at, last_login_at, ...)
        # so this stays a thin wrapper without needing to enumerate every column.
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active

    @staticmethod
    def create(username: str, email: str, password_hash: str) -> int:
        try:
            with get_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                    (username, email, password_hash),
                )
                return cursor.lastrowid
        except IntegrityError as e:
            message = str(e).lower()
            if "username" in message:
                raise DuplicateUserError("username") from e
            if "email" in message:
                raise DuplicateUserError("email") from e
            raise DuplicateUserError("unknown") from e

    @staticmethod
    def find_by_username(username: str):
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()
            return User(**row) if row else None

    @staticmethod
    def find_by_email(email: str):
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            return User(**row) if row else None

    @staticmethod
    def find_by_id(user_id: int):
        # Used during password recovery: once we know WHICH user is
        # recovering (by their id), we need their full record again.
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return User(**row) if row else None

    @staticmethod
    def username_exists(username: str) -> bool:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            return cursor.fetchone() is not None

    @staticmethod
    def email_exists(email: str) -> bool:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cursor.fetchone() is not None

    @staticmethod
    def update_last_login(user_id: int):
        with get_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET last_login_at = NOW() WHERE id = %s", (user_id,)
            )

    @staticmethod
    def update_password(user_id: int, new_password_hash: str):
        # Used by both "change password" (user is logged in and remembers
        # the old one) and "forgot password" (user proved who they are via
        # security questions instead).
        with get_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_password_hash, user_id),
            )
