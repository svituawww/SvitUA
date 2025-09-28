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
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from deployment_manager import DeploymentManager



def individual_upload_methods():

    list_of_dirs_to_upload = [
        { "local_path": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1",
          "ftp_remote_path": "/test.svitua.se/public_html/uploads1"
        }
    ]

    list_of_files_to_upload = [
        # { "local_path": "/Users/nirsixadmin/Desktop/SvitUA/cms_php_custom/.htaccess",
        #   "ftp_remote_path": "/test.svitua.se/public_html/.htaccess"
        # }
        # ,
        # { "local_path": "/Users/nirsixadmin/Desktop/SvitUA/cms_php_custom/simple_html/pages/index.html",
        #   "ftp_remote_path": "/test.svitua.se/public_html/simple_html/pages/index.html"
        # }

        { 
            "local_path": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1/2025/06/logo_120x120.png",
            "ftp_remote_path": "/test.svitua.se/public_html/uploads1/2025/06/logo_120x120.png"
        }
    ]




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


        print(f"\n4. Testing individual file upload...")
        error_i = 0
        success_i = 0

        for dir in list_of_dirs_to_upload:
            local_path = dir["local_path"]
            ftp_remote_path = dir["ftp_remote_path"]

            if manager.transfer.upload_dir(local_path, ftp_remote_path):
                print(f"✓ {local_path}")
                print(f"✓ uploaded successfully to \n {ftp_remote_path}")
                success_i += 1
            else:
                print(f"✗ {local_path}")
                print(f"✗ upload failed")
                error_i += 1
                print(f"✗ {local_path}")
                print(f"✗ upload failed")
                error_i += 1 

        print(f"\n✓ {success_i} dirs uploaded successfully")
        print(f"✗ {error_i} dirs upload failed")

        for file in list_of_files_to_upload:
    
            local_path = file["local_path"]
            ftp_remote_path = file["ftp_remote_path"]

            if manager.transfer.upload_file(local_path, ftp_remote_path):
                print(f"✓ {local_path}")
                print(f"✓ uploaded successfully to \n {ftp_remote_path}")
                success_i += 1
            else:
                print(f"✗ {local_path}")
                print(f"✗ upload failed")
                error_i += 1

        print(f"\n✓ {success_i} files uploaded successfully")
        print(f"✗ {error_i} files upload failed")

   
        
        
        
        # Disconnect
        manager.transfer.disconnect()
        print("✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False





def upload__uploads1___to_ftp():

    # Initialize deployment manager
    config_file = '/Users/nirsixadmin/Desktop/SvitUA/deployment/config/deployment_config.yaml'
    manager = DeploymentManager(config_file)
    
    # Test with development environment
    environment = 'development'
    print(f"\n1. Connecting to {environment}...")
    
    if not manager.connect(environment):
        print(f"✗ Failed to connect to {environment}")
        return False
    
    print(f"✓ Connected to {environment}")

    list_of_dirs_to_upload = {
         "local_path": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1",
          "ftp_remote_path": "/test.svitua.se/public_html/uploads1"
    }
    

    # scan dir /Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1
    # and upload to ftp /test.svitua.se/public_html/uploads1
    # use deployment_manager.py
    # use upload_dir method
    # use upload_file method
    # if sub_dir not exists, create it    
    # if file exists, overwrite it
    # scan dir /Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1 for each file and sub_dir



    all_items = scan_directory_tree(list_of_dirs_to_upload["local_path"])

    error_i = 0
    success_i = 0
    
    print(f"\n📁 Found {len(all_items)} items in directory tree:")
    for item_path, item_type in all_items:        
        # print(f"{item_type}    {item_path}")     
        
        relative_path = os.path.relpath(item_path, list_of_dirs_to_upload["local_path"])
        ftp_path = os.path.join(list_of_dirs_to_upload['ftp_remote_path'], relative_path)
        print(f"   {item_type}: {relative_path}")
        print(f"   FTP Path: {ftp_path}")

        if item_type == "dir":
            if manager.transfer.upload_dir(item_path, ftp_path):
                print(f"✓ {item_path}")
                print(f"✓ uploaded successfully to \n {ftp_path}")
                success_i += 1
            else:
                print(f"✗ {item_path}")
                print(f"✗ upload failed")
                error_i += 1
        else:
            if manager.transfer.upload_file(item_path, ftp_path):
                print(f"✓ {item_path}")
                print(f"✓ uploaded successfully to \n {ftp_path}")
                success_i += 1
            else:
                print(f"✗ {item_path}")
                print(f"✗ upload failed")
                error_i += 1

    print(f"\n✓ {success_i} items uploaded successfully")
    print(f"✗ {error_i} items upload failed")

    manager.transfer.disconnect()
    print("✓ Connection closed")

    return True




def scan_directory_tree(root_path):
    """
    Recursively scan directory tree and return all files and directories.
    Returns a list of absolute paths for all items in the tree.
    """
    all_items = []
    
    def scan_recursive(current_path):
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    all_items.append((item_path, "dir"))
                else:
                    all_items.append((item_path, "file"))
                
                # If it's a directory, recursively scan it
                if os.path.isdir(item_path):
                    scan_recursive(item_path)
        except PermissionError:
            print(f"⚠️ Permission denied: {current_path}")
        except Exception as e:
            print(f"⚠️ Error scanning {current_path}: {e}")
    
    scan_recursive(root_path)
    return all_items


def main():    

    print("    Individual Upload Methods")    

    # if individual_upload_methods():
    #     print("\n✓ Individual Upload Methods completed successfully")
    # else:
    #     print("\n✗ Individual Upload Methods failed")
    #     return    

    if upload__uploads1___to_ftp():
        print("\n✓ upload__uploads1___to_ftp completed successfully")
    else:
        print("\n✗ upload__uploads1___to_ftp failed")
        return    


if __name__ == '__main__':
    main() 