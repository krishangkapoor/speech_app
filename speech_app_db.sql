CREATE DATABASE speech_app_db;

USE speech_app_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE transcriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transcription TEXT NOT NULL,
    translated_transcription TEXT,
    language VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE word_frequencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    word VARCHAR(100) NOT NULL,
    frequency INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE unique_phrases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phrase TEXT NOT NULL,
    frequency INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
