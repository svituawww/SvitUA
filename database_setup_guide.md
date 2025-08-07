# 🗄️ Loopia.se Database Setup Guide

## 📊 **Research Results Summary**

Based on your `loopia_research_results.json`, your Loopia.se hosting has:

### **✅ Available Database Extensions:**
- **PDO MySQL**: ✅ Available (PHP 8.3.23)
- **MySQLi**: ✅ Available (PHP 8.3.23)
- **MySQL**: ❌ Not available (deprecated)

### **⚠️ Current Status:**
- **Connection**: Failed ("No such file or directory")
- **Database**: Not yet created/configured

## 🚀 **Step 1: Create Database in Loopia Customer Zone**

### **Access Loopia Customer Zone:**
1. Go to: https://customerzone.loopia.se/
2. **Login** with your Loopia.se account
3. **Navigate** to your hosting package

### **Create MariaDB Database:**
1. **Find** "Databases" or "MariaDB" section
2. **Click** "Create Database"
3. **Enter details**:
   - **Database Name**: `svitua_cms` (or your preferred name)
   - **Username**: `svitua_user` (or your preferred username)
   - **Password**: Generate a strong password
4. **Save** the credentials

## 🔧 **Step 2: Get Database Connection Details**

### **From Loopia Customer Zone:**
- **Database Host**: Usually `localhost` or provided hostname
- **Database Name**: The name you created
- **Username**: The username you created
- **Password**: The password you set
- **Port**: Usually 3306 (default)

### **Common Loopia.se Database Settings:**
```php
$host = 'localhost';  // or provided hostname
$dbname = 'svitua_cms';
$username = 'svitua_user';
$password = 'your_password';
$port = 3306;
```

## 📝 **Step 3: Create Database Configuration File**

Create `config/database.php`:

```php
<?php
// Database Configuration for Loopia.se
return [
    'host' => 'localhost',  // or your Loopia.se database host
    'dbname' => 'svitua_cms',
    'username' => 'svitua_user',
    'password' => 'your_password',
    'port' => 3306,
    'charset' => 'utf8mb4',
    'options' => [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]
];
?>
```

## 🧪 **Step 4: Test Database Connection**

Create `test_database.php`:

```php
<?php
require_once 'config/database.php';

try {
    $config = require 'config/database.php';
    
    $dsn = "mysql:host={$config['host']};dbname={$config['dbname']};charset={$config['charset']}";
    $pdo = new PDO($dsn, $config['username'], $config['password'], $config['options']);
    
    echo "✅ Database connection successful!\n";
    echo "Server version: " . $pdo->getAttribute(PDO::ATTR_SERVER_VERSION) . "\n";
    
} catch (PDOException $e) {
    echo "❌ Database connection failed: " . $e->getMessage() . "\n";
}
?>
```

## 📊 **Step 5: Create Database Tables**

Create `setup_database.php`:

```php
<?php
require_once 'config/database.php';

try {
    $config = require 'config/database.php';
    $dsn = "mysql:host={$config['host']};dbname={$config['dbname']};charset={$config['charset']}";
    $pdo = new PDO($dsn, $config['username'], $config['password'], $config['options']);
    
    // Create pages table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS pages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            slug VARCHAR(255) UNIQUE,
            meta_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ");
    
    // Create images table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255),
            file_size INT,
            mime_type VARCHAR(100),
            upload_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ");
    
    // Create settings table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ");
    
    echo "✅ Database tables created successfully!\n";
    
} catch (PDOException $e) {
    echo "❌ Database setup failed: " . $e->getMessage() . "\n";
}
?>
```

## 🔍 **Step 6: Verify Database Setup**

### **Upload and Test:**
1. **Upload** `test_database.php` to your Loopia.se hosting
2. **Access** via browser: `https://your-domain.loopia.se/test_database.php`
3. **Check** for connection success
4. **Run** `setup_database.php` to create tables

## 📋 **Database Credentials Template**

Save this as `database_credentials.txt` (keep secure):

```
Loopia.se Database Credentials
==============================

Host: localhost (or provided hostname)
Database: svitua_cms
Username: svitua_user
Password: your_secure_password
Port: 3306

Connection String:
mysql:host=localhost;dbname=svitua_cms;charset=utf8mb4

PDO Connection:
$pdo = new PDO($dsn, $username, $password, $options);
```

## 🚨 **Security Notes**

1. **Keep credentials secure** - don't commit to version control
2. **Use strong passwords** for database access
3. **Limit database user permissions** to only what's needed
4. **Regular backups** of your database
5. **Monitor database usage** in Loopia Customer Zone

## 🎯 **Next Steps**

1. **Create database** in Loopia Customer Zone
2. **Get connection details** from Loopia
3. **Create config file** with your credentials
4. **Test connection** with test script
5. **Create tables** with setup script
6. **Integrate** with your CMS system

Your hosting environment is excellent - just need to set up the database! 🚀 