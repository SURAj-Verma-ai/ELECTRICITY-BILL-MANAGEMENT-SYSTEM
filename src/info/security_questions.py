"""The fixed list of account-recovery security questions.

These never change, so they live here in code instead of a database table.
Each question has a small number as its id. That id (not the question
text) is what gets saved in the security_answers table, so the wording
above can be edited later without breaking anyone's saved answers.
"""

QUESTIONS = [
    {"id": 1, "text": "What was the name of your first employer?"},
    {"id": 2, "text": "What is your mother's maiden name?"},
    {"id": 3, "text": "What was the name of your first school?"},
    {"id": 4, "text": "What city were you born in?"},
    {"id": 5, "text": "What was your childhood nickname?"},
    {"id": 6, "text": "Who is your favorite teacher?"},
]

# At signup, a user must answer at least this many of the questions above
# (their choice which ones). During recovery, they will be asked to answer
# those exact same questions again to prove it's really them.
MIN_SECURITY_ANSWERS = 3
