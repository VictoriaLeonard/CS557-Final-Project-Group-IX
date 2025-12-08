DROP DATABASE IF EXISTS quizmaster_db;
CREATE DATABASE quizmaster_db;
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
    question_type ENUM('MCQ', 'TF', 'SA') NOT NULL,
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
    score DECIMAL(5,2) NULL,
    total_points INT NOT NULL,
    percentage DECIMAL(5,2) NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    time_taken INT NULL,
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
    selected_answer_id INT NULL,
    response_text TEXT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    points_earned INT DEFAULT 0,
    graded_by INT NULL,
    graded_at TIMESTAMP NULL,
    feedback TEXT NULL,
    FOREIGN KEY (attempt_id) REFERENCES student_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_answer_id) REFERENCES answers(answer_id) ON DELETE SET NULL,
    FOREIGN KEY (graded_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_attempt (attempt_id),
    INDEX idx_question (question_id),
    INDEX idx_grading (graded_by, graded_at),
    UNIQUE KEY unique_response (attempt_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO roles (role_name) VALUES ('student'), ('instructor'), ('admin');


CREATE TABLE user_role_map (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
);


CREATE TABLE quiz_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE quiz_category_map (
    quiz_id INT NOT NULL,
    category_id INT NOT NULL,
    PRIMARY KEY (quiz_id, category_id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES quiz_categories(category_id) ON DELETE CASCADE
);


CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE VIEW v_student_quiz_summary AS
SELECT
    sa.attempt_id,
    sa.student_id,
    u.username AS student_username,
    sa.quiz_id,
    q.title AS quiz_title,
    sa.score,
    sa.percentage,
    sa.submit_time
FROM student_attempts sa
JOIN users u ON sa.student_id = u.user_id
JOIN quizzes q ON sa.quiz_id = q.quiz_id;


CREATE VIEW v_quiz_performance AS
SELECT
    q.quiz_id,
    q.title,
    COUNT(sa.attempt_id) AS attempts,
    AVG(sa.percentage) AS avg_score,
    MIN(sa.percentage) AS min_score,
    MAX(sa.percentage) AS max_score
FROM quizzes q
LEFT JOIN student_attempts sa ON q.quiz_id = sa.quiz_id
GROUP BY q.quiz_id, q.title;


CREATE TRIGGER trg_quiz_created
AFTER INSERT ON quizzes
FOR EACH ROW
INSERT INTO audit_logs (user_id, action)
VALUES (NEW.instructor_id, CONCAT('Created quiz: ', NEW.title));


DELIMITER //
CREATE TRIGGER trg_attempt_calc_percentage
BEFORE UPDATE ON student_attempts
FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL AND NEW.total_points > 0 THEN
        SET NEW.percentage = (NEW.score / NEW.total_points) * 100;
    END IF;
END //
DELIMITER ;


DELIMITER //
CREATE FUNCTION fn_percentage(score DECIMAL(5,2), total INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    RETURN (score / total) * 100;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE sp_create_quiz(
    IN p_instructor INT,
    IN p_title VARCHAR(200),
    IN p_description TEXT,
    IN p_time_limit INT,
    IN p_passing INT,
    IN p_start DATETIME,
    IN p_end DATETIME
)
BEGIN
    INSERT INTO quizzes(instructor_id, title, description, time_limit, passing_score, start_date, end_date)
    VALUES(p_instructor, p_title, p_description, p_time_limit, p_passing, p_start, p_end);

    INSERT INTO audit_logs(user_id, action)
    VALUES(p_instructor, CONCAT('Created quiz via SP: ', p_title));
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE sp_assign_role(
    IN p_user INT,
    IN p_role VARCHAR(50)
)
BEGIN
    DECLARE v_role_id INT;

    SELECT role_id INTO v_role_id
    FROM roles
    WHERE role_name = p_role;

    INSERT IGNORE INTO user_role_map (user_id, role_id)
    VALUES (p_user, v_role_id);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE sp_instructor_avg_report()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE instr INT;

    DECLARE c CURSOR FOR
        SELECT DISTINCT instructor_id FROM quizzes;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN c;
    read_loop: LOOP
        FETCH c INTO instr;
        IF done THEN LEAVE read_loop; END IF;

        SELECT
            u.username AS instructor,
            AVG(sa.percentage) AS average_score
        FROM quizzes q
        LEFT JOIN student_attempts sa ON q.quiz_id = sa.quiz_id
        JOIN users u ON u.user_id = q.instructor_id
        WHERE q.instructor_id = instr;
    END LOOP;

    CLOSE c;
END //
DELIMITER ;

