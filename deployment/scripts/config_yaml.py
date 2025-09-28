#!/usr/bin/env python3
"""
Module for handling configuration in YAML format.

"""

import yaml
import os



class ConfigYAML:
    def __init__(self, config_path: str = "/Users/nirsixadmin/Desktop/SvitUA/deployment/config/deployment_config.yaml"):
        self.config_path = config_path
        self.config = self.get_config()
        self.works_config = self.get_works()
        self.constants = self.get_constants()
        self.ftp_transfer_settings = self.get_ftp_transfer_settings()


    def get_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise Exception(f"Failed to load configuration: {str(e)}")
        
    def get_constants(self) -> dict:
        """Get constants from configuration."""
        try:
            config = self.config
            if 'constants' in config:
                return config['constants']
            else:
                raise ValueError("No 'constants' section found in configuration")
        except Exception as e:
            raise Exception(f"Failed to load constants configuration: {str(e)}") 
        
    def get_works(self) -> dict:
        """Get all works from configuration."""
        try:            
            config = self.config
            if 'works' in config:
                return config['works']
            else:
                raise ValueError("No 'works' section found in configuration")
        except Exception as e:
            raise Exception(f"Failed to load works configuration: {str(e)}")
    
    def get_ftp_transfer_settings(self) -> dict:
        """Get FTP transfer settings from configuration."""
        try:
            config = self.config
            if 'ftp_transfer_settings' in config:
                return config['ftp_transfer_settings']
            else:
                raise ValueError("No 'ftp_transfer_settings' section found in configuration")
        except Exception as e:
            raise Exception(f"Error in def get_ftp_transfer_settings: {str(e)}")
    
    def get_id_work_config(self, id_work: str) -> dict:
        """Get action configuration by id_work from YAML config."""
        try:            
            #open works section and find id_work
            config = self.config
            if 'works' in config:
                works_section = config['works']
                for key, value in works_section.items():
                    if isinstance(value, dict) and value.get('id_work') == id_work:
                        return value
                raise ValueError(f"Work '{id_work}' not found in works section")
            else:
                raise ValueError("No 'works' section found in configuration")
        except Exception as e:
            raise Exception(f"Failed to load work configuration: {str(e)}")

    def menu_list_available_works(self) -> list:
        def get_description_be_work_type(work_type: str) -> str:
            match work_type:
                case 'scan':
                    return self.constants.get('des_scan_work', 'scan')
                case 'upload':
                    return self.constants.get('des_upload_work', 'upload')
                case 'compare':
                    return self.constants.get('des_compare_work', 'compare')   
                case _:
                    return ''
        """Menu to list available works."""
        try:
            works_config = self.works_config
            works_found = []
            
            # Scan all top-level keys for work configurations
            i = 0
            for key, value in works_config.items():
                i += 1
                if isinstance(value, dict) and 'id_work' in value:
                    work_config = value
                    id_work = work_config.get('id_work', 'N/A')
                    work_type = work_config.get('typeof_work', 'unknown')
                    description = get_description_be_work_type(work_type)
                    works_found.append({
                        'id_work': id_work,
                        'work_type': work_type,
                        'description': description,
                        'menu_index': i
                    })
            if not works_found:
                return []
            else:
                return works_found
        except Exception as e:
            print(f"Error in def menu_list_available_works: {str(e)}")
    
    def list_available_works(self):
        """List all available works from configuration."""
        try:
            works_config = self.works_config
            works_found = []
            
            # Scan all top-level keys for work configurations
            for key, value in works_config.items():
                if isinstance(value, dict) and 'id_work' in value:
                    work_config = value
                    id_work = work_config.get('id_work', 'N/A')
                    work_type = work_config.get('typeof_work', 'unknown')
                    
                    # Initialize all variables with default values
                    exclude_patterns = 'N/A'
                    source = 'N/A'
                    destination = 'N/A'                    
                    id_subwork = 'N/A'
                    id_prev_snapshot_ref = 'N/A'
                    tmpsavedir = 'N/A'
                    input_json_ftp_list = 'N/A'
                    
                    # Get source and other details based on work type
                    if work_type == 'scan':
                        id_work = work_config.get('id_work', 'N/A')
                        exclude_patterns = work_config.get('exclude_patterns', 'N/A')
                        source = work_config.get('source', 'N/A')
                        destination = work_config.get('destination', 'N/A')
                        output_json_ftp_list = work_config.get('output_json_ftp_list', 'N/A')
                        id_prev_snapshot_ref = work_config.get('id_prev_snapshot_ref', 'N/A')
                    elif work_type == 'upload':
                        id_work = work_config.get('id_work', 'N/A')
                        id_subwork = work_config.get('id_subwork', 'N/A')
                        input_json_ftp_list = work_config.get('input_json_ftp_list', 'N/A')                        
                    elif work_type == 'compare':
                        id_work = work_config.get('id_work', 'N/A')
                        output_json_ftp_list = work_config.get('output_json_ftp_list', 'N/A')
                        exclude_patterns = work_config.get('exclude_patterns', 'N/A')
                        source = work_config.get('source', 'N/A')
                        destination = work_config.get('destination', 'N/A')
                        not_download_to_tmp = work_config.get('not_download_to_tmp', 'N/A')
                        tmpsavedir = work_config.get('tmpsavedir', 'N/A')

                        
                        
                    
                    works_found.append({
                        'id_work': id_work,
                        'work_type': work_type,                        
                        'exclude_patterns': exclude_patterns,                        
                        'source': source,
                        'destination': destination,
                        'id_subwork': id_subwork,
                        'input_json_ftp_list': input_json_ftp_list if work_type == 'upload' else 'N/A',
                        'output_json_ftp_list': output_json_ftp_list if work_type == 'scan' else 'N/A',
                        'id_prev_snapshot_ref': id_prev_snapshot_ref,
                        'tmpsavedir': tmpsavedir if work_type == 'compare' else 'N/A',
                        'not_download_to_tmp': not_download_to_tmp if work_type == 'compare' else 'N/A'
                    })
            
            if not works_found:
                print("No works configured in the configuration file.")
                return
            
            print("Available Works:")
            print("===============")
            
            for i, work in enumerate(works_found, 1):
                print(work.get('id_work'), "   -  ", work.get('work_type'))
        except Exception as e:
            print(f"Error listing works: {str(e)}")
      
    
    def validate_work_type_config(self, id_work: str):
        """Validate work configuration based on work type."""
        try:
            # Get work configuration
            id_work_config = self.get_id_work_config(id_work)
            work_type = id_work_config.get('typeof_work')
            if not work_type:
                raise ValueError(f"✗ Error: 'typeof_work' not specified for work '{id_work}'")

            if work_type not in ['scan', 'upload', 'compare']:
                raise ValueError(f"✗ Error: Unsupported work type '{work_type}' for work '{id_work}'")

            # Validate based on work type
            if work_type == 'scan':
                self.validate_scan_work_config(id_work)
            elif work_type == 'upload':
                self.validate_upload_work_config(id_work)
            elif work_type == 'compare':
                self.validate_compare_work_config(id_work)
        except Exception as e:
            print(f"✗ Error in def validate_work_type_config: {str(e)}")
         
           
        
    
    def validate_scan_work_config(self, id_work: str):
        """Validate scan work configuration parameters."""
        id_work_config = self.get_id_work_config(id_work)
        try:
            # Required parameters for scan work
            required_params = {
                'id_work': "For work identification",
                'typeof_work': "For work type identification",
                'exclude_patterns': 'File exclusion patterns',
                'source': 'Source directory to scan',                                
                'destination': 'Destination path on FTP server',
                'output_json_ftp_list': 'Path to output JSON FTP list',
                'id_prev_snapshot_ref': 'Previous snapshot reference'
            }           
            

            # Check required parameters
            for param, description in required_params.items():
                if param not in id_work_config:
                    raise ValueError(f"✗ Error: Missing required parameter '{param}' ({description}) for scan work '{id_work}'")              
        
            #test if source path exists
            source_path = id_work_config.get('source')
            if not source_path or not os.path.exists(source_path):
                raise ValueError(f"✗ Error: Source path '{source_path}' does not exist for scan work '{id_work}'")   

        except Exception as e:
            print(f"✗ Error in def validate_scan_work_config: {str(e)}")
            
        
    
    def validate_upload_work_config(self, id_work: str):
        """Validate upload work configuration parameters."""
        id_work_config = self.get_id_work_config(id_work)
        try:
            # Required parameters for upload work
            required_params = {
                'id_work': "For work identification",
                'typeof_work': "For work type identification",
                'input_json_ftp_list': "Path to the input JSON FTP list"                
            }
            id_work = id_work_config.get('id_work', None)
            if not id_work:
                raise ValueError("✗ Error: 'id_work' not specified in upload work configuration")
            
            # Check required parameters
            for param, description in required_params.items():
                if param not in id_work_config:
                    raise ValueError(f"✗ Error: Missing required parameter '{param}' ({description}) for upload work '{id_work}'")            
            
        except Exception as e:
            print(f"✗ Error def validate_upload_work_config: {str(e)}")

    def validate_compare_work_config(self, id_work: str):
        """Validate compare work configuration parameters."""
        id_work_config = self.get_id_work_config(id_work)
        try:
            # Required parameters for compare work
            required_params = {
                'id_work': "For work identification",
                'typeof_work': "For work type identification",
                'exclude_patterns': 'File exclusion patterns',
                'source': 'Source directory to compare',                                
                'destination': 'Destination path on FTP server',
                'output_json_ftp_list': 'Path to output JSON FTP list',
                'tmpsavedir': 'Temporary directory to save intermediate files',
                'not_download_to_tmp': 'Flag to skip downloading files to temporary directory'
            }           
            

            # Check required parameters
            for param, description in required_params.items():
                if param not in id_work_config:
                    raise ValueError(f"✗ Error: Missing required parameter '{param}' ({description}) for compare work '{id_work}'")              
        
            #test if source path exists
            source_path = id_work_config.get('source')
            if not source_path or not os.path.exists(source_path):
                raise ValueError(f"✗ Error: Source path '{source_path}' does not exist for compare work '{id_work}'")   

        except Exception as e:
            print(f"✗ Error in def validate_compare_work_config: {str(e)}")
            
        

    def validate_subwork_reference(self, id_subwork: str):
        """Validate that referenced subwork exists and is of correct type."""
        try:
            # Get subwork configuration
            subwork_config = self.get_id_work_config(id_subwork)
            if not subwork_config:
                raise ValueError(f"✗ Error: Subwork '{id_subwork}' not found in configuration")
                
            # Check that subwork is of type 'scan'
            if subwork_config.get('typeof_work') != 'scan':
                raise ValueError(f"✗ Error: Subwork '{id_subwork}' is not of type 'scan'")
        except Exception as e:
            print(f"✗ Error in def validate_subwork_reference: {str(e)}")

    def validate_configuration(self):
        """Validate entire configuration."""
        try:
            self.validate_constants()
            # Validate each work configuration
            works_config = self.works_config
            for key, value in works_config.items():
                if isinstance(value, dict) and 'id_work' in value:
                    id_work = value['id_work']
                    self.validate_work_type_config(id_work)
                    if value.get('typeof_work') == 'upload':
                        id_subwork = value.get('id_subwork')
                        if id_subwork:
                            self.validate_subwork_reference(id_subwork)
        except Exception as e:
            print(f"✗ Error in def validate_configuration: {str(e)}")
    
    def validate_constants(self):
        """Validate constants in configuration."""
        try:
            config = self.config
            if 'constants' not in config:
                raise ValueError("✗ Error: No 'constants' section found in configuration")
            
            constants = config['constants']
            required_constants = [
                'local_base_path',
                'deployment_log_path',
                'file_transfer_log_path',                
                'deployment_scripts_path',
                'deployment_sqllite_path'
            ]
            
            for const in required_constants:
                if const not in constants:
                    raise ValueError(f"✗ Error: Missing required constant '{const}' in configuration")          
            
        
        except Exception as e:
            print(f"✗ Error in def validate_constants: {str(e)}")
