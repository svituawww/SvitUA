#!/usr/bin/env python3
"""
Deployment Manager for Loopia.se Hosting
Handles file transfer, directory management, and deployment operations
"""

import os
import yaml
import logging
import hashlib
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import ftplib
import paramiko
from paramiko import SSHClient, AutoAddPolicy
import shutil
import fnmatch


class Logger:
    """Enhanced logging system for deployment operations"""
    
    def __init__(self, log_file: str = 'logs/deployment.log'):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class FileTransfer:
    """Handles file transfer operations via FTP and SFTP"""
    
    def __init__(self, config: Dict, logger: Logger):
        self.config = config
        self.logger = logger
        self.connection = None
        self.sftp = None
    
    def connect(self, environment: str) -> bool:
        """Establish connection to remote server"""
        try:
            env_config = self.config['environments'][environment]
            protocol = env_config['protocol']
            
            if protocol == 'ftp':
                return self._connect_ftp(env_config)
            elif protocol == 'sftp':
                return self._connect_sftp(env_config)
            else:
                self.logger.error(f"Unsupported protocol: {protocol}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
    
    def _connect_ftp(self, config: Dict) -> bool:
        """Connect via FTP"""
        try:
            self.connection = ftplib.FTP()
            self.connection.connect(
                host=config['host'],
                port=config.get('port', 21),
                timeout=config.get('timeout', 30)
            )
            self.connection.login(
                user=config['username'],
                passwd=config['password']
            )
            self.logger.info(f"FTP connection established to {config['host']}")
            return True
        except Exception as e:
            self.logger.error(f"FTP connection failed: {str(e)}")
            return False
    
    def _connect_sftp(self, config: Dict) -> bool:
        """Connect via SFTP"""
        try:
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(
                hostname=config['host'],
                port=config.get('port', 22),
                username=config['username'],
                password=config['password'],
                timeout=config.get('timeout', 30)
            )
            self.sftp = ssh.open_sftp()
            self.logger.info(f"SFTP connection established to {config['host']}")
            return True
        except Exception as e:
            self.logger.error(f"SFTP connection failed: {str(e)}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a single file"""
        try:
            if self.connection:  # FTP
                with open(local_path, 'rb') as file:
                    self.connection.storbinary(f'STOR {remote_path}', file)
            elif self.sftp:  # SFTP
                self.sftp.put(local_path, remote_path)
            
            self.logger.info(f"Uploaded: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"Upload failed for {local_path}: {str(e)}")
            return False

    def upload_dir(self, local_path: str, remote_path: str) -> bool:
        """Upload a directory"""
        try:
            self.connection.mkd(remote_path)
            return True
        except Exception as e:
            self.logger.error(f"Upload failed for {local_path}: {str(e)}")
            return False
    
    def create_directory(self, remote_path: str) -> bool:
        """Create remote directory"""
        try:
            if self.connection:  # FTP
                self.connection.mkd(remote_path)
            elif self.sftp:  # SFTP
                self.sftp.mkdir(remote_path)
            
            self.logger.info(f"Created directory: {remote_path}")
            return True
        except Exception as e:
            error_message = str(e)
            # Handle "File exists" error gracefully (directory already exists)
            if "File exists" in error_message or "550" in error_message:
                self.logger.debug(f"Directory already exists: {remote_path}")
                return True
            else:
                self.logger.error(f"Directory creation failed for {remote_path}: {error_message}")
                return False
    
    def set_permissions(self, remote_path: str, permissions: int) -> bool:
        """Set file permissions (SFTP only)"""
        if self.sftp:
            try:
                self.sftp.chmod(remote_path, permissions)
                self.logger.info(f"Set permissions {oct(permissions)} for {remote_path}")
                return True
            except Exception as e:
                self.logger.error(f"Permission setting failed for {remote_path}: {str(e)}")
                return False
        return True  # FTP doesn't support chmod

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a remote file ftp"""
        try:
            if self.connection:  # FTP
                self.connection.retrbinary(f'RETR {remote_path}', open(local_path, 'wb').write)
            return True
        except Exception as e:
            self.logger.error(f"File download failed for {remote_path}: {str(e)}")
            return False

    def delete_file(self, remote_path: str) -> bool:
        """Delete a remote file"""
        try:
            if self.connection:  # FTP
                self.connection.delete(remote_path)
            elif self.sftp:  # SFTP
                self.sftp.remove(remote_path)
            
            self.logger.info(f"Deleted file: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"File deletion failed for {remote_path}: {str(e)}")
            return False
    
    def delete_directory(self, remote_path: str) -> bool:
        """Delete a remote directory"""
        try:
            if self.connection:  # FTP
                self.connection.rmd(remote_path)
            elif self.sftp:  # SFTP
                self.sftp.rmdir(remote_path)
            
            self.logger.info(f"Deleted directory: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"Directory deletion failed for {remote_path}: {str(e)}")
            return False
    
    def disconnect(self):
        """Close connection"""
        try:
            if self.connection:
                self.connection.quit()
            elif self.sftp:
                self.sftp.close()
                self.sftp.get_channel().get_transport().close()
            self.logger.info("Connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {str(e)}")


class DeploymentManager:
    """Main deployment management class"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.load_config(config_file)
        self.logger = Logger(self.config['deployment']['logging']['file'])
        self.transfer = None
        self.current_environment = None
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise Exception(f"Failed to load config file: {str(e)}")
    
    def connect(self, environment: str) -> bool:
        """Establish connection to specified environment"""
        if environment not in self.config['environments']:
            self.logger.error(f"Environment '{environment}' not found in configuration")
            return False
        
        self.current_environment = environment
        self.transfer = FileTransfer(self.config, self.logger)
        return self.transfer.connect(environment)
    
    def deploy(self, source_path: str, remote_path: str, environment: str, 
               incremental: bool = False) -> Dict:
        """Main deployment method"""
        start_time = time.time()
        self.logger.info(f"Starting deployment to {environment}")
        
        try:
            # Connect to environment
            if not self.connect(environment):
                return {'success': False, 'error': 'Connection failed'}
            
            # Get environment config
            env_config = self.config['environments'][environment]
            
            # Handle remote path construction
            if remote_path.startswith('/'):
                # If remote_path is absolute, use it directly
                full_remote_path = remote_path
            else:
                # If remote_path is relative, combine with config remote_path
                # Handle special case for './' (current directory)
                if remote_path == './':
                    full_remote_path = env_config['remote_path']
                else:
                    full_remote_path = os.path.join(env_config['remote_path'], remote_path)
            
            # Create backup if enabled
            if self.config['deployment']['backup_enabled']:
                self._create_backup(full_remote_path)
            
            # Get file list
            files_to_upload = self._get_files_to_upload(source_path, incremental)
            
            # Create directories
            directories = self._get_directories_to_create(files_to_upload, full_remote_path)
            for directory in directories:
                self.transfer.create_directory(directory)
            
            # Upload files
            uploaded_count = 0
            failed_count = 0
            
            for local_file, remote_file in files_to_upload:
                if self.transfer.upload_file(local_file, remote_file):
                    uploaded_count += 1
                    # Set permissions
                    if local_file.endswith(('.php', '.py', '.sh')):
                        self.transfer.set_permissions(remote_file, 
                                                   self.config['deployment']['file_permissions']['scripts'])
                    else:
                        self.transfer.set_permissions(remote_file, 
                                                   self.config['deployment']['file_permissions']['files'])
                else:
                    failed_count += 1
            
            # Cleanup old files if not incremental
            if not incremental:
                self._cleanup_old_files(full_remote_path, source_path)
            
            deployment_time = time.time() - start_time
            
            result = {
                'success': failed_count == 0,
                'uploaded_count': uploaded_count,
                'failed_count': failed_count,
                'deployment_time': deployment_time,
                'environment': environment
            }
            
            self.logger.info(f"Deployment completed: {uploaded_count} files uploaded, "
                           f"{failed_count} failed, time: {deployment_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if self.transfer:
                self.transfer.disconnect()
    
    def _get_files_to_upload(self, source_path: str, incremental: bool) -> List[Tuple[str, str]]:
        """Get list of files to upload"""
        files_to_upload = []
        exclude_patterns = self.config['deployment']['exclude_patterns']
        
        for root, dirs, files in os.walk(source_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)]
            
            for file in files:
                # Skip excluded files
                if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    continue
                
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, source_path)
                remote_file = os.path.join(self.config['environments'][self.current_environment]['remote_path'], 
                                         relative_path)
                
                files_to_upload.append((local_file, remote_file))
        
        return files_to_upload
    
    def _get_directories_to_create(self, files_to_upload: List[Tuple[str, str]], 
                                  base_remote_path: str) -> List[str]:
        """Get list of directories to create"""
        directories = set()
        
        for _, remote_file in files_to_upload:
            remote_dir = os.path.dirname(remote_file)
            if remote_dir != base_remote_path:
                directories.add(remote_dir)
                
                # Also add all parent directories
                current_dir = remote_dir
                while current_dir != base_remote_path and current_dir != '/':
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir != current_dir and parent_dir != base_remote_path:
                        directories.add(parent_dir)
                    current_dir = parent_dir
        
        # Sort by depth (shortest paths first) to create parent directories before children
        return sorted(directories, key=lambda x: (x.count('/'), x))
    
    def _create_backup(self, remote_path: str):
        """Create backup of current deployment"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.config['deployment']['backup_path'], backup_name)
        
        self.logger.info(f"Creating backup: {backup_path}")
        # Implementation would depend on server capabilities
    
    def _cleanup_old_files(self, remote_path: str, source_path: str = None):
        """Clean up old files not in current deployment"""
        self.logger.info(f"Cleaning up old files in {remote_path}")
        
        try:
            # Check if remote directory exists before attempting cleanup
            if not self._remote_directory_exists(remote_path):
                self.logger.info(f"Remote directory {remote_path} does not exist, skipping cleanup")
                return
            
            # Get list of files that should be in the deployment
            current_files = set()
            if source_path:
                for _, remote_file in self._get_files_to_upload(source_path, False):
                    current_files.add(remote_file)
            
            # List remote files
            if self.transfer.connection:  # FTP
                remote_files = self._list_ftp_files(remote_path)
            elif self.transfer.sftp:  # SFTP
                remote_files = self._list_sftp_files(remote_path)
            else:
                self.logger.warning("No active connection for file listing")
                return
            
            # Find files to delete (files on server but not in current deployment)
            files_to_delete = set(remote_files) - current_files
            
            # Delete old files
            deleted_count = 0
            for file_path in files_to_delete:
                if self.transfer.delete_file(file_path):
                    deleted_count += 1
                    self.logger.info(f"Deleted old file: {file_path}")
                else:
                    self.logger.error(f"Failed to delete old file: {file_path}")
            
            self.logger.info(f"Cleanup completed: {deleted_count} old files deleted")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
    
    def _remote_directory_exists(self, remote_path: str) -> bool:
        """Check if remote directory exists"""
        try:
            if self.transfer.connection:  # FTP
                # Try to change to the directory
                current_dir = self.transfer.connection.pwd()
                self.transfer.connection.cwd(remote_path)
                self.transfer.connection.cwd(current_dir)  # Go back
                return True
            elif self.transfer.sftp:  # SFTP
                # Try to list the directory
                self.transfer.sftp.listdir(remote_path)
                return True
            return False
        except Exception:
            return False
    
    def _list_ftp_files(self, remote_path: str) -> List[str]:
        """List files in FTP directory"""
        try:
            files = []
            current_dir = self.transfer.connection.pwd()
            
            # Change to target directory
            self.transfer.connection.cwd(remote_path)
            file_list = self.transfer.connection.nlst()
            
            # Go back to original directory
            self.transfer.connection.cwd(current_dir)
            
            for item in file_list:
                if item not in ['.', '..']:
                    file_path = os.path.join(remote_path, item)
                    files.append(file_path)
            
            return files
        except Exception as e:
            self.logger.error(f"FTP file listing failed: {str(e)}")
            return []
    
    def _list_sftp_files(self, remote_path: str) -> List[str]:
        """List files in SFTP directory"""
        try:
            files = []
            for item in self.transfer.sftp.listdir(remote_path):
                if item not in ['.', '..']:
                    file_path = os.path.join(remote_path, item)
                    files.append(file_path)
            
            return files
        except Exception as e:
            self.logger.error(f"SFTP file listing failed: {str(e)}")
            return []
    
    def rollback(self, version: str) -> Dict:
        """Rollback to previous version"""
        self.logger.info(f"Rolling back to version: {version}")
        
        try:
            # This would need to be implemented based on your backup strategy
            # For now, we'll provide a framework
            
            backup_path = os.path.join(self.config['deployment']['backup_path'], f"backup_{version}")
            
            if not self.connect(self.current_environment):
                return {'success': False, 'error': 'Connection failed during rollback'}
            
            # List backup files (this would need to be implemented)
            backup_files = self._list_backup_files(backup_path)
            
            if not backup_files:
                return {'success': False, 'error': f'No backup files found for version {version}'}
            
            # Restore files from backup
            restored_count = 0
            failed_count = 0
            
            for backup_file in backup_files:
                if self.transfer.upload_file(backup_file['local'], backup_file['remote']):
                    restored_count += 1
                    self.logger.info(f"Restored: {backup_file['remote']}")
                else:
                    failed_count += 1
                    self.logger.error(f"Failed to restore: {backup_file['remote']}")
            
            self.transfer.disconnect()
            
            return {
                'success': failed_count == 0,
                'restored_count': restored_count,
                'failed_count': failed_count,
                'message': f'Rolled back to version {version}'
            }
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _list_backup_files(self, backup_path: str) -> List[Dict]:
        """List files in backup directory (placeholder implementation)"""
        # This would need to be implemented based on your backup strategy
        # For now, return empty list
        self.logger.warning("Backup file listing not implemented")
        return []
    
    def cleanup_test_files(self, remote_path: str) -> Dict:
        """Clean up test files and directories"""
        self.logger.info(f"Cleaning up test files in {remote_path}")
        
        try:
            if not self.connect(self.current_environment):
                return {'success': False, 'error': 'Connection failed during cleanup'}
            
            deleted_files = 0
            deleted_dirs = 0
            
            # List and delete files
            if self.transfer.connection:  # FTP
                files = self._list_ftp_files(remote_path)
            elif self.transfer.sftp:  # SFTP
                files = self._list_sftp_files(remote_path)
            else:
                return {'success': False, 'error': 'No active connection'}
            
            # Delete files first
            for file_path in files:
                if self.transfer.delete_file(file_path):
                    deleted_files += 1
                    self.logger.info(f"Deleted file: {file_path}")
                else:
                    self.logger.error(f"Failed to delete file: {file_path}")
            
            # Try to delete the directory
            if self.transfer.delete_directory(remote_path):
                deleted_dirs += 1
                self.logger.info(f"Deleted directory: {remote_path}")
            else:
                self.logger.warning(f"Could not delete directory: {remote_path}")
            
            self.transfer.disconnect()
            
            return {
                'success': True,
                'deleted_files': deleted_files,
                'deleted_dirs': deleted_dirs,
                'message': f'Cleanup completed: {deleted_files} files, {deleted_dirs} directories'
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def generate_test_report(self) -> str:
        """Generate deployment test report"""
        report = f"""
Deployment Test Report
=====================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Configuration: {self.config_file}

Environments:
"""
        for env_name, env_config in self.config['environments'].items():
            port = env_config.get('port', 21 if env_config['protocol'] == 'ftp' else 22)
            report += f"- {env_name}: {env_config['protocol']}://{env_config['host']}:{port}{env_config['remote_path']}\n"
        
        report += f"""
Deployment Settings:
- Backup enabled: {self.config['deployment']['backup_enabled']}
- Max backups: {self.config['deployment']['max_backups']}
- Parallel uploads: {self.config['deployment']['transfer']['parallel_uploads']}
- Retry attempts: {self.config['deployment']['transfer']['retry_attempts']}
"""
        return report 