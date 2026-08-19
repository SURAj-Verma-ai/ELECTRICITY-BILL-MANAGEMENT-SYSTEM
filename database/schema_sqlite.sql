-- EBMS core schema (SQLite, development only)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    is_active INTEGER NOT NULL DEFAULT 1,

    CHECK (LENGTH(username) BETWEEN 3 AND 20)
);

-- One row per security question a user answered at signup. The question
-- text itself is not stored here, it lives in code (src/content/security_questions.py)
-- because the list of questions never changes. Only the id + hashed answer are saved.
CREATE TABLE IF NOT EXISTS security_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, question_id)
);
