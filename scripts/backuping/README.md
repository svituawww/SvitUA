# SVIT UA Backup System

A Python-based CLI backup system that can backup specified directories based on configuration, create compressed archives, and maintain a detailed backup history with commit messages and file integrity verification.

## Features

- **Configuration-Driven**: YAML-based configuration for backup targets and settings
- **Git Integration**: Automatic commit hash and message extraction
- **Compression**: ZIP and TAR.GZ archive support with configurable compression levels
- **File Integrity**: SHA256 hash verification for all files
- **Metadata Tracking**: Detailed backup history with file counts, sizes, and compression ratios
- **Exclusion Patterns**: Flexible file and directory exclusion rules
- **Retention Management**: Automatic cleanup of old backups
- **Restore Functionality**: Extract backups to specified locations
- **Verification**: Comprehensive backup integrity checking

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Make CLI Executable** (optional):
   ```bash
   chmod +x cli.py
   ```

## Configuration

The backup system uses a YAML configuration file (`backup_config.yaml`) to define:

### Source Directories
```yaml
source_directories:
  - path: "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io"
    name: "website"
    exclude_patterns:
      - "*.log"
      - "node_modules/"
      - ".git/"
    exclude_dir:
      - "uploads1"
      - "uploads_old"
```

### Backup Settings
```yaml
backup_destination:
  base_path: "/Users/nirsixadmin/Desktop/SvitUA/backups/"
  naming_pattern: "{timestamp}_{commit_hash}_{name}"

compression:
  format: "zip"  # or tar.gz
  compression_level: 6

metadata:
  include_git_info: true
  include_file_hashes: true
  include_size_info: true
```

## Usage

### Basic Commands

#### Create Backup
```bash
# Create backup with auto commit message
python3 cli.py --config backup_config.yaml --backup

# Create backup with custom commit message
python3 cli.py --config backup_config.yaml --backup --message "Updated website design"
```

#### List Backups
```bash
# List all available backups
python3 cli.py --config backup_config.yaml --list
```

#### Verify Backup
```bash
# Verify specific backup integrity
python3 cli.py --config backup_config.yaml --verify 2025-01-15_14-30-25_a1b2c3d
```

#### Get Backup Information
```bash
# Get detailed information about a specific backup
python3 cli.py --config backup_config.yaml --info 2025-01-15_14-30-25_a1b2c3d
```

#### Restore Backup
```bash
# Restore backup to specified path
python3 cli.py --config backup_config.yaml --restore 2025-01-15_14-30-25_a1b2c3d --restore-path ./restored
```

#### Cleanup Old Backups
```bash
# Remove old backups (keep only 5 most recent)
python3 cli.py --config backup_config.yaml --cleanup --max-backups 5
```

### Advanced Usage

#### Verbose Output
```bash
# Enable verbose output for debugging
python3 cli.py --config backup_config.yaml --backup --verbose
```

#### Custom Restore Path
```bash
# Restore to custom directory
python3 cli.py --config backup_config.yaml --restore 2025-01-15_14-30-25_a1b2c3d --restore-path /path/to/restore
```

## File Structure

```
scripts/backuping/
├── cli.py                    # Command line interface
├── backup_manager.py         # Main backup manager class
├── backup_config.yaml        # Configuration file
├── backup_utils.py          # Utility functions
├── git_integration.py       # Git-related functions
├── compression.py           # Compression utilities
├── verification.py          # Integrity verification
├── requirements.txt         # Python dependencies
└── README.md               # This file

/Users/nirsixadmin/Desktop/SvitUA/backups/
├── backup_history.json      # Backup metadata
├── 2025-01-15_14-30-25_a1b2c3d_website.zip
├── 2025-01-15_14-30-25_a1b2c3d_parser.zip
└── 2025-01-15_14-30-25_a1b2c3d_deployment.zip
```

## Backup Naming Convention

Backups are named using the pattern: `{timestamp}_{commit_hash}_{name}.{format}`

Example: `2025-01-15_14-30-25_a1b2c3d_website.zip`

- **timestamp**: ISO format timestamp (YYYY-MM-DD_HH-MM-SS)
- **commit_hash**: Git commit hash (short format)
- **name**: Backup name from configuration
- **format**: Archive format (zip, tar.gz)

## Metadata Structure

Each backup creates metadata in `backup_history.json`:

```json
{
  "backup_id": "2025-01-15_14-30-25_a1b2c3d",
  "timestamp": "2025-01-15T14:30:25Z",
  "commit_hash": "a1b2c3d",
  "commit_message": "Updated website content",
  "git_status": {
    "is_repository": true,
    "commit_hash": "a1b2c3d",
    "commit_message": "Updated website content",
    "branch": "master",
    "has_changes": false
  },
  "backups": [
    {
      "name": "website",
      "source_path": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io",
      "archive_path": "/Users/nirsixadmin/Desktop/SvitUA/backups/2025-01-15_14-30-25_a1b2c3d_website.zip",
      "file_count": 150,
      "total_size": 2621440,
      "compressed_size": 1835008,
      "compression_ratio": 30.0,
      "file_hashes": {
        "index.html": "sha256:abc123...",
        "assets/css/style.css": "sha256:def456..."
      }
    }
  ]
}
```

## Configuration Options

### Source Directories
- **path**: Directory path to backup
- **name**: Backup name for identification
- **exclude_patterns**: File patterns to exclude (glob patterns)
- **exclude_dir**: Directory names to exclude

### Compression
- **format**: Archive format (`zip`, `tar.gz`)
- **compression_level**: Compression level (1-9 for ZIP, 1-9 for TAR.GZ)

### Metadata
- **include_git_info**: Include Git status information
- **include_file_hashes**: Calculate and store file hashes
- **include_size_info**: Include file size information

## Error Handling

The backup system includes comprehensive error handling:

- **Missing Directories**: Graceful handling of non-existent source directories
- **File Access Errors**: Skip files that cannot be read
- **Compression Errors**: Continue with other files if compression fails
- **Git Errors**: Fallback to default values if Git commands fail
- **Configuration Errors**: Validate configuration before processing

## Security Features

- **File Integrity**: SHA256 hash verification
- **Archive Verification**: Test archive integrity after creation
- **Metadata Validation**: Validate backup metadata structure
- **Error Logging**: Comprehensive error reporting

## Performance Considerations

- **Incremental Processing**: Only process files that exist
- **Efficient Compression**: Configurable compression levels
- **Memory Management**: Process files in chunks
- **Parallel Processing**: Future enhancement for large backups

## Troubleshooting

### Common Issues

1. **"Directory does not exist"**: Check source paths in configuration
2. **"Git command failed"**: Ensure working directory is a Git repository
3. **"Configuration file not found"**: Verify config file path
4. **"Permission denied"**: Check file permissions for source and destination

### Debug Mode

Enable verbose output for detailed debugging:
```bash
python3 cli.py --config backup_config.yaml --backup --verbose
```

## Future Enhancements

- **Incremental Backups**: Only backup changed files
- **Encryption**: Encrypt sensitive backup archives
- **Cloud Storage**: Upload to cloud services
- **Scheduling**: Automatic backup scheduling
- **Notifications**: Email/Slack notifications
- **Monitoring**: Backup success/failure monitoring
- **Parallel Processing**: Multi-threaded backup processing

## License

This backup system is part of the SVIT UA project.

## Support

For issues and questions, please refer to the project documentation or create an issue in the project repository.
