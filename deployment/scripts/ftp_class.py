import os
import ftplib
from paramiko import SSHClient, AutoAddPolicy
from typing import List, Dict
from logger import Logger



class FileTransfer:
    """Handles file transfer operations via FTP and SFTP"""
    
    def __init__(self):
        self.config = self.init_yaml_class()
        self.logger = self.init_logger_class()
        self.connection = None
        self.sftp = None

    def init_yaml_class(self):
        """Initialize YAML configuration"""
        from config_yaml import ConfigYAML
        yaml_config = ConfigYAML()
        # Return the underlying dict so this class can subscript it safely
        return yaml_config.config
    
    def init_logger_class(self):
        """Initialize Logger"""
        from logger import Logger
        file_transfer_log_path = self.config.get('constants', {}).get('file_transfer_log_path', '')
        return Logger(file_transfer_log_path)

    
    def connect(self) -> bool:
        """Establish connection to remote server"""
        try:
            ftp_settings = self.config.get('ftp_transfer_settings', {})
            protocol = ftp_settings.get('protocol')

            if protocol == 'ftp':
                return self._connect_ftp(ftp_settings)
            elif protocol == 'sftp':
                return self._connect_sftp(ftp_settings)
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

    def delete_file(self, remote_path: str, environment: str = None) -> bool:
        """Delete a remote file"""
        try:
            # Ensure connection is alive
            if environment and not self._ensure_connection(environment):
                self.logger.error(f"Failed to maintain connection for file deletion: {remote_path}")
                return False
            
            if self.connection:  # FTP
                self.connection.delete(remote_path)
            elif self.sftp:  # SFTP
                self.sftp.remove(remote_path)
            
            self.logger.info(f"Deleted file: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"File deletion failed for {remote_path}: {str(e)}")
            return False
    
    def delete_directory(self, remote_path: str, environment: str = None) -> bool:
        """Delete a remote directory (recursively if not empty)"""
        try:
            # First, try to delete as empty directory
            if self.connection:  # FTP
                self.connection.rmd(remote_path)
            elif self.sftp:  # SFTP
                self.sftp.rmdir(remote_path)
            
            self.logger.info(f"Deleted directory: {remote_path}")
            return True
        except Exception as e:
            error_message = str(e)
            # If directory is not empty, recursively delete contents
            if "Directory not empty" in error_message or "550" in error_message:
                self.logger.info(f"Directory {remote_path} is not empty, recursively deleting contents...")
                return self._delete_directory_recursive(remote_path, environment=environment)
            else:
                self.logger.error(f"Directory deletion failed for {remote_path}: {error_message}")
                return False
    
    def exists_file_dir(self, remote_path: str) -> bool:
        """Check if a file or directory exists"""
        try:
            if self.connection:  # FTP
                current_dir = self.connection.pwd()
                try:
                    self.connection.cwd(remote_path)
                    self.connection.cwd(current_dir)  # Go back
                    return True  # It's a directory
                except:
                    # Not a directory, check if it's a file
                    try:
                        self.connection.size(remote_path)
                        return True  # It's a file
                    except:
                        return False  # Neither file nor directory
            elif self.sftp:  # SFTP
                try:
                    self.sftp.stat(remote_path)
                    return True
                except:
                    return False
        except Exception as e:
            self.logger.error(f"Existence check failed for {remote_path}: {str(e)}")
            return False

    def _delete_directory_recursive(self, remote_path: str, depth: int = 0, environment: str = None) -> bool:
        """Recursively delete directory contents and then the directory itself"""
        # Safety check to prevent infinite recursion
        if depth > 50:  # Maximum recursion depth
            self.logger.error(f"Maximum recursion depth reached for {remote_path}")
            return False
            
        try:
            # Ensure connection is alive
            if environment and not self._ensure_connection(environment):
                self.logger.error(f"Failed to maintain connection for {remote_path}")
                return False
            
            # First check if directory exists by trying to list it
            try:
                if self.connection:  # FTP
                    current_dir = self.connection.pwd()
                    self.connection.cwd(remote_path)
                    self.connection.cwd(current_dir)  # Go back
                elif self.sftp:  # SFTP
                    self.sftp.stat(remote_path)
            except Exception as e:
                # Directory doesn't exist, consider it already deleted
                self.logger.info(f"Directory {remote_path} doesn't exist, skipping deletion")
                return True
            
            # Get list of files and subdirectories
            files = self.list_files(remote_path)
            subdirs = self.list_directory(remote_path)
            
            self.logger.info(f"Found {len(files)} files and {len(subdirs)} subdirectories in {remote_path}")
            
            # Delete all files first
            for file_path in files:
                # Ensure connection before each file deletion
                if environment and not self._ensure_connection(environment):
                    self.logger.error(f"Failed to maintain connection while deleting file: {file_path}")
                    return False
                
                if not self.delete_file(file_path):
                    self.logger.error(f"Failed to delete file: {file_path}")
                    return False
            
            # Recursively delete subdirectories (use _delete_directory_recursive to avoid infinite loop)
            for subdir_path in subdirs:
                # Ensure connection before each subdirectory deletion
                if environment and not self._ensure_connection(environment):
                    self.logger.error(f"Failed to maintain connection while deleting subdirectory: {subdir_path}")
                    return False
                
                if not self._delete_directory_recursive(subdir_path, depth + 1, environment):
                    self.logger.error(f"Failed to delete subdirectory: {subdir_path}")
                    return False
            
            # Now try to delete the empty directory
            try:
                # Ensure connection before final directory deletion
                if environment and not self._ensure_connection(environment):
                    self.logger.error(f"Failed to maintain connection for final directory deletion: {remote_path}")
                    return False
                
                if self.connection:  # FTP
                    self.connection.rmd(remote_path)
                elif self.sftp:  # SFTP
                    self.sftp.rmdir(remote_path)
                
                self.logger.info(f"Recursively deleted directory: {remote_path}")
                return True
            except Exception as e:
                # If directory still can't be deleted, it might not exist anymore
                self.logger.info(f"Directory {remote_path} may already be deleted: {str(e)}")
                return True
            
        except Exception as e:
            self.logger.error(f"Recursive directory deletion failed for {remote_path}: {str(e)}")
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
    
    def _check_connection(self) -> bool:
        """Check if connection is still alive and reconnect if needed"""
        try:
            if self.connection:  # FTP
                # Try a simple command to test connection
                self.connection.voidcmd("NOOP")
                return True
            elif self.sftp:  # SFTP
                # Try to get current directory
                self.sftp.getcwd()
                return True
        except Exception as e:
            self.logger.warning(f"Connection check failed: {str(e)}")
            return False
        return False
    
    def _ensure_connection(self, environment: str) -> bool:
        """Ensure connection is alive, reconnect if needed"""
        if self._check_connection():
            return True
        
        self.logger.info("Connection lost, attempting to reconnect...")
        return self.connect(environment)
    
    def list_directory(self, remote_path: str) -> List[str]:
        """List directories in remote path"""
        try:
            directories = []
            if self.connection:  # FTP
                current_dir = self.connection.pwd()
                self.connection.cwd(remote_path)
                file_list = self.connection.nlst()
                self.connection.cwd(current_dir)
                
                for item in file_list:
                    if item not in ['.', '..']:
                        # Check if it's a directory by trying to change to it
                        try:
                            self.connection.cwd(os.path.join(remote_path, item))
                            self.connection.cwd(remote_path)  # Go back
                            directories.append(os.path.join(remote_path, item))
                        except:
                            # Not a directory, skip
                            pass
                            
            elif self.sftp:  # SFTP
                for item in self.sftp.listdir(remote_path):
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        try:
                            stat = self.sftp.stat(item_path)
                            if stat.st_mode & 0o40000:  # Check if it's a directory
                                directories.append(item_path)
                        except:
                            pass
            
            self.logger.info(f"Listed {len(directories)} directories in {remote_path}")
            return directories
        except Exception as e:
            self.logger.error(f"Directory listing failed for {remote_path}: {str(e)}")
            return []
    
    def list_files(self, remote_path: str) -> List[str]:
        """List files in remote path"""
        try:
            files = []
            if self.connection:  # FTP
                current_dir = self.connection.pwd()
                self.connection.cwd(remote_path)
                file_list = self.connection.nlst()
                self.connection.cwd(current_dir)
                
                for item in file_list:
                    if item not in ['.', '..']:
                        # Check if it's a file by trying to change to it (should fail for files)
                        try:
                            self.connection.cwd(os.path.join(remote_path, item))
                            self.connection.cwd(remote_path)  # Go back
                            # If we get here, it's a directory, not a file
                        except:
                            # It's a file
                            files.append(os.path.join(remote_path, item))
                            
            elif self.sftp:  # SFTP
                for item in self.sftp.listdir(remote_path):
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        try:
                            stat = self.sftp.stat(item_path)
                            if not (stat.st_mode & 0o40000):  # Check if it's NOT a directory
                                files.append(item_path)
                        except:
                            pass
            
            self.logger.info(f"Listed {len(files)} files in {remote_path}")
            return files
        except Exception as e:
            self.logger.error(f"File listing failed for {remote_path}: {str(e)}")
            return []
        

    def get_all_files_and_dirs_recursive(self, remote_path: str, exclude_patterns: list) -> Dict[str, List[str]]:
        """Get all files and directories in remote path"""
        try:
            all_items = {'files': [], 'dirs': []}
            if self.connection:  # FTP
                current_dir = self.connection.pwd()
                self.connection.cwd(remote_path)
                file_list = self.connection.nlst()
                self.connection.cwd(current_dir)
                
                for item in file_list:
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        if item_path in exclude_patterns:
                            continue
                        # Check if it's a directory by trying to change to it
                        try:
                            self.connection.cwd(item_path)
                            self.connection.cwd(remote_path)  # Go back
                            all_items['dirs'].append(item_path)
                            # Recursively get contents of subdirectory
                            sub_items = self.get_all_files_and_dirs_recursive(item_path, exclude_patterns)
                            all_items['files'].extend(sub_items.get('files', []))
                            all_items['dirs'].extend(sub_items.get('dirs', []))
                        except:
                            all_items['files'].append(item_path)
                            
            elif self.sftp:  # SFTP
                for item in self.sftp.listdir(remote_path):
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        if item_path in exclude_patterns:
                            continue
                        try:
                            stat = self.sftp.stat(item_path)
                            if stat.st_mode & 0o40000:  # Directory
                                all_items['dirs'].append(item_path)
                                # Recursively get contents of subdirectory
                                sub_items = self.get_all_files_and_dirs_recursive(item_path, exclude_patterns)
                                all_items['files'].extend(sub_items.get('files', []))
                                all_items['dirs'].extend(sub_items.get('dirs', []))
                            else:
                                all_items['files'].append(item_path)
                        except:
                            pass
            
            self.logger.info(f"Listed {len(all_items['files'])} files and {len(all_items['dirs'])} directories in {remote_path}")
            return all_items
        except Exception as e:
            self.logger.error(f"File and directory listing failed for {remote_path}: {str(e)}")
            return {'files': [], 'dirs': []}


    # DELETE THIS FUNCTION LATER - DUPLICATE OF THE ABOVE
    def get_all_files_and_dirs(self, remote_path: str, exclude_patterns: list) -> Dict[str, List[str]]:
        """Get all files and directories in remote path"""
        try:
            all_items = {'files': [], 'dirs': []}
            if self.connection:  # FTP
                current_dir = self.connection.pwd()
                self.connection.cwd(remote_path)
                file_list = self.connection.nlst()
                self.connection.cwd(current_dir)
                
                for item in file_list:
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        # Check if it's a directory by trying to change to it
                        if item_path in exclude_patterns:
                            continue
                        try:
                            self.connection.cwd(item_path)
                            self.connection.cwd(remote_path)  # Go back
                            all_items['dirs'].append(item_path)
                        except:
                            all_items['files'].append(item_path)
                            
            elif self.sftp:  # SFTP
                for item in self.sftp.listdir(remote_path):
                    if item not in ['.', '..']:
                        item_path = os.path.join(remote_path, item)
                        if item_path in exclude_patterns:
                            continue
                        try:
                            stat = self.sftp.stat(item_path)
                            if stat.st_mode & 0o40000:  # Directory
                                all_items['dirs'].append(item_path)
                            else:
                                all_items['files'].append(item_path)
                        except:
                            pass
            
            self.logger.info(f"Listed {len(all_items['files'])} files and {len(all_items['dirs'])} directories in {remote_path}")
            return all_items
        except Exception as e:
            self.logger.error(f"File and directory listing failed for {remote_path}: {str(e)}")
            return {'files': [], 'dirs': []}
        
def test_create_and_delete_dir()-> bool:
    """Test creating and deleting directories"""

    count = 0
    pcount = 0
    try:
        # Initialize FileTransfer        
        ftr = FileTransfer()
        pcount += 1
        ftr.connect()
        count += 1


        pcount += 1
        ftr.create_directory('/test_delete_20250907_1')
        ftr.create_directory('/test_delete_20250907_1/subdir1')
        if ftr.exists_file_dir('/test_delete_20250907_1') and ftr.exists_file_dir('/test_delete_20250907_1/subdir1'):            
            count += 1
        else:
            raise Exception("Directory creation verification failed")

        # Create some test files
        local_test_file1 = 'test_file1.txt'
        local_test_file2 = 'test_file2.txt'
        with open(local_test_file1, 'w') as f:
            f.write("This is a test file 1.")
        with open(local_test_file2, 'w') as f:
            f.write("This is a test file 2.")

        # Upload test files
        pcount += 1
        try:
            ftr.upload_file(local_test_file1, '/test_delete_20250907_1/test_file1.txt')
            ftr.upload_file(local_test_file2, '/test_delete_20250907_1/subdir1/test_file2.txt')
            print("✓ Test files uploaded successfully")
            count += 1
        except Exception as e:
            print(f"✗ Test file upload failed with error: {str(e)}")

        pcount += 1
        try:
            files = ftr.list_files('/test_delete_20250907_1')
            subdirs = ftr.list_directory('/test_delete_20250907_1')
            print('LISTED START ======================================')
            for file in files:
                print(f"  - File: {file}")
            for subdir in subdirs:
                print(f"  - Subdirectory: {subdir}")
            print('LISTED END ======================================')
            count += 1
        except Exception as e:
            print(f"✗ Listing files/subdirectories failed with error: {str(e)}")

        # test download
        pcount += 1
        try:
            ftr.download_file('/test_delete_20250907_1/test_file1.txt', 'downloaded_test_file1.txt')
            ftr.download_file('/test_delete_20250907_1/subdir1/test_file2.txt', 'downloaded_test_file2.txt')
            if not os.path.exists('downloaded_test_file1.txt') or not os.path.exists('downloaded_test_file2.txt'):
                raise FileNotFoundError("Downloaded files not found")
            print("✓ Test file downloaded successfully")
            count += 1
        except Exception as e:
            print(f"✗ Test file download failed with error: {str(e)}")        

        # Now delete the directory recursively
        pcount += 1
        if ftr.delete_directory('/test_delete_20250907_1', environment='development'):
            print("✓ Directory and contents deleted successfully")
            count += 1
        else:
            raise Exception("Directory deletion failed")

        # Clean up local test files and downloaded files
        pcount += 1
        os.remove(local_test_file1)
        os.remove(local_test_file2)
        os.remove('downloaded_test_file1.txt')
        os.remove('downloaded_test_file2.txt')
        count += 1


        # Disconnect
        ftr.disconnect()        
        print("✓ Connection closed")
        
        if count == pcount:            
            print("********************************************")
            print("✓ ALL TESTS PASSED --- All tests passed successfully")
            print("********************************************")
            return True
                
    except Exception as e:
        print("x x x x x x x error  x x x x x x x x x x x x x x")
        print(f"✗ ERROR Test failed with error: {str(e)}")
        print("x x x x x x x x  error x x x x x x x x x x x x x")
        return False


def main():
    """Main function for testing"""

    # if not test_create_and_delete_dir():
    #     return

    ftr = FileTransfer() 
    print(ftr.config)

if __name__ == '__main__':
    main() 