# Loopia.se Deployment Automation

A comprehensive Python-based deployment automation system for Loopia.se hosting environments.

## Features

- **Multi-Environment Support**: Development, staging, and production environments
- **Protocol Support**: FTP, SFTP, and FTPS connections
- **Incremental Deployments**: Only upload changed files
- **Rollback Capability**: Quick rollback to previous versions
- **Backup System**: Automatic backups before deployments
- **Progress Tracking**: Real-time deployment progress
- **Error Handling**: Comprehensive error management and recovery
- **Security**: Encrypted credentials and secure connections

## Installation

1. **Clone or download the deployment system**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environments**:
   Edit `config/deployment_config.yaml` with your Loopia.se credentials and paths.

## Configuration

### Environment Setup

Edit `config/deployment_config.yaml`:

```yaml
environments:
  development:
    host: 's334.loopia.se'
    username: 'your_username'
    password: 'your_password'
    remote_path: '/public_html/dev/'
    protocol: 'ftp'
    
  production:
    host: 's334.loopia.se'
    username: 'your_username'
    password: 'your_password'
    remote_path: '/public_html/'
    protocol: 'sftp'
```

### Deployment Settings

```yaml
deployment:
  backup_enabled: true
  backup_path: '/backups/'
  max_backups: 5
  exclude_patterns:
    - '*.log'
    - '*.tmp'
    - '.git/'
    - 'node_modules/'
  
  file_permissions:
    directories: 755
    files: 644
    scripts: 755
```

## Usage

### Basic Deployment

Deploy to production:
```bash
python deploy.py --environment production --source ./cms/ --remote /public_html/
```

Deploy to staging:
```bash
python deploy.py --environment staging --source ./cms/ --remote /public_html/staging/
```

### Incremental Deployment

Only upload changed files:
```bash
python deploy.py --environment production --source ./cms/ --remote /public_html/ --incremental
```

### Dry Run

See what would be deployed without actually uploading:
```bash
python deploy.py --environment production --source ./cms/ --remote /public_html/ --dry-run
```

### Test Configuration

Test connections and configuration:
```bash
python deploy.py --test
```

### Rollback

Rollback to a previous version:
```bash
python deploy.py --rollback --version 2024-01-15-14-30-00
```

### Custom Configuration

Use a custom configuration file:
```bash
python deploy.py --config ./my_config.yaml --environment production --source ./cms/ --remote /public_html/
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--environment, -e` | Target environment (development/staging/production) |
| `--source, -s` | Source directory to deploy |
| `--remote, -r` | Remote directory path |
| `--config, -c` | Configuration file path |
| `--incremental, -i` | Perform incremental deployment |
| `--rollback` | Rollback to previous version |
| `--version` | Version to rollback to |
| `--test` | Test configuration and connections |
| `--dry-run` | Show what would be deployed |
| `--verbose, -v` | Verbose output |

## File Structure

```
deployment/
├── deploy.py                 # Main deployment script
├── config/
│   └── deployment_config.yaml # Environment configurations
├── scripts/
│   └── deployment_manager.py # Core deployment class
├── templates/
│   └── deployment_log.html   # Results display template
├── logs/
│   └── deployment.log        # Deployment logs
├── backups/
│   └── previous_versions/    # Backup storage
└── requirements.txt          # Python dependencies
```

## Security Features

- **Encrypted Credentials**: Secure storage of sensitive information
- **SSH Key Authentication**: Support for key-based authentication
- **Connection Encryption**: SFTP/FTPS support for secure transfers
- **Access Logging**: Track all deployment activities
- **Permission Validation**: Verify file permissions

## Error Handling

- **Connection Failures**: Automatic retry with exponential backoff
- **File Conflicts**: Handle file permission issues gracefully
- **Disk Space**: Check available space before upload
- **Timeout Handling**: Configurable timeouts for operations
- **Rollback on Failure**: Automatic rollback if deployment fails

## Performance Optimizations

- **Connection Pooling**: Reuse connections efficiently
- **Parallel Processing**: Multiple file transfers simultaneously
- **Compression**: Compress files during transfer
- **Caching**: Cache directory listings
- **Bandwidth Management**: Throttle transfers if needed

## Integration Capabilities

- **CI/CD Integration**: Hook into continuous deployment pipelines
- **Webhook Support**: Notify external services
- **Email Notifications**: Send deployment reports
- **Slack/Discord**: Real-time deployment notifications
- **Monitoring Integration**: Connect to monitoring systems

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify credentials in configuration
   - Check firewall settings
   - Ensure correct protocol (FTP/SFTP)

2. **Permission Denied**
   - Verify remote directory permissions
   - Check file ownership
   - Ensure correct file permissions

3. **Upload Timeout**
   - Increase timeout in configuration
   - Check network stability
   - Reduce file size or use compression

### Logs

Check deployment logs in `logs/deployment.log` for detailed error information.

## Support

For issues and questions:
1. Check the logs in `logs/deployment.log`
2. Test configuration with `--test` flag
3. Use `--dry-run` to preview deployments
4. Review configuration file syntax

## License

This deployment automation system is provided as-is for use with Loopia.se hosting environments. 