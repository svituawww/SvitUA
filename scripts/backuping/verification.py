import json
import os
import hashlib
from typing import Dict, List, Optional
from datetime import datetime


def verify_backup_metadata(metadata_path: str) -> bool:
    """Verify backup metadata file integrity."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check required fields
        required_fields = ['backup_id', 'timestamp', 'backups']
        for field in required_fields:
            if field not in metadata:
                print(f"Error: Missing required metadata field: {field}")
                return False
        
        # Verify backup entries
        for backup in metadata['backups']:
            required_backup_fields = ['name', 'source_path', 'archive_path', 'file_count', 'total_size']
            for field in required_backup_fields:
                if field not in backup:
                    print(f"Error: Missing required backup field: {field}")
                    return False
        
        return True
    except Exception as e:
        print(f"Error verifying backup metadata {metadata_path}: {e}")
        return False


def verify_backup_files(metadata_path: str) -> Dict[str, bool]:
    """Verify that all backup files exist and match metadata."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        verification_results = {}
        
        for backup in metadata['backups']:
            archive_path = backup['archive_path']
            backup_name = backup['name']
            
            # Check if archive file exists
            if not os.path.exists(archive_path):
                print(f"Error: Backup archive not found: {archive_path}")
                verification_results[backup_name] = False
                continue
            
            # Check archive size
            actual_size = os.path.getsize(archive_path)
            expected_size = backup.get('compressed_size', 0)
            
            if expected_size and abs(actual_size - expected_size) > 1024:  # Allow 1KB difference
                print(f"Warning: Archive size mismatch for {backup_name}")
                print(f"  Expected: {expected_size}, Actual: {actual_size}")
            
            verification_results[backup_name] = True
        
        return verification_results
    except Exception as e:
        print(f"Error verifying backup files: {e}")
        return {}


def calculate_backup_hash(archive_path: str) -> str:
    """Calculate SHA256 hash of backup archive."""
    try:
        hash_obj = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {archive_path}: {e}")
        return ""


def verify_file_hashes(metadata_path: str) -> Dict[str, Dict[str, bool]]:
    """Verify file hashes in backup metadata."""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        hash_verification = {}
        
        for backup in metadata['backups']:
            backup_name = backup['name']
            hash_verification[backup_name] = {}
            
            if 'file_hashes' not in backup:
                print(f"Warning: No file hashes found for backup {backup_name}")
                continue
            
            # Note: This would require extracting files to verify hashes
            # For now, we'll just note that hash verification is available
            hash_verification[backup_name]['hashes_available'] = True
            hash_verification[backup_name]['files_count'] = len(backup['file_hashes'])
        
        return hash_verification
    except Exception as e:
        print(f"Error verifying file hashes: {e}")
        return {}


def validate_backup_structure(backup_dir: str) -> bool:
    """Validate backup directory structure."""
    try:
        # Check if backup directory exists
        if not os.path.exists(backup_dir):
            print(f"Error: Backup directory does not exist: {backup_dir}")
            return False
        
        # Check for metadata file
        metadata_path = os.path.join(backup_dir, 'backup_history.json')
        if not os.path.exists(metadata_path):
            print(f"Error: Backup metadata file not found: {metadata_path}")
            return False
        
        # Check for backup archives
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith(('.zip', '.tar.gz', '.tgz'))]
        if not backup_files:
            print(f"Warning: No backup archives found in {backup_dir}")
        
        return True
    except Exception as e:
        print(f"Error validating backup structure: {e}")
        return False


def get_backup_info(backup_id: str, backup_dir: str) -> Optional[Dict]:
    """Get detailed information about a specific backup."""
    try:
        metadata_path = os.path.join(backup_dir, 'backup_history.json')
        
        if not os.path.exists(metadata_path):
            print(f"Error: Backup metadata file not found: {metadata_path}")
            return None
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Find backup by ID
        for backup_entry in metadata.get('backups', []):
            if backup_entry.get('backup_id') == backup_id:
                return backup_entry
        
        print(f"Error: Backup ID {backup_id} not found")
        return None
    except Exception as e:
        print(f"Error getting backup info: {e}")
        return None


def list_backups(backup_dir: str) -> List[Dict]:
    """List all available backups."""
    try:
        metadata_path = os.path.join(backup_dir, 'backup_history.json')
        
        if not os.path.exists(metadata_path):
            print(f"Error: Backup metadata file not found: {metadata_path}")
            return []
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return metadata.get('backups', [])
    except Exception as e:
        print(f"Error listing backups: {e}")
        return []


def check_backup_integrity(backup_id: str, backup_dir: str) -> Dict[str, bool]:
    """Perform comprehensive backup integrity check."""
    integrity_results = {
        'metadata_valid': False,
        'files_exist': False,
        'structure_valid': False,
        'overall_valid': False
    }
    
    try:
        metadata_path = os.path.join(backup_dir, 'backup_history.json')
        
        # Check metadata validity
        integrity_results['metadata_valid'] = verify_backup_metadata(metadata_path)
        
        # Check file existence
        file_verification = verify_backup_files(metadata_path)
        integrity_results['files_exist'] = all(file_verification.values())
        
        # Check structure
        integrity_results['structure_valid'] = validate_backup_structure(backup_dir)
        
        # Overall validity
        integrity_results['overall_valid'] = all([
            integrity_results['metadata_valid'],
            integrity_results['files_exist'],
            integrity_results['structure_valid']
        ])
        
        return integrity_results
    except Exception as e:
        print(f"Error checking backup integrity: {e}")
        return integrity_results
