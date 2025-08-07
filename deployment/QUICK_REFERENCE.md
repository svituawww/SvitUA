# Loopia.se Deployment System - Quick Reference

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure Credentials
Edit `config/deployment_config.yaml`:
```yaml
environments:
  production:
    host: 's334.loopia.se'
    username: 'your_username'    # ← YOUR Loopia.se username
    password: 'your_password'    # ← YOUR Loopia.se password
    remote_path: '/public_html/'
    protocol: 'sftp'
```

### 3. Test Connection
```bash
python3 deploy.py --test
```

## 📋 Essential Commands

### Configuration Testing
```bash
# Test all environments
python3 deploy.py --test

# Test specific environment
python3 deploy.py --environment production --source ./test/ --remote /public_html/ --dry-run
```

### Deployment Operations
```bash
# Deploy to production
python3 deploy.py --environment production --source ./cms/ --remote /public_html/

# Incremental deployment
python3 deploy.py --environment staging --source ./cms/ --remote /public_html/staging/ --incremental

# Preview deployment (dry run)
python3 deploy.py --environment production --source ./cms/ --remote /public_html/ --dry-run
```

### Rollback Operations
```bash
# Rollback to previous version
python3 deploy.py --rollback --version 2024-01-15-14-30-00
```

### Testing Scripts
```bash
# Test single file upload
python3 test_single_file.py

# Test full deployment
python3 test_real_deployment.py
```

## ⚙️ Configuration Settings

### Environment Settings
| Setting | Description | Example |
|---------|-------------|---------|
| `host` | Loopia.se server | `'s334.loopia.se'` |
| `username` | Your username | `'cust@yourdomain'` |
| `password` | Your password | `'your_password'` |
| `remote_path` | Remote directory | `'/public_html/'` |
| `protocol` | Connection type | `'ftp'` or `'sftp'` |
| `port` | Connection port | `21` (FTP) or `22` (SFTP) |

### Deployment Settings
| Setting | Description | Default |
|---------|-------------|---------|
| `backup_enabled` | Auto backup | `true` |
| `parallel_uploads` | Upload speed | `5` |
| `retry_attempts` | Retry count | `3` |
| `exclude_patterns` | Skip files | `['*.log', '.git/']` |

## 🔧 Common Tasks

### Update Credentials
1. Edit `config/deployment_config.yaml`
2. Update username/password for each environment
3. Test with: `python3 deploy.py --test`

### Change Remote Path
```yaml
environments:
  production:
    remote_path: '/public_html/my-site/'  # ← Change this
```

### Exclude Files
```yaml
deployment:
  exclude_patterns:
    - '*.log'
    - '.git/'
    - 'node_modules/'
    - 'your-custom-pattern'  # ← Add your patterns
```

### Optimize Performance
```yaml
deployment:
  transfer:
    parallel_uploads: 10    # ← Increase for speed
    chunk_size: 16384      # ← Increase for large files
    retry_attempts: 5      # ← More retries
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connection
python3 deploy.py --test

# Check credentials
# Verify server details
# Test different protocol (FTP vs SFTP)
```

### Upload Failures
```bash
# Dry run first
python3 deploy.py --dry-run --environment production --source ../cms_php_custom/ --remote /public_html/

# Check file paths
# Verify file existence
# Check permissions
```

### Permission Errors
```bash
# Use SFTP for better permissions
# Check remote directory permissions
# Verify user permissions on server
```

## 📊 Monitoring

### View Logs
```bash
# Real-time deployment logs
tail -f logs/deployment.log

# Error logs
tail -f logs/error.log
```

### Verbose Output
```bash
# Detailed logging
python3 deploy.py --verbose --environment production --source ./cms_php_custom/ --remote /public_html/
```

## 🔒 Security

### Best Practices
- Use SFTP for production
- Secure credential storage
- Regular credential rotation
- Monitor access logs

### Environment Variables
```bash
export LOOPIA_USERNAME="your_username"
export LOOPIA_PASSWORD="your_password"
```

## 📁 File Structure
```
deployment/
├── deploy.py                    # Main script
├── config/deployment_config.yaml # Configuration
├── scripts/deployment_manager.py # Core logic
├── test_*.py                   # Test scripts
├── logs/                       # Log files
└── backups/                    # Backup storage
```

## 🆘 Help Commands

### Get Help
```bash
# Main script help
python3 deploy.py --help

# Test script help
python3 test_single_file.py --help
```

### Debug Mode
```bash
# Verbose logging
python3 deploy.py --verbose --environment production --source ./cms/ --remote /public_html/

# Check logs
tail -f logs/deployment.log
```

---

**Need more help?** See the full `DEPLOYMENT_GUIDE.md` for comprehensive documentation. 