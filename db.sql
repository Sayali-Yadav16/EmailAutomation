-- =========================
-- CREATE DATABASE
-- =========================
CREATE DATABASE IF NOT EXISTS hospital_rpa;
USE hospital_rpa;

-- =========================
-- PATIENTS TABLE (UPDATED)
-- =========================
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    doctor VARCHAR(100),
    appointment_date DATE,
    slot VARCHAR(50),
    priority VARCHAR(50) DEFAULT 'Normal',
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- AUTOMATION LOGS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS automation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    action VARCHAR(255),
    status VARCHAR(50),
    log_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(100)
);

-- =========================
-- INSERT DEFAULT ADMIN
-- =========================
INSERT INTO users (username, password)
SELECT 'admin', 'admin123'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username='admin'
);


-- =========================
-- SAMPLE DATA (OPTIONAL)
-- =========================
INSERT INTO patients (name, age, email, doctor, appointment_date, slot, priority, status) VALUES
('Sayali', 21, 'sayali@gmail.com', 'Dentist', '2026-03-25', 'Morning', 'Normal', 'Pending'),
('Rahul', 30, 'rahul@gmail.com', 'Cardiologist', '2026-03-26', 'Evening', 'High Priority', 'Confirmed');