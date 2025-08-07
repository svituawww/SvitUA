-- Setup Local Database for SvitUA Custom CMS
-- This script creates the database and user for local development

-- Create database
CREATE DATABASE IF NOT EXISTS svitua_cms 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create user for the CMS
CREATE USER IF NOT EXISTS 'svitua_user'@'localhost' 
IDENTIFIED BY 'svitua_password_2025';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON svitua_cms.* TO 'svitua_user'@'localhost';

-- Grant additional privileges for development
GRANT CREATE, DROP, ALTER, INDEX, REFERENCES ON svitua_cms.* TO 'svitua_user'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show created databases
SHOW DATABASES;

-- Show users
SELECT User, Host FROM mysql.user WHERE User = 'svitua_user';

-- Use the database
USE svitua_cms;

-- Create tables for the CMS
CREATE TABLE IF NOT EXISTS pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    slug VARCHAR(255) UNIQUE,
    meta_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255),
    file_size INT,
    mime_type VARCHAR(100),
    upload_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert some default settings
INSERT INTO settings (setting_key, setting_value) VALUES
('site_name', 'SvitUA Local Development'),
('site_description', 'Custom CMS - Local Development'),
('site_url', 'http://localhost'),
('version', '1.0.0'),
('environment', 'local')
ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);

-- Insert a sample page
INSERT INTO pages (title, content, slug, meta_description) VALUES
('Welcome to SvitUA', '<h1>Welcome to SvitUA</h1><p>Your custom CMS is running locally!</p>', 'home', 'Welcome to SvitUA - Custom Content Management System')
ON DUPLICATE KEY UPDATE content = VALUES(content);

-- Show tables
SHOW TABLES;

-- Show table structure
DESCRIBE pages;
DESCRIBE images;
DESCRIBE settings;

-- Show sample data
SELECT * FROM pages;
SELECT * FROM settings; 