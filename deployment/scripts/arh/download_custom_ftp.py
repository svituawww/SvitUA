#!/usr/bin/env python3
"""
id_part2 Implementation: Test Delete/Cleanup Functionality
Tests file transfer and deletion capabilities as specified in id_part2
"""

import os
import sys
import time
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from deployment_manager import DeploymentManager



def individual_delete_methods():

    list_of_files_to_download = [
        "/test.svitua.se/public_html/index.php",
        "/test.svitua.se/public_html/.htaccess"        
    ]

    local_dir = "/Users/nirsixadmin/Desktop/SvitUA/deployment/backups/wordpress/test.svitua.se/public_html/"    

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)



    """Test 2: Test individual download methods"""
    print("    Testing Individual Download Methods")
    
    try:
        # Initialize deployment manager
        config_file = 'config/deployment_config.yaml'
        manager = DeploymentManager(config_file)
        
        # Test with development environment
        environment = 'development'
        print(f"\n1. Connecting to {environment}...")
        
        if not manager.connect(environment):
            print(f"✗ Failed to connect to {environment}")
            return False
        
        print(f"✓ Connected to {environment}")



        
        # Test individual file deletion


        print(f"\n4. Testing individual file download...")

        for file in list_of_files_to_download:
            # Extract just the filename from the remote path
            filename = os.path.basename(file)
            local_file_path = os.path.join(local_dir, filename)
            
            if manager.transfer.download_file(file, local_file_path):
                print(f"✓ {file} downloaded successfully to {local_file_path}")
            else:
                print(f"✗ {file} download failed")        



        
        
        
        
        # Disconnect
        manager.transfer.disconnect()
        print("✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False


def demonstrate_log_output():
    """Show expected log output for delete operations"""
    print("\n" + "=" * 70)
    print("    Expected Log Output for Delete Operations")
    print("=" * 70)
    
    log_examples = [
        {
            'operation': 'File Upload',
            'logs': [
                'INFO - Uploaded: test/test_delete.txt -> /test_delete_20250805_165430/test_delete.txt'
            ]
        },
        {
            'operation': 'File Deletion',
            'logs': [
                'INFO - Deleted file: /test_delete_20250805_165430/test_delete.txt'
            ]
        },
        {
            'operation': 'Directory Cleanup',
            'logs': [
                'INFO - Cleaning up test files in /test_delete_20250805_165430',
                'INFO - Deleted file: /test_delete_20250805_165430/test_file1.txt',
                'INFO - Deleted file: /test_delete_20250805_165430/test_file2.txt',
                'INFO - Deleted directory: /test_delete_20250805_165430',
                'INFO - Cleanup completed: 2 files, 1 directories'
            ]
        },
        {
            'operation': 'Error Handling',
            'logs': [
                'ERROR - File deletion failed for /non_existent_file.txt: 550 Could not delete file',
                'WARNING - Could not delete directory: /non_empty_directory (expected if not empty)'
            ]
        }
    ]
    
    for example in log_examples:
        print(f"\n{example['operation']}:")
        for log in example['logs']:
            print(f"  {log}")


def show_test_summary():
    """Show summary of what id_part2 tests"""
    print("\n" + "=" * 70)
    print("    id_part2 Test Summary")
    print("=" * 70)
    
    tests = [
        {
            'test': '1. File Transfer Test',
            'description': 'Upload test_delete.txt to server',
            'method': 'FileTransfer.upload_file()',
            'expected': 'File uploaded successfully'
        },
        {
            'test': '2. File Verification Test',
            'description': 'Verify file exists on server',
            'method': 'FileTransfer connection listing',
            'expected': 'File found in directory listing'
        },
        {
            'test': '3. File Deletion Test',
            'description': 'Delete test_delete.txt from server',
            'method': 'FileTransfer.delete_file()',
            'expected': 'File deleted successfully'
        },
        {
            'test': '4. Deletion Verification Test',
            'description': 'Verify file has been removed',
            'method': 'FileTransfer connection listing',
            'expected': 'File not found in directory listing'
        },
        {
            'test': '5. Directory Cleanup Test',
            'description': 'Clean up test directory',
            'method': 'DeploymentManager.cleanup_test_files()',
            'expected': 'Directory and contents removed'
        }
    ]
    
    for test in tests:
        print(f"\n{test['test']}")
        print(f"   Description: {test['description']}")
        print(f"   Method: {test['method']}")
        print(f"   Expected: {test['expected']}")


def main():    

    print("    Individual Delete Methods")    
    
    if individual_delete_methods():
        print("\n✓ Individual Delete Methods completed successfully")
    else:
        print("\n✗ Individual Delete Methods failed")
        return    


if __name__ == '__main__':
    main() 