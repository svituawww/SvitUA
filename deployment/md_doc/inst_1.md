
<!-- PRESERVE begin id_part1 -->

## Database Testing Script for Loopia.se Hosting

### Objective
Create comprehensive PHP testing scripts in the `cms_php_custom` directory to verify MariaDB connectivity and perform essential database operations on Loopia.se hosting environment.

### Database Connection Parameters
```php
$host = 's334.loopia.se';
$user = 'cust@s379899';       // Use full user ID from Loopia
$password = 'hfrn9q64K2DBbuR'; // Must match what's in Loopia
$dbname = 'svitua_se_db_2';
```

### File Structure
```
cms_php_custom/
├── config/
│   ├── database_config.php    # Database connection configuration
│   └── config.php            # General application settings
├── includes/
│   ├── DatabaseTester.php    # Main database testing class
│   ├── ConnectionManager.php # Database connection management
│   └── Logger.php           # Logging functionality
├── tests/
│   ├── connection_test.php   # Database connection testing
│   ├── table_operations.php  # Table creation and operations
│   ├── data_operations.php   # CRUD operations testing
│   └── performance_test.php  # Database performance testing
├── logs/
│   ├── database_tests.log    # Test execution logs
│   └── errors.log           # Error logs
├── templates/
│   └── test_results.html    # Results display template
└── index_dbtest.php                # Main entry point
```

### Script Requirements

#### **1. Connection Testing (connection_test.php)**
- **Basic Connectivity**: Test database connection with provided credentials
- **Error Handling**: Display detailed connection errors and status messages
- **Timeout Testing**: Test connection timeout scenarios
- **Connection Pooling**: Test multiple connection attempts
- **SSL/TLS Support**: Test secure connection options
- **Connection Status**: Display server version and connection info

#### **2. Table Operations (table_operations.php)**
- **Table Creation**: Create "Test_Table1" with comprehensive structure
- **Schema Validation**: Verify table structure and constraints
- **Index Testing**: Test primary key and unique constraints
- **Data Type Testing**: Test all MariaDB data types
- **Table Cleanup**: Proper cleanup of test tables

#### **3. Data Operations (data_operations.php)**
- **INSERT Operations**: Add test records with various data types
- **SELECT Operations**: Query data with different conditions
- **UPDATE Operations**: Modify existing records
- **DELETE Operations**: Remove test data with proper cleanup
- **Transaction Testing**: Test ACID properties
- **Prepared Statements**: Test SQL injection prevention

#### **4. Performance Testing (performance_test.php)**
- **Query Performance**: Measure query execution times
- **Connection Speed**: Test connection establishment time
- **Memory Usage**: Monitor memory consumption
- **Concurrent Connections**: Test multiple simultaneous connections
- **Load Testing**: Simulate high database load

### Database Schema for Testing

#### **Test_Table1 Structure:**
```sql
CREATE TABLE Test_Table1 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive', 'pending') DEFAULT 'active',
    test_value DECIMAL(10,2) DEFAULT 0.00,
    is_deleted BOOLEAN DEFAULT FALSE,
    metadata JSON,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### **Sample Test Data:**
```php
$test_records = [
    [
        'name' => 'Test User 1',
        'email' => 'test1@example.com',
        'description' => 'First test record',
        'status' => 'active',
        'test_value' => 100.50,
        'metadata' => json_encode(['category' => 'test', 'priority' => 'high'])
    ],
    [
        'name' => 'Test User 2',
        'email' => 'test2@example.com',
        'description' => 'Second test record with special chars: éñü',
        'status' => 'pending',
        'test_value' => 250.75,
        'metadata' => json_encode(['category' => 'demo', 'priority' => 'medium'])
    ],
    [
        'name' => 'Test User 3',
        'email' => 'test3@example.com',
        'description' => 'Third test record with unicode: 🚀🌟',
        'status' => 'inactive',
        'test_value' => 999.99,
        'metadata' => json_encode(['category' => 'production', 'priority' => 'low'])
    ]
];
```

### Implementation Classes

#### **DatabaseTester Class:**
```php
class DatabaseTester {
    private $pdo;
    private $logger;
    
    public function __construct($config) {
        $this->logger = new Logger();
        $this->connect($config);
    }
    
    public function testConnection() {
        // Test basic connectivity
    }
    
    public function createTestTable() {
        // Create Test_Table1 with full structure
    }
    
    public function insertTestData() {
        // Insert sample records
    }
    
    public function testCRUDOperations() {
        // Test Create, Read, Update, Delete
    }
    
    public function testPerformance() {
        // Performance testing
    }
    
    public function cleanup() {
        // Clean up test data
    }
    
    public function generateReport() {
        // Generate comprehensive test report
    }
}
```

#### **ConnectionManager Class:**
```php
class ConnectionManager {
    private $config;
    private $connections = [];
    
    public function getConnection() {
        // Get database connection with pooling
    }
    
    public function testConnection($host, $user, $password, $dbname) {
        // Test connection with error handling
    }
    
    public function getServerInfo() {
        // Get MariaDB server information
    }
}
```

### Test Execution Flow

#### **1. Connection Test:**
- Test basic connectivity
- Display connection parameters (masked)
- Show server version and capabilities
- Test connection timeout scenarios

#### **2. Table Operations:**
- Create Test_Table1 with full schema
- Verify table structure
- Test constraints and indexes
- Validate data types

#### **3. Data Operations:**
- Insert test records
- Perform SELECT queries
- Test UPDATE operations
- Test DELETE operations
- Verify data integrity

#### **4. Performance Test:**
- Measure query execution times
- Test concurrent connections
- Monitor resource usage
- Generate performance report

#### **5. Cleanup:**
- Remove test data
- Drop test tables
- Verify cleanup completion

### Expected Output Format

#### **Console Output:**
```
=== Database Connection Test ===
✓ Connected to MariaDB server: s334.loopia.se
✓ Server version: 10.5.15-MariaDB
✓ Database: svitua_se_db_2
✓ Connection time: 0.045s

=== Table Operations Test ===
✓ Created table: Test_Table1
✓ Verified table structure
✓ All constraints working

=== Data Operations Test ===
✓ Inserted 3 test records
✓ SELECT operations: 3 queries successful
✓ UPDATE operations: 2 records updated
✓ DELETE operations: 1 record deleted

=== Performance Test ===
✓ Average query time: 0.012s
✓ Connection pool: 5 connections tested
✓ Memory usage: 2.5MB

=== Test Summary ===
✓ All tests passed
✓ Database ready for production use
```

#### **Log File Output:**
```
2024-01-15 14:30:00 - INFO - Database connection test started
2024-01-15 14:30:01 - INFO - Connected to MariaDB server successfully
2024-01-15 14:30:02 - INFO - Test_Table1 created successfully
2024-01-15 14:30:03 - INFO - 3 test records inserted
2024-01-15 14:30:04 - INFO - All CRUD operations completed successfully
2024-01-15 14:30:05 - INFO - Performance test completed
2024-01-15 14:30:06 - INFO - Cleanup completed successfully
```

### Security Considerations
- **Credential Protection**: Store credentials in separate config file
- **Error Handling**: Don't expose sensitive information in error messages
- **SQL Injection Prevention**: Use prepared statements exclusively
- **Connection Security**: Test SSL/TLS connections
- **Access Control**: Verify database user permissions

### Error Handling
- **Connection Failures**: Graceful handling of connection errors
- **Query Errors**: Detailed error logging without exposing sensitive data
- **Timeout Handling**: Proper timeout configuration and handling
- **Resource Cleanup**: Ensure connections are properly closed

### Performance Optimization
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Use efficient queries and indexes
- **Memory Management**: Monitor and control memory usage
- **Timeout Configuration**: Set appropriate timeouts

<!-- PRESERVE end id_part1 -->











<!-- PRESERVE begin id_part2 -->

## Deployment Location and Parameter Verification

### **Where to Locate the Database Testing System**

#### **1. Recommended Location Structure:**
```
Loopia.se Hosting Structure:
├── public_html/                    # Main web root
│   ├── index.php                  # Main website
│   ├── cms_php_custom/           # Database testing system
│   │   ├── index_dbtest.php      # Main entry point
│   │   ├── config/               # Configuration files
│   │   ├── includes/             # PHP classes
│   │   ├── logs/                 # Log files
│   │   └── templates/            # HTML templates
│   └── other_website_files/      # Other website files
```

#### **2. Access URLs:**
```
Browser Access:
- Main website: https://yourdomain.com/
- Database tests: https://yourdomain.com/cms_php_custom/index_dbtest.php
- Specific tests: https://yourdomain.com/cms_php_custom/index_dbtest.php?test=connection
```

#### **3. How to Check Your Right Location:**

**Method 1: File Structure Verification**
```bash
# Check current directory structure
ls -la cms_php_custom/
# Should show: config/, includes/, logs/, templates/, index_dbtest.php, README.md

# Verify all files exist
find cms_php_custom -name "*.php" -o -name "*.html" -o -name "*.md"
# Should list all 8 files we created
```

**Method 2: Path Verification**
```bash
# Check absolute path
pwd
# Should be: /path/to/your/project

# Check relative to deployment directory
ls -la ../cms_php_custom/
# Should show the database testing system files
```

**Method 3: Deployment Script Verification**
```bash
# Test deployment parameters
python3 deploy.py --test
# Should show configuration and connection status
```

### **Deployment Command Analysis**

#### **Your Command:**
```bash
python3 deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Parameter Verification:**

✅ **`--dry-run`**: Correct - Safe testing without actual deployment
✅ **`--environment production`**: Correct - Uses production credentials
✅ **`--source ./cms_php_custom/`**: Correct - Points to our database testing system
✅ **`--remote /public_html/`**: Correct - Deploys to web root

#### **Expected Result:**
```
Deployment Simulation (Dry Run)
==============================
Source: ./cms_php_custom/
Destination: /public_html/
Environment: production
Files to upload:
- config/database_config.php
- config/config.php
- includes/Logger.php
- includes/ConnectionManager.php
- includes/DatabaseTester.php
- index_dbtest.php
- templates/test_results.html
- README.md
```

### **Recommended Deployment Steps:**

#### **Step 1: Verify Current Location**
```bash
# Check you're in the right directory
pwd
# Should be: /Users/nirsixadmin/Desktop/SvitUA

# Verify cms_php_custom exists
ls -la cms_php_custom/
```

#### **Step 2: Test Deployment Parameters**
```bash
# Test with dry-run first
python3 deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Step 3: Actual Deployment**
```bash
# Remove --dry-run for actual deployment
python3 deploy.py --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Step 4: Verify Deployment**
```bash
# Test the deployed system
curl https://yourdomain.com/cms_php_custom/index_dbtest.php
```

### **Alternative Deployment Options:**

#### **Option 1: Deploy to Subdirectory**
```bash
python3 deploy.py --environment production --source ./cms_php_custom/ --remote /public_html/db-tests/
# Access: https://yourdomain.com/db-tests/index_dbtest.php
```

#### **Option 2: Deploy to Development Environment**
```bash
python3 deploy.py --environment development --source ./cms_php_custom/ --remote /public_html/dev/
# Access: https://yourdomain.com/dev/index_dbtest.php
```

#### **Option 3: Deploy with Custom Path**
```bash
python3 deploy.py --environment production --source ./cms_php_custom/ --remote /public_html/testing/
# Access: https://yourdomain.com/testing/index_dbtest.php
```

### **Post-Deployment Verification:**

#### **1. File Access Test:**
```bash
# Test if files are accessible
curl -I https://yourdomain.com/cms_php_custom/index_dbtest.php
# Should return: HTTP/1.1 200 OK
```

#### **2. Database Connection Test:**
```bash
# Test database connectivity
curl https://yourdomain.com/cms_php_custom/index_dbtest.php?test=connection
# Should show connection success
```

#### **3. Full System Test:**
```bash
# Test complete system
curl https://yourdomain.com/cms_php_custom/index_dbtest.php?test=all
# Should run all tests and show results
```

### **Security Considerations:**

#### **1. File Permissions:**
```bash
# Ensure logs directory is writable
chmod 755 cms_php_custom/logs/
chmod 644 cms_php_custom/logs/*.log
```

#### **2. Access Control:**
```bash
# Consider adding .htaccess for protection
echo "Order Deny,Allow" > cms_php_custom/.htaccess
echo "Deny from all" >> cms_php_custom/.htaccess
echo "Allow from your-ip-address" >> cms_php_custom/.htaccess
```

#### **3. Credential Security:**
- Database credentials are in `config/database_config.php`
- Ensure this file is not publicly accessible
- Consider moving credentials to environment variables

### **Troubleshooting:**

#### **If Deployment Fails:**
1. **Check Path**: Verify `./cms_php_custom/` exists
2. **Check Permissions**: Ensure files are readable
3. **Check Connection**: Verify FTP credentials work
4. **Check Space**: Ensure server has enough disk space

#### **If Access Fails:**
1. **Check URL**: Verify the correct domain and path
2. **Check Permissions**: Ensure PHP files are executable
3. **Check Logs**: Check server error logs
4. **Check Database**: Verify database credentials work

### **Final Answer:**

**Your deployment command is correct!** All parameters are properly set:

- ✅ **Location**: `./cms_php_custom/` (relative to current directory)
- ✅ **Destination**: `/public_html/` (web root on Loopia.se)
- ✅ **Environment**: `production` (uses production credentials)
- ✅ **Safety**: `--dry-run` (tests without actual deployment)

**Recommended next steps:**
1. Run the dry-run command to verify
2. Remove `--dry-run` for actual deployment
3. Test the deployed system via browser
4. Verify database connectivity works

<!-- PRESERVE end id_part2 -->






<!-- PRESERVE begin id_part3 -->

## Deployment Location Analysis

### **Current Directory Structure:**
```
/Users/nirsixadmin/Desktop/SvitUA/
├── deployment/
│   ├── deploy.py                    # Deployment script
│   ├── config/
│   │   └── deployment_config.yaml   # Deployment configuration
│   └── scripts/
│       └── deployment_manager.py    # Deployment manager
└── cms_php_custom/                 # Database testing system
    ├── index_dbtest.php
    ├── config/
    ├── includes/
    ├── logs/
    └── templates/
```

### **Correct Deployment Location:**

#### **Option 1: Run from SvitUA Root Directory (Recommended)**
```bash
# Navigate to the root directory
cd /Users/nirsixadmin/Desktop/SvitUA

# Verify current location
pwd
# Should show: /Users/nirsixadmin/Desktop/SvitUA

# Run deployment command
python3 deployment/deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Option 2: Run from Deployment Directory**
```bash
# Navigate to deployment directory
cd /Users/nirsixadmin/Desktop/SvitUA/deployment

# Verify current location
pwd
# Should show: /Users/nirsixadmin/Desktop/SvitUA/deployment

# Run deployment command with relative path
python3 deploy.py --dry-run --environment production --source ../cms_php_custom/ --remote /public_html/
```

### **Recommended Approach:**

#### **Step 1: Navigate to Root Directory**
```bash
cd /Users/nirsixadmin/Desktop/SvitUA
```

#### **Step 2: Verify Structure**
```bash
# Check if both directories exist
ls -la deployment/
ls -la cms_php_custom/

# Should show:
# deployment/ - directory with deploy.py
# cms_php_custom/ - directory with database testing system
```

#### **Step 3: Run Deployment**
```bash
# From root directory
python3 deployment/deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

### **Why Root Directory is Recommended:**

#### **1. Path Clarity:**
- **Source**: `./cms_php_custom/` (clear relative path)
- **Script**: `deployment/deploy.py` (explicit path)
- **No confusion**: All paths are relative to project root

#### **2. Configuration Access:**
- Deployment config is in `deployment/config/`
- Database testing system is in `cms_php_custom/`
- Both accessible from root directory

#### **3. Future Deployments:**
- Easy to deploy other projects
- Consistent directory structure
- Clear project organization

### **Alternative Locations (Not Recommended):**

#### **❌ From Desktop:**
```bash
cd /Users/nirsixadmin/Desktop
python3 SvitUA/deployment/deploy.py --source ./SvitUA/cms_php_custom/ --remote /public_html/
# Too complex paths, error-prone
```

#### **❌ From Home Directory:**
```bash
cd ~
python3 Desktop/SvitUA/deployment/deploy.py --source ./Desktop/SvitUA/cms_php_custom/ --remote /public_html/
# Very long paths, hard to maintain
```

### **Verification Commands:**

#### **Check Current Location:**
```bash
pwd
# Should be: /Users/nirsixadmin/Desktop/SvitUA
```

#### **Verify Files Exist:**
```bash
# Check deployment script
ls -la deployment/deploy.py
# Should show: -rw-r--r-- ... deploy.py

# Check database testing system
ls -la cms_php_custom/index_dbtest.php
# Should show: -rw-r--r-- ... index_dbtest.php
```

#### **Test Deployment Command:**
```bash
# Test with dry-run
python3 deployment/deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/

# Expected output:
# Deployment Simulation (Dry Run)
# Source: ./cms_php_custom/
# Destination: /public_html/
# Files to upload: [list of files]
```

### **Complete Deployment Workflow:**

#### **Step 1: Navigate to Correct Directory**
```bash
cd /Users/nirsixadmin/Desktop/SvitUA
```

#### **Step 2: Verify Environment**
```bash
# Check current directory
pwd
# Should show: /Users/nirsixadmin/Desktop/SvitUA

# List contents
ls -la
# Should show: deployment/ and cms_php_custom/ directories
```

#### **Step 3: Test Deployment**
```bash
# Run dry-run first
python3 deployment/deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Step 4: Actual Deployment**
```bash
# Remove --dry-run for actual deployment
python3 deployment/deploy.py --environment production --source ./cms_php_custom/ --remote /public_html/
```

#### **Step 5: Verify Deployment**
```bash
# Test the deployed system
curl https://yourdomain.com/cms_php_custom/index_dbtest.php
```

### **Troubleshooting:**

#### **If "deploy.py not found":**
```bash
# Check if you're in the right directory
pwd
# Should be: /Users/nirsixadmin/Desktop/SvitUA

# Check if deploy.py exists
ls -la deployment/deploy.py
```

#### **If "cms_php_custom not found":**
```bash
# Check if database testing system exists
ls -la cms_php_custom/
# Should show: index_dbtest.php, config/, includes/, etc.
```

#### **If "Permission denied":**
```bash
# Make deploy.py executable
chmod +x deployment/deploy.py

# Check file permissions
ls -la deployment/deploy.py
```

### **Final Answer:**

**Your current location should be:**
```bash
cd /Users/nirsixadmin/Desktop/SvitUA
```

**Then run:**
```bash
python3 deployment/deploy.py --dry-run --environment production --source ./cms_php_custom/ --remote /public_html/
```

**This ensures:**
- ✅ **Correct paths**: All relative paths work properly
- ✅ **Access to both systems**: Deployment script and database testing system
- ✅ **Clear structure**: Easy to understand and maintain
- ✅ **Future deployments**: Consistent approach for other projects

<!-- PRESERVE end id_part3 -->