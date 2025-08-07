# Loopia.se Deployment System - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Scripts Overview](#scripts-overview)
5. [Usage Examples](#usage-examples)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Security Best Practices](#security-best-practices)

---

## Overview

The Loopia.se Deployment System is a Python-based automation tool designed specifically for Loopia.se hosting environments. It provides secure, efficient file transfer and deployment capabilities with support for multiple environments.

### Key Features
- **Multi-Environment Support**: Development, staging, and production
- **Protocol Support**: FTP, SFTP, and FTPS
- **Incremental Deployments**: Only upload changed files
- **Rollback Capability**: Quick rollback to previous versions
- **Backup System**: Automatic backups before deployments
- **Progress Tracking**: Real-time deployment progress
- **Error Handling**: Comprehensive error management

---

## Installation

### Prerequisites
- Python 3.7 or higher
- Access to Loopia.se hosting account
- FTP/SFTP credentials

### Setup Steps

1. **Clone or download the deployment system**
2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure your environments** (see Configuration section)

---

## Configuration

### Configuration File Location
```
deployment/config/deployment_config.yaml
```

### Configuration Structure

#### 1. Environment Settings

```yaml
environments:
  development:
    host: 's334.loopia.se'           # Your Loopia.se server
    username: 'your_username'        # Your Loopia.se username
    password: 'your_password'        # Your Loopia.se password
    remote_path: '/public_html/dev/' # Remote directory path
    protocol: 'ftp'                  # Connection protocol (ftp/sftp)
    port: 21                         # Port number (21 for FTP, 22 for SFTP)
    timeout: 30                      # Connection timeout in seconds
    
  staging:
    host: 's334.loopia.se'
    username: 'your_username'
    password: 'your_password'
    remote_path: '/public_html/staging/'
    protocol: 'sftp'
    port: 22
    timeout: 30
    
  production:
    host: 's334.loopia.se'
    username: 'your_username'
    password: 'your_password'
    remote_path: '/public_html/'
    protocol: 'sftp'
    port: 22
    timeout: 30
```

#### 2. Deployment Settings

```yaml
deployment:
  # Backup Configuration
  backup_enabled: true               # Enable automatic backups
  backup_path: '/backups/'          # Backup directory path
  max_backups: 5                    # Maximum number of backups to keep
  
  # File Exclusion Patterns
  exclude_patterns:
    - '*.log'                       # Exclude log files
    - '*.tmp'                       # Exclude temporary files
    - '.git/'                       # Exclude Git directory
    - 'node_modules/'               # Exclude Node.js modules
    - '__pycache__/'                # Exclude Python cache
    - '*.pyc'                       # Exclude Python compiled files
    - '.DS_Store'                   # Exclude macOS system files
    - 'Thumbs.db'                   # Exclude Windows system files
  
  # File Permissions
  file_permissions:
    directories: 755                 # Directory permissions (rwxr-xr-x)
    files: 644                       # File permissions (rw-r--r--)
    scripts: 755                     # Script permissions (rwxr-xr-x)
  
  # Transfer Settings
  transfer:
    parallel_uploads: 5              # Number of parallel file uploads
    chunk_size: 8192                # File transfer chunk size
    retry_attempts: 3               # Number of retry attempts
    retry_delay: 5                  # Delay between retries (seconds)
  
  # Logging Configuration
  logging:
    level: 'INFO'                   # Log level (DEBUG/INFO/WARNING/ERROR)
    file: 'logs/deployment.log'     # Log file path
    max_size: '10MB'                # Maximum log file size
    backup_count: 5                 # Number of log file backups
```

### Configuration Parameters Explained

#### Environment Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `host` | Loopia.se server hostname | `'s334.loopia.se'` |
| `username` | Your Loopia.se username | `'cust@yourdomain'` |
| `password` | Your Loopia.se password | `'your_password'` |
| `remote_path` | Remote directory path | `'/public_html/'` |
| `protocol` | Connection protocol | `'ftp'` or `'sftp'` |
| `port` | Connection port | `21` (FTP) or `22` (SFTP) |
| `timeout` | Connection timeout | `30` (seconds) |

#### Deployment Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backup_enabled` | Enable automatic backups | `true` |
| `backup_path` | Backup directory path | `'/backups/'` |
| `max_backups` | Maximum backup count | `5` |
| `parallel_uploads` | Parallel upload count | `5` |
| `chunk_size` | Transfer chunk size | `8192` bytes |
| `retry_attempts` | Retry attempts | `3` |
| `retry_delay` | Retry delay | `5` seconds |

---

## Scripts Overview

### 1. Main Deployment Script (`deploy.py`)

**Purpose**: Main command-line interface for deployment operations

**Key Features**:
- Environment selection
- Incremental deployment
- Dry run mode
- Configuration testing
- Rollback operations

**Usage**:
```bash
python3 deploy.py [options]
```

### 2. Deployment Manager (`scripts/deployment_manager.py`)

**Purpose**: Core deployment logic and file transfer operations

**Key Classes**:

#### `DeploymentManager`
- Main deployment orchestration
- Environment management
- File upload coordination
- Error handling and logging

#### `FileTransfer`
- FTP/SFTP connection management
- File upload/download operations
- Directory creation/deletion
- Permission management

#### `Logger`
- Comprehensive logging system
- Error tracking
- Performance monitoring

### 3. Test Scripts

#### `test_deployment.py`
- General functionality testing
- Configuration validation
- Connection testing

#### `test_single_file.py`
- Single file transfer testing
- Upload/delete operations
- Permission testing

#### `test_real_deployment.py`
- Full project deployment testing
- Multi-environment testing
- Real file transfer validation

---

## Usage Examples

### Basic Operations

#### 1. Test Configuration
```bash
# Test all environment connections
python3 deploy.py --test
```

#### 2. Deploy to Production
```bash
# Deploy all files to production
python3 deploy.py --environment production --source ./cms/ --remote /public_html/
```

#### 3. Incremental Deployment
```bash
# Deploy only changed files to staging
python3 deploy.py --environment staging --source ./cms/ --remote /public_html/staging/ --incremental
```

#### 4. Dry Run (Preview)
```bash
# Show what would be deployed without uploading
python3 deploy.py --environment production --source ./cms/ --remote /public_html/ --dry-run
```

#### 5. Rollback
```bash
# Rollback to previous version
python3 deploy.py --rollback --version 2024-01-15-14-30-00
```

### Advanced Operations

#### 1. Custom Configuration
```bash
# Use custom configuration file
python3 deploy.py --config ./my_config.yaml --environment production --source ./cms/ --remote /public_html/
```

#### 2. Verbose Output
```bash
# Enable detailed logging
python3 deploy.py --environment production --source ./cms/ --remote /public_html/ --verbose
```

#### 3. Test Single File
```bash
# Test single file upload
python3 test_single_file.py
```

#### 4. Real Deployment Test
```bash
# Test full deployment with real files
python3 test_real_deployment.py
```

---

## Advanced Features

### 1. Incremental Deployment

**How it works**:
- Compares local and remote file timestamps
- Only uploads files that have changed
- Skips files matching exclusion patterns
- Maintains deployment efficiency

**Benefits**:
- Faster deployments
- Reduced bandwidth usage
- Lower server load
- Quick updates

### 2. Backup System

**Automatic backups**:
- Creates backup before each deployment
- Timestamped backup directories
- Configurable backup retention
- Quick rollback capability

**Backup structure**:
```
/backups/
├── backup_2024-01-15_14-30-00/
├── backup_2024-01-15_15-45-30/
└── backup_2024-01-16_09-15-20/
```

### 3. Error Handling

**Comprehensive error management**:
- Connection failure recovery
- File transfer retry logic
- Graceful error reporting
- Detailed error logging

**Error types handled**:
- Network timeouts
- Authentication failures
- File permission errors
- Disk space issues
- Invalid file paths

### 4. Security Features

**Security measures**:
- Encrypted SFTP connections
- Secure credential storage
- Permission validation
- Access logging

**Best practices**:
- Use SFTP for production
- Secure credential management
- Regular security audits
- Access monitoring

---

## Troubleshooting

### Common Issues

#### 1. Connection Failures

**Symptoms**:
- "Connection failed: timed out"
- "Authentication failed"

**Solutions**:
```bash
# Check credentials
python3 deploy.py --test

# Verify server details
# Check firewall settings
# Test with different protocol (FTP vs SFTP)
```

#### 2. File Permission Errors

**Symptoms**:
- "Permission denied"
- "Cannot create directory"

**Solutions**:
```bash
# Check remote directory permissions
# Verify user permissions on server
# Use SFTP for better permission control
```

#### 3. Upload Failures

**Symptoms**:
- "Upload failed"
- "File not found"

**Solutions**:
```bash
# Check file paths
# Verify file existence
# Test with dry run first
python3 deploy.py --dry-run --environment production --source ./cms/ --remote /public_html/
```

### Debug Mode

**Enable verbose logging**:
```bash
python3 deploy.py --verbose --environment production --source ./cms/ --remote /public_html/
```

**Check log files**:
```bash
# View deployment logs
tail -f logs/deployment.log

# View error logs
tail -f logs/error.log
```

### Performance Optimization

**Optimization tips**:
- Use incremental deployments
- Increase parallel uploads
- Optimize chunk size
- Use SFTP for large files

**Configuration adjustments**:
```yaml
transfer:
  parallel_uploads: 10    # Increase for faster uploads
  chunk_size: 16384       # Increase for better performance
  retry_attempts: 5       # More retries for stability
```

---

## Security Best Practices

### 1. Credential Management

**Secure credential storage**:
```bash
# Use environment variables
export LOOPIA_USERNAME="your_username"
export LOOPIA_PASSWORD="your_password"

# Or use encrypted configuration files
# Never commit credentials to version control
```

### 2. Network Security

**Security measures**:
- Use SFTP for production environments
- Enable connection encryption
- Use strong passwords
- Regular credential rotation

### 3. Access Control

**Access management**:
- Limit deployment user permissions
- Use dedicated deployment accounts
- Monitor access logs
- Regular security audits

### 4. File Security

**File protection**:
- Validate file permissions
- Check file integrity
- Secure file transfers
- Backup verification

---

## File Structure

```
deployment/
├── deploy.py                    # Main deployment script
├── config/
│   └── deployment_config.yaml   # Configuration file
├── scripts/
│   └── deployment_manager.py    # Core deployment logic
├── templates/
│   └── deployment_log.html      # Results template
├── logs/
│   └── deployment.log          # Deployment logs
├── backups/
│   └── previous_versions/      # Backup storage
├── test_*.py                   # Test scripts
├── requirements.txt             # Python dependencies
├── README.md                   # Basic documentation
└── DEPLOYMENT_GUIDE.md         # This comprehensive guide
```

---

## Command Reference

### Main Script Options

| Option | Description | Example |
|--------|-------------|---------|
| `--environment, -e` | Target environment | `--environment production` |
| `--source, -s` | Source directory | `--source ./cms/` |
| `--remote, -r` | Remote directory | `--remote /public_html/` |
| `--config, -c` | Config file | `--config ./my_config.yaml` |
| `--incremental, -i` | Incremental deploy | `--incremental` |
| `--rollback` | Rollback mode | `--rollback` |
| `--version` | Rollback version | `--version 2024-01-15-14-30-00` |
| `--test` | Test configuration | `--test` |
| `--dry-run` | Preview mode | `--dry-run` |
| `--verbose, -v` | Verbose output | `--verbose` |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LOOPIA_USERNAME` | Loopia.se username | `export LOOPIA_USERNAME="your_username"` |
| `LOOPIA_PASSWORD` | Loopia.se password | `export LOOPIA_PASSWORD="your_password"` |
| `LOOPIA_HOST` | Loopia.se server | `export LOOPIA_HOST="s334.loopia.se"` |

---

## Support and Maintenance

### Regular Maintenance

**Recommended tasks**:
- Update dependencies monthly
- Review log files weekly
- Test configurations monthly
- Backup configuration files
- Monitor deployment performance

### Getting Help

**Troubleshooting steps**:
1. Check configuration file
2. Test connections
3. Review log files
4. Use dry run mode
5. Check server status

**Contact information**:
- Review this guide for common issues
- Check log files for detailed errors
- Test with different environments
- Verify server connectivity

---

This guide provides comprehensive information about the Loopia.se deployment system. For specific issues or questions, refer to the troubleshooting section or check the log files for detailed error information. 