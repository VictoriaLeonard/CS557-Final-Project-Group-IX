CREATE DATABASE IF NOT EXISTS quizmaster_db;
USE quizmaster_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    role ENUM('instructor', 'student') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE quizzes (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    time_limit INT NOT NULL COMMENT 'Time limit in minutes',
    passing_score INT DEFAULT 60 CHECK (passing_score >= 0 AND passing_score <= 100),
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_instructor (instructor_id),
    INDEX idx_active (is_active),
    INDEX idx_dates (start_date, end_date),
    CONSTRAINT chk_date_order CHECK (end_date > start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM('MCQ', 'TF', 'SA') NOT NULL COMMENT 'MCQ=Multiple Choice, TF=True/False, SA=Short Answer',
    points INT DEFAULT 1 CHECK (points > 0),
    question_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_quiz (quiz_id),
    INDEX idx_type (question_type),
    INDEX idx_order (quiz_id, question_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    answer_text VARCHAR(500) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    answer_order INT DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_question (question_id),
    INDEX idx_correct (question_id, is_correct)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE student_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    quiz_id INT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submit_time TIMESTAMP NULL,
    score DECIMAL(5,2) NULL COMMENT 'Actual score earned',
    total_points INT NOT NULL COMMENT 'Total possible points',
    percentage DECIMAL(5,2) NULL COMMENT 'Score as percentage',
    is_completed BOOLEAN DEFAULT FALSE,
    time_taken INT NULL COMMENT 'Time taken in seconds',
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_quiz (quiz_id),
    INDEX idx_completed (is_completed),
    INDEX idx_student_quiz (student_id, quiz_id),
    UNIQUE KEY unique_attempt (student_id, quiz_id, start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE student_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer_id INT NULL COMMENT 'For MCQ/TF questions',
    response_text TEXT NULL COMMENT 'For short answer questions',
    is_correct BOOLEAN DEFAULT FALSE,
    points_earned INT DEFAULT 0,
    graded_by INT NULL COMMENT 'Instructor ID for manual grading',
    graded_at TIMESTAMP NULL,
    feedback TEXT NULL COMMENT 'Instructor feedback for short answers',
    FOREIGN KEY (attempt_id) REFERENCES student_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_answer_id) REFERENCES answers(answer_id) ON DELETE SET NULL,
    FOREIGN KEY (graded_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_attempt (attempt_id),
    INDEX idx_question (question_id),
    INDEX idx_grading (graded_by, graded_at),
    UNIQUE KEY unique_response (attempt_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;