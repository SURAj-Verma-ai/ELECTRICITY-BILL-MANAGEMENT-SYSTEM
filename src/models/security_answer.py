"""Storage for account-recovery security question answers.

Answers are hashed with bcrypt, exactly like passwords. We never store the
plain text answer to "what is your mother's maiden name?" in the database.
"""

import bcrypt

from src.data.database import get_cursor


def _normalize(answer: str) -> str:
    # Lowercase + trim so "Blue" and " blue " count as the same answer.
    # These answers are easy to mistype in odd casing/spacing, and getting
    # locked out of your own account over a capital letter is not fun.
    return answer.strip().lower()


def _hash_answer(answer: str) -> str:
    # Turn a plain-text answer into a one-way hash, same approach as
    # password hashing: this can be checked against later, but not reversed.
    normalized = _normalize(answer)
    return bcrypt.hashpw(normalized.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_answer(answer: str, answer_hash: str) -> bool:
    # Compare a freshly typed answer against a stored hash from before.
    normalized = _normalize(answer)
    return bcrypt.checkpw(normalized.encode("utf-8"), answer_hash.encode("utf-8"))


class SecurityAnswer:
    @staticmethod
    def save_answers(user_id: int, answers: dict) -> None:
        # Save a batch of {question_id: plain_text_answer} for one user.
        # Called once, right after their account is created.
        with get_cursor(commit=True) as cursor:
            for question_id, answer in answers.items():
                cursor.execute(
                    "INSERT INTO security_answers (user_id, question_id, answer_hash) "
                    "VALUES (%s, %s, %s)",
                    (user_id, question_id, _hash_answer(answer)),
                )

    @staticmethod
    def question_ids_for_user(user_id: int):
        # Which questions did this user answer at signup? We need this list
        # so recovery can ask them the SAME questions, not different ones.
        with get_cursor() as cursor:
            cursor.execute(
                "SELECT question_id FROM security_answers WHERE user_id = %s",
                (user_id,),
            )
            rows = cursor.fetchall()
            return [row["question_id"] for row in rows]

    @staticmethod
    def verify_answer(user_id: int, question_id: int, provided_answer: str) -> bool:
        # Check one typed-in answer against the hash saved for that
        # question. Returns False if the question was never answered too.
        with get_cursor() as cursor:
            cursor.execute(
                "SELECT answer_hash FROM security_answers WHERE user_id = %s AND question_id = %s",
                (user_id, question_id),
            )
            row = cursor.fetchone()
            if not row:
                return False
            return _check_answer(provided_answer, row["answer_hash"])
