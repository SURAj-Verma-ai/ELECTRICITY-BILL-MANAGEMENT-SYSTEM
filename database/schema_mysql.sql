-- EBMS core schema (MySQL)

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_username_length CHECK (CHAR_LENGTH(username) BETWEEN 3 AND 20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- One row per security question a user answered at signup. The question
-- text itself is not stored here, it lives in code (src/content/security_questions.py)
-- because the list of questions never changes. Only the id + hashed answer are saved.
CREATE TABLE IF NOT EXISTS security_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_user_question (user_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
