"""User data access: raw SQL against MySQL, kept intentionally simple."""

from src.data.database import get_cursor, IntegrityError


class DuplicateUserError(Exception):
    # happens if two signups race each other at the same time
    def __init__(self, field: str):
        self.field = field
        super().__init__(field)


class User:
    def __init__(self, id, username, email, password_hash, is_active=True, is_admin=False, **_extra):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.is_admin = bool(is_admin)

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
        with get_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_password_hash, user_id),
            )

    @staticmethod
    def list_all():
        # used on the admin users page
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY id DESC")
            return [User(**row) for row in cursor.fetchall()]

    @staticmethod
    def count():
        with get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM users")
            return cursor.fetchone()["total"]

    @staticmethod
    def set_admin(user_id: int, is_admin: bool):
        with get_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET is_admin = %s WHERE id = %s",
                (1 if is_admin else 0, user_id),
            )
