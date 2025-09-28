import os
import hashlib
import fnmatch
from pathlib import Path
from typing import List, Dict, Set
import yaml


def load_config(config_path: str) -> dict:
    """Load backup configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Calculate hash of a file."""
    hash_obj = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return f"{algorithm}:{hash_obj.hexdigest()}"
    except Exception as e:
        print(f"Warning: Could not calculate hash for {file_path}: {e}")
        return ""


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def should_exclude_file(file_path: str, exclude_patterns: List[str], exclude_dirs: List[str]) -> bool:
    """Check if file should be excluded based on patterns and directories."""
    file_path_str = str(file_path)
    
    # Check directory exclusions
    for exclude_dir in exclude_dirs:
        if exclude_dir in file_path_str:
            return True
    
    # Check pattern exclusions
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(os.path.basename(file_path_str), pattern):
            return True
        if pattern in file_path_str:
            return True
    
    return False


def scan_directory(directory_path: str, exclude_patterns: List[str], exclude_dirs: List[str]) -> Dict[str, dict]:
    """Scan directory and return file information."""
    files_info = {}
    
    if not os.path.exists(directory_path):
        print(f"Warning: Directory does not exist: {directory_path}")
        return files_info
    
    try:
        for root, dirs, files in os.walk(directory_path):
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if not should_exclude_file(os.path.join(root, d), exclude_patterns, exclude_dirs)]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory_path)
                
                if not should_exclude_file(file_path, exclude_patterns, exclude_dirs):
                    try:
                        file_size = get_file_size(file_path)
                        file_hash = calculate_file_hash(file_path)
                        
                        files_info[relative_path] = {
                            'path': file_path,
                            'size': file_size,
                            'hash': file_hash,
                            'modified': os.path.getmtime(file_path)
                        }
                    except OSError as e:
                        print(f"Warning: Could not process file {file_path}: {e}")
    
    except Exception as e:
        print(f"Error scanning directory {directory_path}: {e}")
    
    return files_info


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


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(directory_path, exist_ok=True)


def get_total_size(files_info: Dict[str, dict]) -> int:
    """Calculate total size of all files."""
    return sum(file_info['size'] for file_info in files_info.values())


def validate_config(config: dict) -> bool:
    """Validate backup configuration."""
    required_keys = ['source_directories', 'backup_destination', 'compression', 'metadata']
    
    for key in required_keys:
        if key not in config.get('backup_settings', {}):
            print(f"Error: Missing required configuration key: {key}")
            return False
    
    # Validate source directories
    for directory in config['backup_settings']['source_directories']:
        required_dir_keys = ['path', 'name']
        for key in required_dir_keys:
            if key not in directory:
                print(f"Error: Missing required directory configuration key: {key}")
                return False
    
    return True
