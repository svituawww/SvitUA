import zipfile
import os
import tarfile
import gzip
from typing import Dict, List
from pathlib import Path


def create_zip_archive(source_files: Dict[str, dict], archive_path: str, compression_level: int = 6) -> bool:
    """Create ZIP archive from source files."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            for relative_path, file_info in source_files.items():
                try:
                    # Add file to archive
                    zipf.write(file_info['path'], relative_path)
                except Exception as e:
                    print(f"Warning: Could not add file {file_info['path']} to archive: {e}")
                    continue
        
        return True
    except Exception as e:
        print(f"Error creating ZIP archive {archive_path}: {e}")
        return False


def create_tar_gz_archive(source_files: Dict[str, dict], archive_path: str, compression_level: int = 6) -> bool:
    """Create TAR.GZ archive from source files."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        with tarfile.open(archive_path, 'w:gz', compresslevel=compression_level) as tar:
            for relative_path, file_info in source_files.items():
                try:
                    # Add file to archive
                    tar.add(file_info['path'], arcname=relative_path)
                except Exception as e:
                    print(f"Warning: Could not add file {file_info['path']} to archive: {e}")
                    continue
        
        return True
    except Exception as e:
        print(f"Error creating TAR.GZ archive {archive_path}: {e}")
        return False


def create_archive(source_files: Dict[str, dict], archive_path: str, format_type: str = 'zip', compression_level: int = 6) -> bool:
    """Create archive in specified format."""
    if format_type.lower() == 'zip':
        return create_zip_archive(source_files, archive_path, compression_level)
    elif format_type.lower() in ['tar.gz', 'tgz']:
        return create_tar_gz_archive(source_files, archive_path, compression_level)
    else:
        print(f"Error: Unsupported archive format: {format_type}")
        return False


def get_archive_size(archive_path: str) -> int:
    """Get archive file size in bytes."""
    try:
        return os.path.getsize(archive_path)
    except OSError:
        return 0


def verify_archive(archive_path: str, format_type: str = 'zip') -> bool:
    """Verify archive integrity."""
    try:
        if format_type.lower() == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # Test archive integrity
                return zipf.testzip() is None
        elif format_type.lower() in ['tar.gz', 'tgz']:
            with tarfile.open(archive_path, 'r:gz') as tar:
                # Test archive integrity
                tar.getmembers()
                return True
        else:
            print(f"Error: Unsupported archive format for verification: {format_type}")
            return False
    except Exception as e:
        print(f"Error verifying archive {archive_path}: {e}")
        return False


def list_archive_contents(archive_path: str, format_type: str = 'zip') -> List[str]:
    """List contents of archive."""
    try:
        if format_type.lower() == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                return zipf.namelist()
        elif format_type.lower() in ['tar.gz', 'tgz']:
            with tarfile.open(archive_path, 'r:gz') as tar:
                return [member.name for member in tar.getmembers() if member.isfile()]
        else:
            print(f"Error: Unsupported archive format for listing: {format_type}")
            return []
    except Exception as e:
        print(f"Error listing archive contents {archive_path}: {e}")
        return []


def extract_archive(archive_path: str, extract_path: str, format_type: str = 'zip') -> bool:
    """Extract archive to specified path."""
    try:
        os.makedirs(extract_path, exist_ok=True)
        
        if format_type.lower() == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_path)
        elif format_type.lower() in ['tar.gz', 'tgz']:
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_path)
        else:
            print(f"Error: Unsupported archive format for extraction: {format_type}")
            return False
        
        return True
    except Exception as e:
        print(f"Error extracting archive {archive_path}: {e}")
        return False
