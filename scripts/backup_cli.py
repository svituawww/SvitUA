#!/usr/bin/env python3
"""
SVIT UA Backup System - Command Line Interface
"""

import argparse
import sys
import os
from pathlib import Path
import sys
import os

# Add the backuping directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backuping'))

from backuping.backup_manager import BackupManager


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="SVIT UA Backup System - Automated backup with configuration management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create backup with auto commit message
  python3 backup_cli.py --config backuping/backup_config.yaml --backup

  # Create backup with custom commit message
  python3 backup_cli.py --config backuping/backup_config.yaml --backup --message "Updated website design"

  # Verify specific backup
  python3 backup_cli.py --config backuping/backup_config.yaml --verify 2025-01-15_14-30-25_a1b2c3d

  # List all backups
  python3 backup_cli.py --config backuping/backup_config.yaml --list

  # Restore from backup
  python3 backup_cli.py --config backuping/backup_config.yaml --restore 2025-01-15_14-30-25_a1b2c3d --restore-path ./restored

  # Cleanup old backups
  python3 backup_cli.py --config backuping/backup_config.yaml --cleanup --max-backups 5
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--config',
        required=True,
        help='Path to backup configuration file (YAML)'
    )
    
    # Action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--backup',
        action='store_true',
        help='Create a new backup'
    )
    action_group.add_argument(
        '--verify',
        metavar='BACKUP_ID',
        help='Verify backup integrity'
    )
    action_group.add_argument(
        '--list',
        action='store_true',
        help='List all available backups'
    )
    action_group.add_argument(
        '--info',
        metavar='BACKUP_ID',
        help='Get detailed information about a specific backup'
    )
    action_group.add_argument(
        '--restore',
        metavar='BACKUP_ID',
        help='Restore backup to specified path'
    )
    action_group.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove old backups based on retention policy'
    )
    
    # Optional arguments
    parser.add_argument(
        '--message',
        help='Custom commit message for backup'
    )
    parser.add_argument(
        '--restore-path',
        default='./restored',
        help='Path to restore backup to (default: ./restored)'
    )
    parser.add_argument(
        '--max-backups',
        type=int,
        default=10,
        help='Maximum number of backups to keep during cleanup (default: 10)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate config file
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        # Initialize backup manager
        backup_manager = BackupManager(args.config)
        
        # Execute requested action
        if args.backup:
            success = backup_manager.create_backup(args.message)
            if not success:
                print("Error: Backup creation failed")
                sys.exit(1)
            print("Backup completed successfully")
            
        elif args.verify:
            success = backup_manager.verify_backup(args.verify)
            if not success:
                print("Error: Backup verification failed")
                sys.exit(1)
            print("Backup verification completed successfully")
            
        elif args.list:
            backups = backup_manager.list_backups()
            if not backups:
                print("No backups found")
            else:
                print(f"Found {len(backups)} backup(s):")
                print("-" * 80)
                for backup in backups:
                    backup_id = backup.get('backup_id', 'Unknown')
                    timestamp = backup.get('timestamp', 'Unknown')
                    commit_message = backup.get('commit_message', 'No message')
                    file_count = sum(b.get('file_count', 0) for b in backup.get('backups', []))
                    total_size = sum(b.get('total_size', 0) for b in backup.get('backups', []))
                    
                    print(f"ID: {backup_id}")
                    print(f"Timestamp: {timestamp}")
                    print(f"Commit: {commit_message}")
                    print(f"Files: {file_count}")
                    print(f"Size: {format_size(total_size)}")
                    print("-" * 80)
                    
        elif args.info:
            backup_info = backup_manager.get_backup_info(args.info)
            if not backup_info:
                print(f"Error: Backup {args.info} not found")
                sys.exit(1)
            
            print(f"Backup Information: {args.info}")
            print("=" * 50)
            print(f"Timestamp: {backup_info.get('timestamp', 'Unknown')}")
            print(f"Commit Hash: {backup_info.get('commit_hash', 'Unknown')}")
            print(f"Commit Message: {backup_info.get('commit_message', 'No message')}")
            print()
            
            print("Backup Entries:")
            for backup_entry in backup_info.get('backups', []):
                print(f"  - {backup_entry.get('name', 'Unknown')}")
                print(f"    Source: {backup_entry.get('source_path', 'Unknown')}")
                print(f"    Archive: {backup_entry.get('archive_path', 'Unknown')}")
                print(f"    Files: {backup_entry.get('file_count', 0)}")
                print(f"    Size: {format_size(backup_entry.get('total_size', 0))}")
                print(f"    Compressed: {format_size(backup_entry.get('compressed_size', 0))}")
                print(f"    Compression: {backup_entry.get('compression_ratio', 0)}%")
                print()
                
        elif args.restore:
            success = backup_manager.restore_backup(args.restore, args.restore_path)
            if not success:
                print("Error: Backup restoration failed")
                sys.exit(1)
            print(f"Backup restored successfully to {args.restore_path}")
            
        elif args.cleanup:
            success = backup_manager.cleanup_old_backups(args.max_backups)
            if not success:
                print("Error: Backup cleanup failed")
                sys.exit(1)
            print("Backup cleanup completed successfully")
            
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def format_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


if __name__ == "__main__":
    main()
