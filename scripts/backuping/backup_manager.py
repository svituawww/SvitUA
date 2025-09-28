import os
import json
import datetime
from typing import Dict, List, Optional
from pathlib import Path

from backup_utils import (
    load_config, validate_config, scan_directory, 
    format_size, ensure_directory_exists, get_total_size
)
from git_integration import get_git_info, get_git_status
from compression import create_archive, get_archive_size, verify_archive
from verification import verify_backup_metadata, check_backup_integrity


class BackupManager:
    def __init__(self, config_path: str):
        """Initialize backup manager with configuration."""
        self.config_path = config_path
        self.config = None
        self.backup_history = []
        self.load_config()
    
    def load_config(self):
        """Load and validate backup configuration."""
        try:
            self.config = load_config(self.config_path)
            if not validate_config(self.config):
                raise ValueError("Invalid backup configuration")
            print("Configuration loaded successfully")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    def create_backup(self, commit_message: Optional[str] = None) -> bool:
        """Create backup with timestamp and commit hash."""
        try:
            # Get git information
            commit_hash, git_commit_message = get_git_info()
            git_status = get_git_status()
            
            # Use provided commit message or git commit message
            final_commit_message = commit_message or git_commit_message
            
            # Generate backup ID
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_id = f"{timestamp}_{commit_hash}"
            
            print(f"Creating backup: {backup_id}")
            print(f"Commit message: {final_commit_message}")
            
            # Initialize backup metadata
            backup_metadata = {
                'backup_id': backup_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'commit_hash': commit_hash,
                'commit_message': final_commit_message,
                'git_status': git_status,
                'backups': []
            }
            
            # Process each source directory
            for directory_config in self.config['backup_settings']['source_directories']:
                success = self._backup_directory(directory_config, backup_id, backup_metadata)
                if not success:
                    print(f"Warning: Failed to backup directory {directory_config['name']}")
            
            # Save backup metadata
            self._save_backup_metadata(backup_metadata)
            
            print(f"Backup completed: {backup_id}")
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def _backup_directory(self, directory_config: Dict, backup_id: str, backup_metadata: Dict) -> bool:
        """Backup a single directory."""
        try:
            source_path = directory_config['path']
            backup_name = directory_config['name']
            exclude_patterns = directory_config.get('exclude_patterns', [])
            exclude_dirs = directory_config.get('exclude_dir', [])
            
            print(f"Backing up {backup_name} from {source_path}")
            
            # Scan directory
            files_info = scan_directory(source_path, exclude_patterns, exclude_dirs)
            
            if not files_info:
                print(f"Warning: No files found in {source_path}")
                return False
            
            # Calculate total size
            total_size = get_total_size(files_info)
            print(f"Found {len(files_info)} files, total size: {format_size(total_size)}")
            
            # Generate archive path
            archive_name = f"{backup_id}_{backup_name}.{self.config['backup_settings']['compression']['format']}"
            archive_path = os.path.join(
                self.config['backup_settings']['backup_destination']['base_path'],
                archive_name
            )
            
            # Create archive
            compression_level = self.config['backup_settings']['compression']['compression_level']
            format_type = self.config['backup_settings']['compression']['format']
            
            print(f"Creating archive: {archive_path}")
            success = create_archive(files_info, archive_path, format_type, compression_level)
            
            if not success:
                print(f"Error creating archive for {backup_name}")
                return False
            
            # Get archive size
            compressed_size = get_archive_size(archive_path)
            
            # Prepare backup entry
            backup_entry = {
                'name': backup_name,
                'source_path': source_path,
                'archive_path': archive_path,
                'file_count': len(files_info),
                'total_size': total_size,
                'compressed_size': compressed_size,
                'compression_ratio': round((1 - compressed_size / total_size) * 100, 2) if total_size > 0 else 0
            }
            
            # Add file hashes if enabled
            if self.config['backup_settings']['metadata']['include_file_hashes']:
                file_hashes = {}
                for relative_path, file_info in files_info.items():
                    if file_info['hash']:
                        file_hashes[relative_path] = file_info['hash']
                backup_entry['file_hashes'] = file_hashes
            
            # Add to backup metadata
            backup_metadata['backups'].append(backup_entry)
            
            print(f"Successfully backed up {backup_name}: {format_size(compressed_size)}")
            return True
            
        except Exception as e:
            print(f"Error backing up directory {directory_config.get('name', 'unknown')}: {e}")
            return False
    
    def _save_backup_metadata(self, backup_metadata: Dict):
        """Save backup metadata to history file."""
        try:
            backup_dir = self.config['backup_settings']['backup_destination']['base_path']
            ensure_directory_exists(backup_dir)
            
            history_file = os.path.join(backup_dir, 'backup_history.json')
            
            # Load existing history
            existing_history = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        existing_history = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load existing backup history: {e}")
            
            # Add new backup
            existing_history.append(backup_metadata)
            
            # Save updated history
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(existing_history, f, indent=2, ensure_ascii=False)
            
            print(f"Backup metadata saved to {history_file}")
            
        except Exception as e:
            print(f"Error saving backup metadata: {e}")
    
    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        try:
            backup_dir = self.config['backup_settings']['backup_destination']['base_path']
            integrity_results = check_backup_integrity(backup_id, backup_dir)
            
            print(f"Backup verification results for {backup_id}:")
            for check, result in integrity_results.items():
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"  {check}: {status}")
            
            return integrity_results['overall_valid']
            
        except Exception as e:
            print(f"Error verifying backup {backup_id}: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups."""
        try:
            backup_dir = self.config['backup_settings']['backup_destination']['base_path']
            history_file = os.path.join(backup_dir, 'backup_history.json')
            
            if not os.path.exists(history_file):
                print("No backup history found")
                return []
            
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            return history
            
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """Get detailed information about a specific backup."""
        try:
            backups = self.list_backups()
            
            for backup in backups:
                if backup.get('backup_id') == backup_id:
                    return backup
            
            print(f"Backup {backup_id} not found")
            return None
            
        except Exception as e:
            print(f"Error getting backup info: {e}")
            return None
    
    def cleanup_old_backups(self, max_backups: int = 10) -> bool:
        """Remove old backups based on retention policy."""
        try:
            backups = self.list_backups()
            
            if len(backups) <= max_backups:
                print(f"No cleanup needed. Current backups: {len(backups)}, Max: {max_backups}")
                return True
            
            # Sort by timestamp (oldest first)
            backups.sort(key=lambda x: x.get('timestamp', ''))
            
            # Remove oldest backups
            backups_to_remove = backups[:-max_backups]
            
            print(f"Removing {len(backups_to_remove)} old backups...")
            
            for backup in backups_to_remove:
                self._remove_backup(backup)
            
            print("Cleanup completed")
            return True
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False
    
    def _remove_backup(self, backup: Dict):
        """Remove a specific backup."""
        try:
            backup_id = backup.get('backup_id')
            
            # Remove archive files
            for backup_entry in backup.get('backups', []):
                archive_path = backup_entry.get('archive_path')
                if archive_path and os.path.exists(archive_path):
                    os.remove(archive_path)
                    print(f"Removed archive: {archive_path}")
            
            # Update history file
            backup_dir = self.config['backup_settings']['backup_destination']['base_path']
            history_file = os.path.join(backup_dir, 'backup_history.json')
            
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Remove the backup from history
                history = [b for b in history if b.get('backup_id') != backup_id]
                
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                
                print(f"Removed backup {backup_id} from history")
            
        except Exception as e:
            print(f"Error removing backup {backup.get('backup_id', 'unknown')}: {e}")
    
    def restore_backup(self, backup_id: str, restore_path: str) -> bool:
        """Restore backup to specified path."""
        try:
            backup_info = self.get_backup_info(backup_id)
            if not backup_info:
                return False
            
            print(f"Restoring backup {backup_id} to {restore_path}")
            
            # Create restore directory
            ensure_directory_exists(restore_path)
            
            # Restore each backup entry
            for backup_entry in backup_info.get('backups', []):
                archive_path = backup_entry.get('archive_path')
                backup_name = backup_entry.get('name')
                
                if not os.path.exists(archive_path):
                    print(f"Error: Archive not found: {archive_path}")
                    continue
                
                # Create subdirectory for this backup
                backup_restore_path = os.path.join(restore_path, backup_name)
                ensure_directory_exists(backup_restore_path)
                
                # Extract archive
                format_type = self.config['backup_settings']['compression']['format']
                from compression import extract_archive
                
                success = extract_archive(archive_path, backup_restore_path, format_type)
                
                if success:
                    print(f"Restored {backup_name} to {backup_restore_path}")
                else:
                    print(f"Error restoring {backup_name}")
            
            print(f"Restore completed: {backup_id}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup {backup_id}: {e}")
            return False
