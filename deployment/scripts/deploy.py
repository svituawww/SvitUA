#!/usr/bin/env python3
"""
Main Deployment Script for Loopia.se Hosting
Command-line interface for deployment automation
"""

import argparse
import re
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import hashlib
import fnmatch
import yaml





class MainDeploymentManager:
    def __init__(self):        
        self.config = self.init_yaml_class()
        self.logger = self.init_logger_class()                
        self.db_manager = self.init_db_manager_class()
        self.db_compare = self.init_db_compare_class()
        self.ftr = self.init_ftp_class()
        
    def init_db_manager_class(self):
        """Initialize database"""
        # Import db_manager - now in same directory
        from db_manager import DP_DB_Manager
        db_manager = DP_DB_Manager()
        return db_manager
    
    def init_db_compare_class(self):
        """Initialize database for comparison"""
        # Import db_compare - now in same directory
        from db_compare import DB_Compare
        db_compare = DB_Compare()
        return db_compare

    def init_yaml_class(self):
        """Initialize YAML configuration"""
        from config_yaml import ConfigYAML
        yaml_config = ConfigYAML()
        return yaml_config
    
    def init_logger_class(self):
        """Initialize Logger"""
        from logger import Logger        
        deployment_log_path = self.config.constants.get('deployment_log_path')
        return Logger(deployment_log_path)
    
    def init_ftp_class(self):
        """Initialize FTP class"""
        from ftp_class import FileTransfer
        ftr = FileTransfer()
        return ftr

    def print_deb(self, id_function: int, message):
        if id_function is not None and self.db_manager.get_settings_for_print_deb_by_id(id_function) == 1:
          print(message)

    def print_err(self, message):
        print(message)


    def get_works_config(self, id_work: str) -> dict:
        return self.config.get_id_work_config(id_work)
    
      

    def generate_ftp_file_lists_from_db(self, id_work_config: dict) -> dict:
        """Generate FTP file lists from database."""                
        id_prev_snapshot_ref = id_work_config.get('id_prev_snapshot_ref')
        ftp_dest_path = id_work_config.get('destination')
        root_local_path = id_work_config.get('source')
        deploy_list = self.db_manager.get_deploy_list(id_prev_snapshot_ref)
        deploy_list_dict = {
            'copy_list': [],            
            'delete_list': []
        }
        for item_local in deploy_list:            
            item_local_path, dir_or_file, item_action = item_local
            
            # Determine action based on the values
            if item_action == 'Replace' or item_action == 'New':
                item_action = 'Replace'
            elif item_action == 'Delete':
                item_action = 'Delete'
            else:
                item_action = 'Unknown'
            
            # exctract relative path from file_path
            item_local_rel_path = extract_relative_path(item_local_path, root_local_path)
            item_ftp_path = os.path.join(ftp_dest_path, item_local_rel_path)

            if item_action == 'Replace' or item_action == 'New':
                deploy_list_dict['copy_list'].append({
                    'from': item_local_path,
                    'to': item_ftp_path,
                    'dir_or_file': dir_or_file
                })
            elif item_action == 'Delete':
                deploy_list_dict['delete_list'].append({'delete': item_ftp_path, 'dir_or_file': dir_or_file})

        return deploy_list_dict

    def print_deploy_list(self, id_work: str):
        # Generate FTP file lists from database        
        try:            
            id_work_config = self.get_works_config(id_work)
            deploy_list_dict = self.generate_ftp_file_lists_from_db(id_work_config)
            for item in deploy_list_dict['copy_list']:
                # print(f"✓ copy from: {item['from']}")
                print(f"✓ copy to: {item['to']} {item['dir_or_file']}")
            print()
            for item in deploy_list_dict['delete_list']:
                print(f"✓ Delete: {item['delete']} {item['dir_or_file']}")
        except Exception as e:
            print(f"✗ Error generating FTP file lists: {str(e)}")
            return False
    
    def save_deploy_list_to_json(self, id_work: str) -> bool:
        # Save deploy list to JSON file in log directory
        try:
            id_work_config = self.get_works_config(id_work)
            deploy_list_dict = self.generate_ftp_file_lists_from_db(id_work_config)
            jsondata = {
                'copy_list': {
                    'files': [],
                    'dirs': []
                },
                'delete_list': deploy_list_dict['delete_list']
            }
            for item in deploy_list_dict['copy_list']:
                if item['dir_or_file'] == 'file':                    
                    jsondata['copy_list']['files'].append({
                        'from': item['from'],
                        'to': item['to']
                    })
                elif item['dir_or_file'] == 'dir':
                    jsondata['copy_list']['dirs'].append({
                        'from': item['from'],
                        'to': item['to']
                    })

            # Sort directories by hierarchy in JSON data
            dirs = [i for i in deploy_list_dict['copy_list'] if i.get('dir_or_file') == 'dir']
            jsondata['copy_list']['dirs'] = sorted(dirs, key=lambda d: d.get('to', '').count('/'))
            # Save to JSON file    
            file_path_output_ftp_list = id_work_config.get('output_json_ftp_list')
            with open(file_path_output_ftp_list, 'w') as f:
                json.dump(jsondata, f, indent=4)
            return True
        except Exception as e:
            print(f"✗ Error saving deploy list to JSON: {str(e)}")
            return False


    def ftp_upload_execute(self, id_work: str) -> bool:
        def get_input_ftp_list_data() -> dict:
            id_work_config = self.get_works_config(id_work)
            file_path_input_ftp_list = id_work_config.get('input_json_ftp_list')
            with open(file_path_input_ftp_list, 'r') as f:
                return json.load(f)
            
        def ifnot_exists_create_dir():
            id_work_config = self.get_works_config(id_work)
            ftp_dest_path = id_work_config.get('destination')            
            if not self.ftr.exists_file_dir(ftp_dest_path):
                print(f"Creating base FTP directory: {ftp_dest_path}")
                self.ftr.create_directory(ftp_dest_path)

        # Execute FTP upload work automatically without user interaction.
        try:
            self.ftr.connect()
            # ifnot_exists_create_dir() # create FTP base directory if not exists
            deploy_list_dict = get_input_ftp_list_data()
            
            # First create directories, then upload files, then delete files/dirs
            dirs = deploy_list_dict['copy_list']['dirs']
            for item in dirs:
                print(f"Creating directory: {item['to']}")
                self.ftr.create_directory(item['to'])

            for item in deploy_list_dict['copy_list']['files']:
                print(f"Uploading file: {item['from']} to {item['to']}")
                self.ftr.upload_file(item['from'], item['to'])
        
            for item in deploy_list_dict['delete_list']:
                print(f"Deleting: {item['delete']}")
                if item['dir_or_file'] == 'file':
                    self.ftr.delete_file(item['delete'])
                elif item['dir_or_file'] == 'dir':
                    self.ftr.delete_directory(item['delete'])

            self.ftr.disconnect()
            return True
        except Exception as e:
            print(f"✗ Error in def ftp_upload_execute: {str(e)}")
            return False


    def upload_execute(self, id_work: str):
        def check_subwork_and_execute():
            try:
                id_subwork = self.get_works_config(id_work).get('id_subwork')
                if id_subwork:
                    # Validate subwork reference
                    try:
                        self.config.validate_subwork_reference(id_subwork)
                    except Exception as e:
                        print(f"✗ Subwork reference validation failed: {str(e)}")
                        exit(1)
                    # Execute subwork first (automatically, no user interaction)                
                    print("EXECUTING SUBWORK (automatic)")                
                    if not self.scan_execute(id_subwork):
                        raise Exception("Subwork execution failed")                        
            except Exception as e:
                print(f"✗ Error in def check_subwork_and_execute : {str(e)}")
                return False

        # Execute upload work automatically without user interaction.
        try:
            response = input("Do you want to execute UPLOAD work (including subwork)? (Y/N): ").strip().upper()
            if response != 'Y':
                print("Work cancelled by user.")
                return False
            check_subwork_and_execute()
            # After subwork completion work upload work 
            self.ftp_upload_execute(id_work) 
            print("* * * * * * FTP UPLOAD WORK COMPLETED * * * * * *")
            return True
        except Exception as e:
            print(f"✗ Error executing upload work: {str(e)}")
            return False
    
    def scan_execute(self, id_work: str):
        # Execute scan work automatically without user interaction.
        try:
            print(f"Scan Execution: {id_work}")
            print("=" * 50)
            source = self.get_works_config( id_work).get('source')
            exclude_patterns = self.get_works_config(id_work).get('exclude_patterns', default_exclude_patterns())
            current_snapshot = self.create_snapshot(source, exclude_patterns, id_work)
            if not current_snapshot:
                print("✗ Error: Failed to create snapshot")
                return False
            self.print_deploy_list(id_work)
            self.save_deploy_list_to_json(id_work)
            return True

        except Exception as e:
            print(f"✗ Error executing scan work: {str(e)}")
            return False   
           


    def execute_work(self, id_work: str) -> bool:
        """Execute work by id_work with interactive confirmation and optional subwork execution."""
        try:            
            works_config = self.get_works_config(id_work)            

            work_type = works_config.get('typeof_work')
            if work_type == 'upload':
              return self.upload_execute(id_work)
            elif work_type == 'scan':
                return self.scan_execute(id_work)
            elif work_type == 'compare':
                return self.compare_execute(id_work)
            else:
                print(f"✗ Error: Work '{id_work}' is of type '{work_type}' but has no subwork. Only 'scan' type works can execute standalone.")
                return False           
                
        except Exception as e:
            print(f"✗ Error executing work: {str(e)}")
            return False
        


    def create_snapshot(self, source_dir: str, exclude_patterns: list = None, id_work: str = None) -> bool:
        """Create a snapshot. Save snapshot to database.
        """
        source_dir = os.path.abspath(source_dir)
        excludes = exclude_patterns if exclude_patterns else default_exclude_patterns()
        all_items = scan_directory(source_dir, excludes)
        snapshot_id = self.db_manager.add_snapshot_ref(id_work)
        id_record = 0

        for item in all_items:
            item_full_path, item_type = item
            id_record += 1
            try:
                if item_type == "file":
                    sha256 = compute_sha256(item_full_path)
                    stat = os.stat(item_full_path)
                    fname = os.path.basename(item_full_path)
                    item_size = stat.st_size
                    dir_or_file = "file"
                    self.db_manager.add_file_to_db(item_full_path, fname, sha256, item_size, snapshot_id, id_record, dir_or_file)                
                elif item_type == "dir":
                    dirname = os.path.basename(item_full_path)
                    item_size = 0
                    sha256 = ''
                    dir_or_file = "dir"
                    self.db_manager.add_file_to_db(item_full_path, dirname, sha256, item_size, snapshot_id, id_record, dir_or_file)
            except Exception as e:
                print(f"Error adding {item_full_path} to database: {e}")
                return False
        return True   


    def print_banner(self):
        """Print deployment banner"""
        function_description = """Print deployment banner"""    
        function_name = "print_banner"
        self.db_manager.store_in_db_settings_for_print_deb(function_name, function_description, 0)
        idf = self.db_manager.get_id_function_for_print_deb(function_name)
        self.print_deb(idf, "=" * 60)
        self.print_deb(idf, "           Loopia.se Deployment Automation")
        self.print_deb(idf, "=" * 60)
        self.print_deb(idf, f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_deb(idf, "")

    def print_deployment_info(self, args):
        """Print deployment information"""
        function_description = """Print deployment information"""    
        function_name = "print_deployment_info"
        self.db_manager.store_in_db_settings_for_print_deb(function_name, function_description, 1)
        idf = self.db_manager.get_id_function_for_print_deb(function_name)

        # self.print_deb(idf, "Deployment Configuration:")
        if args.list_works:
            self.print_deb(idf, "  Mode: LIST WORKS (local-only)")
            self.print_deb(idf, f"  Config: {args.config}")
        elif args.idwork:            
            self.print_deb(idf, f"  Work ID: {args.idwork}")

    def dialog_menu_select_work(self):
        """Dialog menu to select work"""
        works = self.config.menu_list_available_works()
        if not works:
            print("No works configured in the configuration file.")
            return None
        print("\n" + "=" * 50)
        print("Select Work by number or 0 to exit:")
        for work in works:
            print(f"[{work['menu_index']}] {work['id_work']}     - {work['description']}")
        while True:
            try:
                choice = int(input("Input <number>: "))
                if choice == 0:
                    return None
                selected_work = next((w for w in works if w['menu_index'] == choice), None)
                if selected_work:
                    return selected_work['id_work']
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def compare_execute(self, id_work: str):
        # Execute compare work automatically without user interaction.
        try:
            print(f"Compare Execution: {id_work}")
            print("=" * 50)
            source = self.get_works_config(id_work).get('source')
            destination = self.get_works_config(id_work).get('destination')
            tmpsavedir = self.get_works_config(id_work).get('tmpsavedir')
            exclude_patterns = self.get_works_config(id_work).get('exclude_patterns', default_exclude_patterns())
            not_download_to_tmp = self.get_works_config(id_work).get('not_download_to_tmp', False)
            if not not_download_to_tmp:
                self.download_files_for_compare(destination, tmpsavedir, exclude_patterns)
            self.save_compare_deploy_list_to_json(id_work)


            # source_snapshot_id = self.create_snapshot_compare(source, exclude_patterns)
            # destination_snapshot_id = self.create_snapshot_compare(tmpsavedir, exclude_patterns)

        except Exception as e:
            print(f"✗ Error in def compare_execute: {str(e)}")


    def compare_file_lists_from_db(self, source_path, destination_path, source_snapshot_id, destination_snapshot_id) -> dict:
        """Compare file lists from database."""
        # id_prev_snapshot_ref = id_work_config.get('id_prev_snapshot_ref')
        # ftp_dest_path = id_work_config.get('destination')
        ftp_dest_path = destination_path
        root_local_path = source_path
        deploy_list = self.db_compare.get_deploy_list(source_snapshot_id, destination_snapshot_id)
        deploy_list_dict = {
            'copy_list': [],            
            'delete_list': []
        }
        for item_local in deploy_list:            
            item_local_path, dir_or_file, item_action = item_local
            
            # Determine action based on the values
            if item_action == 'Replace' or item_action == 'New':
                item_action = 'Replace'
            elif item_action == 'Delete':
                item_action = 'Delete'
            else:
                item_action = 'Unknown'
            
            # exctract relative path from file_path
            item_local_rel_path = extract_relative_path(item_local_path, root_local_path)
            item_ftp_path = os.path.join(ftp_dest_path, item_local_rel_path)

            if item_action == 'Replace' or item_action == 'New':
                deploy_list_dict['copy_list'].append({
                    'from': item_local_path,
                    'to': item_ftp_path,
                    'dir_or_file': dir_or_file
                })
            elif item_action == 'Delete':
                deploy_list_dict['delete_list'].append({'delete': item_ftp_path, 'dir_or_file': dir_or_file})

        return deploy_list_dict

    def create_snapshot_compare(self, source_dir: str, replace_dict: dict = None, exclude_patterns: list = None) -> int:
        """Create a for comparison snapshot. Save snapshot to database.
        """
        source_dir = os.path.abspath(source_dir)
        excludes = exclude_patterns if exclude_patterns else default_exclude_patterns()
        all_items = scan_directory(source_dir, excludes)
        snapshot_id = self.db_compare.add_snapshot_ref(source_dir)
        id_record = 0

        for item in all_items:
            item_full_path, item_type = item
            if replace_dict:                        
                item_full_path_rrr = item_full_path.replace(replace_dict['from'], replace_dict['to'])
            id_record += 1
            try:
                if item_type == "file":
                    sha256 = compute_sha256(item_full_path)
                    stat = os.stat(item_full_path)
                    fname = os.path.basename(item_full_path)
                    item_size = stat.st_size
                    dir_or_file = "file"
                    self.db_compare.add_file_to_db(item_full_path_rrr, fname, sha256, item_size, snapshot_id, id_record, dir_or_file)                
                elif item_type == "dir":
                    dirname = os.path.basename(item_full_path)
                    item_size = 0
                    sha256 = ''
                    dir_or_file = "dir"
                    self.db_compare.add_file_to_db(item_full_path_rrr, dirname, sha256, item_size, snapshot_id, id_record, dir_or_file)
            except Exception as e:
                print(f"Error adding {item_full_path} to database: {e}")
                return None
        # Return the snapshot identifier so downstream functions can use it
        return snapshot_id


    def download_files_for_compare(self, destination: str, tmpsavedir: str, exclude_patterns: list) -> bool:
        try:
            self.ftr.connect()
            items_to_download = self.ftr.get_all_files_and_dirs_recursive(destination, exclude_patterns)
            # for dir_path in items_to_download.get('dirs', []):
            #     print(f"Dir: {dir_path}")
        
            # for file_path in items_to_download.get('files', []):
            #     print(f"File: {file_path}")
            

            # exit() 


            for dir_path in items_to_download.get('dirs', []):
                # Determine local path
                rel_path = extract_relative_path(dir_path, destination)
                local_path = os.path.join(tmpsavedir, rel_path)
                os.makedirs(local_path, exist_ok=True)

            for file_path in items_to_download.get('files', []):
                # Determine local path
                rel_path = extract_relative_path(file_path, destination)
                local_path = os.path.join(tmpsavedir, rel_path)
                local_dir = os.path.dirname(local_path)
                # Ensure local directory exists
                os.makedirs(local_dir, exist_ok=True)
                print(f"Downloading file: {file_path} to {local_path}")
                self.ftr.download_file(file_path, local_path)
            self.ftr.disconnect()
            return True
        except Exception as e:
            print(f"✗ Error downloading files for compare: {str(e)}")
            return False
        

    def save_compare_deploy_list_to_json(self, id_work: str) -> bool:
        # Save deploy list to JSON file in log directory
        try:
            source = self.get_works_config(id_work).get('source')            
            tmpsavedir = self.get_works_config(id_work).get('tmpsavedir')
            destination = self.get_works_config(id_work).get('destination')
            exclude_patterns = self.get_works_config(id_work).get('exclude_patterns', default_exclude_patterns())
            replace_dict = {'from': tmpsavedir, 'to': source}
            source_snapshot_id = self.create_snapshot_compare(source, replace_dict, exclude_patterns)
            destination_snapshot_id = self.create_snapshot_compare(tmpsavedir, replace_dict, exclude_patterns)
            deploy_list_dict = self.compare_file_lists_from_db(source, destination, source_snapshot_id, destination_snapshot_id)
            jsondata = {
                'copy_list': {
                    'files': [],
                    'dirs': []
                },
                'delete_list': deploy_list_dict['delete_list']
            }
            for item in deploy_list_dict['copy_list']:
                if item['dir_or_file'] == 'file':                    
                    jsondata['copy_list']['files'].append({
                        'from': item['from'],
                        'to': item['to']
                    })
                elif item['dir_or_file'] == 'dir':
                    jsondata['copy_list']['dirs'].append({
                        'from': item['from'],
                        'to': item['to']
                    })

            # Sort directories by hierarchy in JSON data
            dirs = [i for i in deploy_list_dict['copy_list'] if i.get('dir_or_file') == 'dir']
            jsondata['copy_list']['dirs'] = sorted(dirs, key=lambda d: d.get('to', '').count('/'))
            # Save to JSON file    
            file_path_output_ftp_list = self.get_works_config(id_work).get('output_json_ftp_list')
            with open(file_path_output_ftp_list, 'w') as f:
                json.dump(jsondata, f, indent=4)
            return True
        except Exception as e:
            print(f"✗ Error saving deploy list to JSON: {str(e)}")
            return False



# ------------------------------------------------------------
#  END OF CLASS MainDeploymentManager
# ------------------------------------------------------------




def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Deployment automation script for Loopia.se hosting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available works from configuration
  python deploy.py --list-works
  
  # Execute work with interactive confirmation
  python deploy.py --idwork=upload_cms_php_custom  
        """
    )   

    # YAML-driven action commands (local-only)
    parser.add_argument(
        '--list-works',
        action='store_true',
        help='List all available works from configuration'
    )
    parser.add_argument(
        '--idwork',
        help='Execute work by id_work key (e.g., --idwork=upload_cms_php_custom)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='../config/deployment_config.yaml',
        help='Configuration file path (default: ../config/deployment_config.yaml)'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Validate command line arguments"""

    # YAML-driven action mode
    if args.list_works:
        # Config required for listing works
        if not os.path.exists(args.config):
            print(f"Error: Configuration file '{args.config}' does not exist")
            return False
        return True

    if args.idwork:
        # Config required for idwork execution
        if not os.path.exists(args.config):
            print(f"Error: Configuration file '{args.config}' does not exist")
            return False
        return True    
    
    if not os.path.exists(args.config):
        print(f"Error: Configuration file '{args.config}' does not exist")
        return False
    
    return True




def compute_sha256(file_path: str, max_bytes: int = None) -> str:
    """Compute SHA-256 hash of a file (optionally limited to max_bytes)."""
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        if max_bytes is None:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        else:
            remaining = max_bytes
            while remaining > 0:
                chunk = f.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                h.update(chunk)
                remaining -= len(chunk)
    return h.hexdigest()

def custom_d1_compute_sha256(file_path: str,  max_bytes: int = None) -> str:
    """Compute SHA-256 hash of a file (optionally limited to max_bytes).
    but first delete string like
    "generated_at": "2025-08-22T13:19:59Z",
    from the file and then compute hash
    """

    regexp1 = r'"generated_at": ".*Z",'
    file_content = open(file_path, 'r').read()
    file_content = re.sub(regexp1, '', file_content)
    temp_file_path = file_path + '.temp'
    with open(temp_file_path, 'w') as f:
        f.write(file_content)    

    h = hashlib.sha256()
    with open(temp_file_path, 'rb') as f:
        if max_bytes is None:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        else:
            remaining = max_bytes
            while remaining > 0:
                chunk = f.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                h.update(chunk)
                remaining -= len(chunk)
    os.remove(temp_file_path)
    return h.hexdigest()


def get_snapshots_log_path(log_dir: str) -> str:
    """Get the path to snapshots_log.json file."""
    return os.path.join(log_dir, 'snapshots_log.json')


def generate_timestamped_filename(id_work: str, file_type: str) -> str:
    """Generate timestamped filename for snapshot or diff files."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f"{timestamp}_{file_type}_{id_work}.json"



def default_exclude_patterns() -> list:
    """Default exclude patterns for snapshotting (local-only)."""
    return [
        '.git/', '**/.git/**',
        'backups/**', 'backupwww/**', 'deployment/logs/**',
        '**/*.tmp', '**/*.log', 'logs/**',
        'svitua_py_env/**', 'node_modules/**', '__pycache__/', '*.pyc', '.DS_Store', 'Thumbs.db',
        'ptb_parser/output/**', 'svituawww.github.io/output/**'
    ]


def path_matches_any_pattern(name: str, patterns: list) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def should_exclude(path: str, rel_path: str, is_dir: bool, patterns: list) -> bool:
    # Check directory-style and file-style patterns
    parts = rel_path.replace('\\', '/').split('/')
    # Check each segment against patterns
    if any(path_matches_any_pattern(seg + ('/' if is_dir else ''), patterns) for seg in parts):
        return True
    # Check full relative path
    if path_matches_any_pattern(rel_path, patterns):
        return True
    return False





def load_json(path_str: str) -> dict:
    with open(path_str, 'r') as f:
        return json.load(f)


def index_by_hash_and_size(files: list) -> dict:
    index = {}
    for f in files:
        key = (f.get('sha256'), f.get('size_bytes'))
        index.setdefault(key, []).append(f)
    return index


def extract_relative_path(full_path: str, base_path: str) -> str:
    """Extract relative path from full path based on base path."""
    try:
        full_path = os.path.abspath(full_path)
        base_path = os.path.abspath(base_path)
        if not full_path.startswith(base_path):
            raise ValueError(f"Full path '{full_path}' does not start with base path '{base_path}'")
        relative_path = os.path.relpath(full_path, base_path)
        return relative_path
    except Exception as e:
        raise Exception(f"Failed to extract relative path: {str(e)}")



def scan_directory_tree(root_path: str, excludes: list):
    """
    Recursively scan directory tree and return all files and directories.
    Returns a list of absolute paths for all items in the tree.
    """
    all_items = []
    
    def scan_recursive(current_path: str):
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                rel_path = os.path.relpath(item_path, root_path)
                
                # Check if this item should be excluded
                if should_exclude(item_path, rel_path, os.path.isdir(item_path), excludes):
                    continue
                    
                if os.path.isdir(item_path):
                    all_items.append((item_path, "dir"))
                    # Recursively scan the subdirectory
                    scan_recursive(item_path)
                else:
                    all_items.append((item_path, "file"))
                
        except PermissionError:
            print(f"⚠️ Permission denied: {current_path}")
        except Exception as e:
            print(f"⚠️ Error scanning {current_path}: {e}")
    
    scan_recursive(root_path)
    return all_items



def scan_directory(root_path: str, excludes: list):
    #scan for subdirectories and files
    all_items = scan_directory_tree(root_path, excludes)
    return all_items

def test_scan_directory():
    try:
        with open('../config/deployment_config.yaml', 'r') as f:
            config = yaml.safe_load(f)       
        root_path = config['subwork_scan_aat1']['source']
        excludes = config['subwork_scan_aat1']['exclude_patterns']        
        all_items = scan_directory(root_path, excludes)
        for item in all_items:
            item_path, item_type = item
            rel_item_path = extract_relative_path(item_path, root_path)
            print(f"{item_type}: {rel_item_path}")
            # print(f"{item_type}: {item_path}")
        
    except Exception as e:
        print(f"✗ Error scanning directory: {str(e)}")
        exit()



def main():
    """Main function"""
    # Parse arguments
    args = parse_arguments()
    
    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)
    
    # Initialize MainDeploymentManager with config file
    manager = MainDeploymentManager()
    
    # Print banner and deployment info
    manager.print_banner()    
    manager.print_deployment_info(args)

    #validate configuration
    try:
        manager.config.validate_configuration()
    except Exception as e:
        print(f"✗ Configuration validation failed: {str(e)}")
        sys.exit(1)

    # Interactive work selection if no idwork provided
    work_id = manager.dialog_menu_select_work() 
    # print(f"Selected work: {work_id}")
    if work_id:
        manager.config.validate_work_type_config(work_id)
        if not manager.execute_work(work_id):
            sys.exit(1)
    else:
        print("No work selected. Exiting.")
        exit()

    # YAML-driven action modes
    # if args.list_works:        
    #     manager.config.list_available_works()
    #     return
  

    # #!!!TESTING!!!
    # test_scan_directory()
    # exit()
    # #END OF TESTING!!!    

    # if args.idwork:
    #     manager.config.validate_work_type_config(args.idwork)
    #     if not manager.execute_work(args.idwork):
    #         sys.exit(1)
    #     return    


if __name__ == '__main__':
    main() 