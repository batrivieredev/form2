-- Store current state of foreign key checks
SET @FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS;

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Drop all tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS subsites;
DROP TABLE IF EXISTS forms;
DROP TABLE IF EXISTS form_responses;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS ticket_responses;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS alembic_version;

-- Restore foreign key checks to original state
SET FOREIGN_KEY_CHECKS = @FOREIGN_KEY_CHECKS;

-- Recreate the database
DROP DATABASE IF EXISTS form_db;
CREATE DATABASE form_db CHARACTER SET utf8mb4;

-- Switch to the database
USE form_db;

-- Set default collation for new tables
ALTER DATABASE form_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant permissions (adjust username and password as needed)
-- CREATE USER IF NOT EXISTS 'form_user'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON form_db.* TO 'form_user'@'localhost';
-- FLUSH PRIVILEGES;
