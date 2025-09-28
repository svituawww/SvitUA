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

    # list_of_files_to_delete = [
    #     "/test.svitua.se/public_html/ftp_test.txt",
    #     "/test.svitua.se/public_html/DatabaseResearch.php",
    #     "/test.svitua.se/public_html/HostingEnvironment.php",
    #     "/test.svitua.se/public_html/PerformanceTester.php",
    #     "/test.svitua.se/public_html/README.md",
    #     "/test.svitua.se/public_html/SecurityAssessment.php",
    #     "/test.svitua.se/public_html/download_json.php",
    #     "/test.svitua.se/public_html/download_report.php",        
    #     "/test.svitua.se/public_html/loopia_research_results.json",
    #     "/test.svitua.se/public_html/research_web.php",
    #     "/test.svitua.se/public_html/run_research.php"
    # ]

    # list_of_dirs_to_delete = [
    #     "/test.svitua.se/public_html/test_delete_methods_20250805_171718"
    # ]

    list_of_files_to_delete = [    
        "/test.svitua.se/public_html/simple_html/assets/images/logo1.png"
    ]   

    list_of_dirs_to_delete = [
        "/test.svitua.se/public_html/json"
    ]



    
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


        print(f"\n4.Individual file deletion...")

        f_error_i = 0
        f_success_i = 0
        d_error_i = 0
        d_success_i = 0


        for file in list_of_files_to_delete:
            if manager.transfer.delete_file(file, environment):
                print(f"✓ {file} deleted successfully")
                f_success_i += 1
            else:
                print(f"✗ {file} deletion failed")        
                f_error_i += 1

        for dir in list_of_dirs_to_delete:
            if manager.transfer.delete_directory(dir, environment):
                print(f"✓ DIR {dir} deleted successfully")
                d_success_i += 1
            else:
                print(f"✗ DIR {dir} deletion failed")     
                d_error_i += 1

        print(f"\n")





        if f_success_i > 0:
            print(f"\n✓ {f_success_i} files deleted successfully")
        if f_error_i > 0:
            print(f"✗ {f_error_i} files deletion failed")
        if d_success_i > 0:
            print(f"\n✓ {d_success_i} directories deleted successfully")
        if d_error_i > 0:
            print(f"✗ {d_error_i} directories deletion failed")
        
        if f_success_i == 0 and f_error_i == 0 :
            print(f"\n✓ No files deleted")
        if d_success_i == 0 and d_error_i == 0:
            print(f"\n✓ No directories deleted")
        
        
        # Disconnect
        manager.transfer.disconnect()
        print("✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False

def scan_dir_for_subdir_and_files(dir_to_scan):  

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

        # get list of subdirs and files in dir_to_scan
        subdirs = manager.transfer.list_directory(dir_to_scan)
        files = manager.transfer.list_files(dir_to_scan)

        # save in dir_list.txt

        # save in dir_list.txt
        with open('dir_list.txt', 'w') as f:
            for subdir in subdirs:
                f.write(subdir + '\n')
            for file in files:
                f.write(file + '\n')

        # disconnect
        manager.transfer.disconnect()
        print("✓ Connection closed")

        return True

    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False
    
    
    


def main():    

    print("    Individual Delete Methods")    

    # first scan some dir for subdir and files in this dir in ftp and save in dir_list.txt
    # scan_dir_for_subdir_and_files("/test.svitua.se/public_html")
    
    if individual_delete_methods():
        print("\n✓ Individual Delete Methods completed successfully")
    else:
        print("\n✗ Individual Delete Methods failed")
        return    


if __name__ == '__main__':
    main() 