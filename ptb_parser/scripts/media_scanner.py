#!/usr/bin/env python3
"""
Media Directory Scanner with Pillow
Comprehensive media scanning system to collect detailed information about images.
"""

import json
import os
import hashlib
import mimetypes
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ExifTags

class BytesEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle bytes objects and other non-serializable types."""
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

class MediaConfigLoader:
    """Load and validate media scanning configuration."""
    
    @staticmethod
    def load_media_config(config_path: str = "/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/config/media_config.json") -> Dict[str, Any]:
        """
        Load media scanning configuration.
        
        Args:
            config_path (str): Path to media configuration file
            
        Returns:
            dict: Configuration settings for media scanning
        """
        if not os.path.exists(config_path):
            # Create default configuration if not exists
            default_config = {
                "input_dir_for_scanning": [
                    "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1"
                ],
                "output_dir_json": [
                    "/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/json_output/media_info.json"
                ],
                "scan_options": {
                    "recursive": True,
                    "include_hidden": False,
                    "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
                    "max_file_size_mb": 50,
                    "generate_thumbnails": False,
                    "thumbnail_size": [150, 150],
                    "exclude_patterns": ["*thumb*", "*temp*", "*backup*"]
                },
                "output_options": {
                    "include_thumbnails": False,
                    "include_exif": True,
                    "include_file_stats": True,
                    "compress_json": False,
                    "pretty_print": True
                }
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created default configuration: {config_path}")
            return default_config
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate configuration
        required_keys = ['input_dir_for_scanning', 'output_dir_json']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        

        
        return config


class MediaScanner:
    """Comprehensive media scanning system using Pillow library."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scan_options = config.get('scan_options', {})
        self.output_options = config.get('output_options', {})
        self.supported_formats = self.scan_options.get('supported_formats', 
                                                      ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'])
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'total_size_bytes': 0,
            'supported_formats_found': {},
            'processing_time': 0
        }
    
    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if file format is supported for processing.
        
        Args:
            file_path (str): Path to file
            
        Returns:
            bool: True if format is supported
        """
        file_ext = os.path.splitext(file_path.lower())[1]
        return file_ext in self.supported_formats
    
    def should_exclude_file(self, file_path: str) -> bool:
        """
        Check if file should be excluded based on patterns.
        
        Args:
            file_path (str): Path to file
            
        Returns:
            bool: True if file should be excluded
        """
        filename = os.path.basename(file_path).lower()
        exclude_patterns = self.scan_options.get('exclude_patterns', [])
        
        for pattern in exclude_patterns:
            if pattern.lower() in filename:
                return True
        
        return False
    
    def get_file_hash(self, file_path: str) -> str:
        """
        Generate SHA-256 hash of file for deduplication.
        
        Args:
            file_path (str): Path to file
            
        Returns:
            str: SHA-256 hash of file
        """
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to generate hash for {file_path}: {e}")
            return ""
    
    def extract_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image.
        
        Args:
            image (Image.Image): PIL Image object
            
        Returns:
            dict: EXIF metadata
        """
        exif_data = {}
        
        try:
            exif = image._getexif()
            if exif:
                for tag_id in exif:
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    data = exif.get(tag_id)
                    # Convert data to JSON-serializable format
                    if isinstance(data, bytes):
                        exif_data[tag] = data.hex()
                    elif isinstance(data, (int, float, str, bool)):
                        exif_data[tag] = data
                    else:
                        exif_data[tag] = str(data)
        except Exception as e:
            self.logger.debug(f"Failed to extract EXIF data: {e}")
        
        return exif_data
    
    def analyze_image(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze single image file and extract comprehensive information.
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            dict: Comprehensive image information
        """
        file_info = {
            'file_path': file_path,
            'filename': os.path.basename(file_path),
            'directory': os.path.dirname(file_path),
            'file_size_bytes': 0,
            'file_size_mb': 0,
            'file_hash': '',
            'mime_type': '',
            'creation_date': None,
            'modification_date': None,
            'access_date': None,
            'permissions': '',
            'processing_errors': []
        }
        
        try:
            # Basic file information
            stat_info = os.stat(file_path)
            file_info['file_size_bytes'] = stat_info.st_size
            file_info['file_size_mb'] = round(stat_info.st_size / (1024 * 1024), 2)
            file_info['creation_date'] = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
            file_info['modification_date'] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            file_info['access_date'] = datetime.fromtimestamp(stat_info.st_atime).isoformat()
            file_info['permissions'] = oct(stat_info.st_mode)[-3:]
            
            # File hash
            file_info['file_hash'] = self.get_file_hash(file_path)
            
            # MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            file_info['mime_type'] = mime_type or 'unknown'
            
            # Image analysis with Pillow
            with Image.open(file_path) as img:
                # Minimal image information as requested
                file_info['size_width'] = img.width
                file_info['size_height'] = img.height
                file_info['format'] = img.format
                file_info['mode'] = img.mode
            
            self.stats['processed_files'] += 1
            self.stats['total_size_bytes'] += file_info['file_size_bytes']
            
            # Track format statistics
            format_key = file_info['format']
            self.stats['supported_formats_found'][format_key] = \
                self.stats['supported_formats_found'].get(format_key, 0) + 1
            
        except Exception as e:
            error_msg = f"Failed to analyze {file_path}: {str(e)}"
            file_info['processing_errors'].append(error_msg)
            self.logger.error(error_msg)
            self.stats['error_files'] += 1
        
        return file_info
    
    def scan_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Scan directory for media files and analyze them.
        
        Args:
            directory_path (str): Path to directory to scan
            
        Returns:
            list: List of file information dictionaries
        """
        if not os.path.exists(directory_path):
            self.logger.error(f"Directory does not exist: {directory_path}")
            return []
        
        media_files = []
        
        # Walk directory
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden directories if configured
            if not self.scan_options.get('include_hidden', False):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                self.stats['total_files'] += 1
                
                # Check if file should be excluded
                if self.should_exclude_file(file_path):
                    self.stats['skipped_files'] += 1
                    continue
                
                # Check if format is supported
                if not self.is_supported_format(file_path):
                    self.stats['skipped_files'] += 1
                    continue
                
                # Check file size limit
                try:
                    file_size = os.path.getsize(file_path)
                    max_size_mb = self.scan_options.get('max_file_size_mb', 50)
                    if file_size > (max_size_mb * 1024 * 1024):
                        self.logger.warning(f"File too large, skipping: {file_path}")
                        self.stats['skipped_files'] += 1
                        continue
                except OSError:
                    self.logger.warning(f"Cannot access file: {file_path}")
                    self.stats['skipped_files'] += 1
                    continue
                
                # Analyze file
                file_info = self.analyze_image(file_path)
                media_files.append(file_info)
        
        return media_files
    
    def scan_all_directories(self) -> Dict[str, Any]:
        """
        Scan all configured directories and compile results.
        
        Returns:
            dict: Complete scanning results with statistics
        """
        start_time = datetime.now()
        all_media_files = []
        
        for directory in self.config['input_dir_for_scanning']:
            self.logger.info(f"🔍 Scanning directory: {directory}")
            directory_files = self.scan_directory(directory)
            all_media_files.extend(directory_files)
            self.logger.info(f"   Found {len(directory_files)} media files")
        
        # Calculate processing time
        end_time = datetime.now()
        self.stats['processing_time'] = (end_time - start_time).total_seconds()
        
        # Compile results
        results = {
            'scan_configuration': self.config,
            'scan_statistics': self.stats,
            'media_files': all_media_files,
            'scan_summary': {
                'total_directories_scanned': len(self.config['input_dir_for_scanning']),
                'total_files_found': self.stats['total_files'],
                'media_files_processed': self.stats['processed_files'],
                'files_skipped': self.stats['skipped_files'],
                'files_with_errors': self.stats['error_files'],
                'total_size_mb': round(self.stats['total_size_bytes'] / (1024 * 1024), 2),
                'processing_time_seconds': self.stats['processing_time'],
                'formats_found': self.stats['supported_formats_found']
            }
        }
        
        return results


class MediaInfoExporter:
    """Handle export of media information to JSON format."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_options = config.get('output_options', {})
    
    def export_to_json(self, scan_results: Dict[str, Any]) -> str:
        """
        Export scan results to JSON file.
        
        Args:
            scan_results (dict): Results from media scanner
            
        Returns:
            str: Path to exported JSON file
        """
        output_path = self.config['output_dir_json'][0]
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare data for export
        export_data = {
            'metadata': {
                'scan_date': datetime.now().isoformat(),
                'scanner_version': '1.0.0',
                'configuration': scan_results['scan_configuration'],
                'statistics': scan_results['scan_statistics']
            },
            'summary': scan_results['scan_summary'],
            'media_files': scan_results['media_files']
        }
        
        # Export options
        if self.output_options.get('pretty_print', True):
            indent = 2
        else:
            indent = None
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=indent, ensure_ascii=False, cls=BytesEncoder)
        
        return output_path


def process_media_scanning(config_path: str = "/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/config/media_config.json") -> Dict[str, Any]:
    """
    Complete workflow for media directory scanning.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Complete scanning results
    """
    print("🖼️  Starting media directory scanning...")
    
    # Step 1: Load configuration
    print("📋 Loading media configuration...")
    config = MediaConfigLoader.load_media_config(config_path)
    print(f"   Input directories: {len(config['input_dir_for_scanning'])}")
    print(f"   Output JSON: {config['output_dir_json'][0]}")
    
    # Step 2: Initialize scanner
    print("🔧 Initializing media scanner...")
    scanner = MediaScanner(config)
    
    # Step 3: Scan all directories
    print("🔍 Scanning directories for media files...")
    scan_results = scanner.scan_all_directories()
    
    # Step 4: Export results
    print("📤 Exporting results to JSON...")
    exporter = MediaInfoExporter(config)
    output_file = exporter.export_to_json(scan_results)
    
    # Print summary
    summary = scan_results['scan_summary']
    print(f"✅ Media scanning complete!")
    print(f"   📁 Directories scanned: {summary['total_directories_scanned']}")
    print(f"   📄 Total files found: {summary['total_files_found']}")
    print(f"   🖼️  Media files processed: {summary['media_files_processed']}")
    print(f"   ⏭️  Files skipped: {summary['files_skipped']}")
    print(f"   ❌ Files with errors: {summary['files_with_errors']}")
    print(f"   💾 Total size: {summary['total_size_mb']} MB")
    print(f"   ⏱️  Processing time: {summary['processing_time_seconds']:.2f} seconds")
    print(f"   📊 Output file: {output_file}")
    
    # Print format statistics
    if scan_results['scan_statistics']['supported_formats_found']:
        print(f"   🎨 Formats found:")
        for format_name, count in scan_results['scan_statistics']['supported_formats_found'].items():
            print(f"      - {format_name}: {count} files")
    
    return scan_results


if __name__ == "__main__":
    # Run the media scanning process
    results = process_media_scanning()
    print(f"\n🎉 Media scanning completed successfully!")
    print(f"📊 Results saved to: {results['scan_configuration']['output_dir_json'][0]}")
