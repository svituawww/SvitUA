<!-- File Processing → Brackets → Elements → Validation → Content Extraction → Summary -->


<!-- PRESERVE begin id_part1 -->


input config
ptb_parser/json/tech_tag_config.json - don`t allow agent access to edit denied

## Pre-Parsing Content Extraction Phase

### Objective
Before starting the main HTML parsing process, extract all **inline** JavaScript and CSS strings from the input HTML files and save them as external files for better organization and processing.

### Requirements

#### 1. **Inline Script Extraction**
- **Target**: Extract all inline JavaScript content between `<script>` and `</script>` tags (excluding those with `src` attributes)
- **Output Format**: `{original_filename}_js_{YYYYMMDD}_{i}.js`
- **Location**: `input_dir/` directory from `tech_tag_config.json`
- **Replacement**: Replace original inline `<script>` tag with placeholder comment
- number each file with end i

#### 2. **Inline Style Extraction**
- **Target**: Extract all inline CSS content between `<style>` and `</style>` tags (excluding those with `src` attributes)
- **Output Format**: `{original_filename}_css_{YYYYMMDD}_{i}.css`
- **Location**: `input_dir/` directory from `tech_tag_config.json`
- **Replacement**: Replace original inline `<style>` tag with placeholder comment
- number each file with end i

### Implementation Steps

#### **Step 1: Configuration Loading**
```python
import json
import os
from pathlib import Path

def load_config(config_path: str = "json/tech_tag_config.json") -> dict:
    """
    Load configuration from tech_tag_config.json.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration settings
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required configuration
    required_keys = ['input_dir', 'output_dir']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    return config
```

#### **Step 2: HTML Analysis for Inline Content**
```python
import re
import hashlib
from typing import Dict, List, Tuple

def analyze_inline_content(html_content: str) -> Dict[str, any]:
    """
    Analyze HTML content for inline scripts and styles.
    
    Args:
        html_content (str): HTML content to analyze
        
    Returns:
        dict: Analysis results with inline scripts and styles
    """
    results = {
        'inline_scripts': [],
        'inline_styles': [],
        'external_scripts': [],
        'external_styles': [],
        'total_scripts': 0,
        'total_styles': 0
    }
    
    # Pattern for inline scripts (without src attribute)
    inline_script_pattern = r'<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>'
    inline_scripts = re.findall(inline_script_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    # Pattern for external scripts (with src attribute)
    external_script_pattern = r'<script[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
    external_scripts = re.findall(external_script_pattern, html_content, re.IGNORECASE)
    
    # Pattern for inline styles (without src attribute)
    inline_style_pattern = r'<style(?![^>]*\bsrc\s*=)[^>]*>(.*?)</style>'
    inline_styles = re.findall(inline_style_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    # Pattern for external styles (with src attribute)
    external_style_pattern = r'<link[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>'
    external_styles = re.findall(external_style_pattern, html_content, re.IGNORECASE)
    
    # Clean and store inline content
    for i, script_content in enumerate(inline_scripts):
        cleaned_content = script_content.strip()
        if cleaned_content:  # Only include non-empty scripts
            results['inline_scripts'].append({
                'content': cleaned_content,
                'index': i,
                'size': len(cleaned_content)
            })
    
    for i, style_content in enumerate(inline_styles):
        cleaned_content = style_content.strip()
        if cleaned_content:  # Only include non-empty styles
            results['inline_styles'].append({
                'content': cleaned_content,
                'index': i,
                'size': len(cleaned_content)
            })
    
    # Store external resources for reference
    results['external_scripts'] = external_scripts
    results['external_styles'] = external_styles
    results['total_scripts'] = len(inline_scripts) + len(external_scripts)
    results['total_styles'] = len(inline_styles) + len(external_styles)
    
    return results
```

#### **Step 3: Content Extraction and File Creation**
```python
from datetime import datetime

def extract_inline_content(html_file: str, config: dict) -> Dict[str, any]:
    """
    Extract inline JavaScript and CSS content to external files.
    
    Args:
        html_file (str): Path to HTML file
        config (dict): Configuration from tech_tag_config.json
        
    Returns:
        dict: Extraction results with file paths and replacements
    """
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(html_file))[0]
    current_date = datetime.now().strftime('%Y%m%d')
    input_dir = config['input_dir']
    
    # Ensure input directory exists
    os.makedirs(input_dir, exist_ok=True)
    
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Analyze inline content
    analysis = analyze_inline_content(html_content)
    
    results = {
        'extracted_scripts': [],
        'extracted_styles': [],
        'replacements': [],
        'errors': [],
        'warnings': [],
        'summary': {
            'inline_scripts_found': len(analysis['inline_scripts']),
            'inline_styles_found': len(analysis['inline_styles']),
            'external_scripts_found': len(analysis['external_scripts']),
            'external_styles_found': len(analysis['external_styles']),
            'successful_extractions': 0,
            'failed_extractions': 0
        }
    }
    
    # Extract inline scripts
    for i, script_data in enumerate(analysis['inline_scripts']):
        try:
            script_filename = f"{base_name}_js_{current_date}_{i+1}.js"
            script_path = os.path.join(input_dir, script_filename)
            
            # Write script content
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_data['content'])
            
            results['extracted_scripts'].append({
                'original_content': script_data['content'],
                'local_path': script_path,
                'filename': script_filename,
                'size': script_data['size'],
                'index': script_data['index']
            })
            
            # Create replacement pattern for this specific script
            script_pattern = re.escape(f'<script>{script_data["content"]}</script>')
            replacement = f'<!-- EXTRACTED_INLINE_SCRIPT: {script_filename} | Size: {script_data["size"]} bytes -->'
            
            results['replacements'].append({
                'original': script_pattern,
                'replacement': replacement,
                'type': 'inline_script',
                'index': script_data['index']
            })
            
            results['summary']['successful_extractions'] += 1
            
        except Exception as e:
            error_msg = f"Failed to extract inline script {i+1}: {str(e)}"
            results['errors'].append(error_msg)
            results['summary']['failed_extractions'] += 1
    
    # Extract inline styles
    for i, style_data in enumerate(analysis['inline_styles']):
        try:
            style_filename = f"{base_name}_css_{current_date}_{i+1}.css"
            style_path = os.path.join(input_dir, style_filename)
            
            # Write style content
            with open(style_path, 'w', encoding='utf-8') as f:
                f.write(style_data['content'])
            
            results['extracted_styles'].append({
                'original_content': style_data['content'],
                'local_path': style_path,
                'filename': style_filename,
                'size': style_data['size'],
                'index': style_data['index']
            })
            
            # Create replacement pattern for this specific style
            style_pattern = re.escape(f'<style>{style_data["content"]}</style>')
            replacement = f'<!-- EXTRACTED_INLINE_STYLE: {style_filename} | Size: {style_data["size"]} bytes -->'
            
            results['replacements'].append({
                'original': style_pattern,
                'replacement': replacement,
                'type': 'inline_style',
                'index': style_data['index']
            })
            
            results['summary']['successful_extractions'] += 1
            
        except Exception as e:
            error_msg = f"Failed to extract inline style {i+1}: {str(e)}"
            results['errors'].append(error_msg)
            results['summary']['failed_extractions'] += 1
    
    return results
```

#### **Step 4: HTML File Update with Backup**
```python
import shutil

def update_html_with_extractions(html_file: str, replacements: List[Dict], create_backup: bool = True) -> Dict[str, any]:
    """
    Update HTML file by replacing inline content with placeholder comments.
    
    Args:
        html_file (str): Path to HTML file
        replacements (list): List of replacement rules
        create_backup (bool): Whether to create backup before modification
        
    Returns:
        dict: Update results with statistics
    """
    results = {
        'original_file': html_file,
        'backup_file': None,
        'replacements_applied': 0,
        'errors': [],
        'warnings': []
    }
    
    # Create backup if requested
    if create_backup:
        backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{html_file}.backup_{backup_suffix}"
        try:
            shutil.copy2(html_file, backup_file)
            results['backup_file'] = backup_file
        except Exception as e:
            results['warnings'].append(f"Failed to create backup: {str(e)}")
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements with validation
        for replacement in replacements:
            try:
                new_content = re.sub(
                    replacement['original'],
                    replacement['replacement'],
                    content,
                    flags=re.DOTALL
                )
                
                if new_content != content:
                    content = new_content
                    results['replacements_applied'] += 1
                else:
                    results['warnings'].append(f"No match found for pattern: {replacement['original'][:50]}...")
                    
            except Exception as e:
                results['errors'].append(f"Replacement failed: {str(e)}")
        
        # Write updated content back to file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        results['content_changed'] = content != original_content
        results['final_size'] = len(content)
        
    except Exception as e:
        results['errors'].append(f"File update failed: {str(e)}")
    
    return results
```

#### **Step 5: Main Processing Function**
```python
def process_inline_extraction(html_file: str, config_path: str = "json/tech_tag_config.json") -> Dict[str, any]:
    """
    Complete workflow for inline content extraction.
    
    Args:
        html_file (str): Path to HTML file
        config_path (str): Path to configuration file
        
    Returns:
        dict: Complete processing results
    """
    print(f"🔄 Starting inline extraction for: {html_file}")
    
    # Step 1: Load configuration
    print("📋 Loading configuration...")
    config = load_config(config_path)
    print(f"   Input directory: {config['input_dir']}")
    
    # Step 2: Analyze file
    print("📊 Analyzing HTML file for inline content...")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    analysis = analyze_inline_content(html_content)
    print(f"   Found {len(analysis['inline_scripts'])} inline scripts and {len(analysis['inline_styles'])} inline styles")
    print(f"   Found {len(analysis['external_scripts'])} external scripts and {len(analysis['external_styles'])} external styles")
    
    # Step 3: Extract content
    print("📥 Extracting inline content...")
    extraction_results = extract_inline_content(html_file, config)
    
    # Step 4: Update HTML file
    print("✏️  Updating HTML file...")
    update_results = update_html_with_extractions(html_file, extraction_results['replacements'])
    
    # Combine results
    final_results = {
        'analysis': analysis,
        'extraction': extraction_results,
        'update': update_results,
        'config': config,
        'summary': {
            'inline_scripts_found': len(analysis['inline_scripts']),
            'inline_styles_found': len(analysis['inline_styles']),
            'successful_extractions': extraction_results['summary']['successful_extractions'],
            'failed_extractions': extraction_results['summary']['failed_extractions'],
            'replacements_applied': update_results['replacements_applied']
        }
    }
    
    # Print summary
    print(f"✅ Inline extraction complete!")
    print(f"   📁 Extracted: {final_results['summary']['successful_extractions']} files")
    print(f"   ❌ Failed: {final_results['summary']['failed_extractions']} files")
    print(f"   🔄 Applied: {final_results['summary']['replacements_applied']} replacements")
    
    if extraction_results['errors']:
        print(f"   ⚠️  Errors: {len(extraction_results['errors'])}")
        for error in extraction_results['errors'][:3]:  # Show first 3 errors
            print(f"      - {error}")
    
    return final_results
```

### File Naming Convention

#### **JavaScript Files:**
```
Format: {original_filename}_js_{YYYYMMDD}_{i}.js
Example: index_html_js_20241204_1.js
Example: about_page_js_20241204_2.js
```

#### **CSS Files:**
```
Format: {original_filename}_css_{YYYYMMDD}_{i}.css
Example: index_html_css_20241204_1.css
Example: about_page_css_20241204_2.css
```

### Processing Workflow

#### **Phase 1: Configuration & Analysis**
1. **Load configuration** from `tech_tag_config.json`
2. **Analyze HTML content** for inline scripts and styles
3. **Identify external resources** for reference (not extracted)
4. **Generate file statistics** and metadata

#### **Phase 2: Content Extraction**
1. **Extract inline scripts** to external `.js` files with sequential numbering
2. **Extract inline styles** to external `.css` files with sequential numbering
3. **Generate numbered filenames** with date and sequence format
4. **Create replacement patterns** for each extraction

#### **Phase 3: HTML File Update**
1. **Create backup** of original HTML file
2. **Replace inline content** with placeholder comments
3. **Validate replacements** were applied correctly
4. **Update file statistics** and metadata

### Error Handling

#### **Common Issues:**
- **Missing configuration** - Validate required config keys
- **Empty inline content** - Skip empty scripts/styles
- **File permission errors** - Report and continue
- **Pattern matching failures** - Log warnings and continue

#### **Recovery Options:**
- **Partial extraction** - Continue with available content
- **Fallback to original** - Keep original tags if extraction fails
- **Manual intervention** - Flag files requiring manual processing

### Output Structure

```
input_dir/
├── original_file.html (updated with placeholders)
├── original_file_js_20241204_1.js
├── original_file_js_20241204_2.js
├── original_file_css_20241204_1.css
└── original_file_css_20241204_2.css
```

### Benefits

#### **Processing Advantages:**
- **Separated concerns** - HTML structure vs. styling/scripting
- **Better organization** - External files for CSS/JS
- **Easier maintenance** - Individual files for each component
- **Improved caching** - External files can be cached separately

#### **Development Benefits:**
- **Cleaner HTML** - Reduced inline content
- **Better debugging** - External files are easier to debug
- **Version control** - Individual file tracking
- **Code reusability** - Extracted files can be reused

#### **Performance Benefits:**
- **Faster parsing** - Smaller HTML files
- **Better caching** - Browser can cache external resources
- **Parallel loading** - CSS/JS can load in parallel
- **Reduced bandwidth** - Cached resources don't need re-download

<!-- PRESERVE end id_part1 -->











<!-- PRESERVE begin id_part2 -->

## 🖼️ **Media Directory Scanner with Pillow**

### **🎯 Objective**
Create a comprehensive media scanning system using Pillow library to collect detailed information about all images in specified directories and store the data in JSON format for analysis and management.

### **📋 Requirements**

#### **1. Media Configuration**
- **Config File**: `ptb_parser/json/media_config.json`
- **Input Directories**: Multiple directories for scanning
- **Output JSON**: Structured media information storage
- **Supported Formats**: All Pillow-supported image formats

#### **2. Information Collection**
- **Basic Info**: Filename, path, size, modification date
- **Image Metadata**: Dimensions, format, color mode, DPI
- **Technical Details**: Bit depth, compression, EXIF data
- **File Statistics**: File size, creation date, permissions
- **Thumbnail Generation**: Optional thumbnail creation

### **🔧 Implementation**

#### **Step 1: Configuration Management**
```python
import json
import os
from pathlib import Path
from typing import List, Dict, Any

def load_media_config(config_path: str = "ptb_parser/json/media_config.json") -> Dict[str, Any]:
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
                "ptb_parser/json/media_info.json"
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
```

#### **Step 2: Media Scanner Class**
```python
from PIL import Image, ExifTags
import hashlib
import mimetypes
from datetime import datetime
import logging

class MediaScanner:
    """
    Comprehensive media scanning system using Pillow library.
    """
    
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
            'image_info': {},
            'exif_data': {},
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
                # Basic image information
                file_info['image_info'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': {
                        'width': img.width,
                        'height': img.height,
                        'aspect_ratio': round(img.width / img.height, 3) if img.height > 0 else 0
                    },
                    'info': dict(img.info) if img.info else {},
                    'palette': img.palette.mode if img.palette else None,
                    'bands': img.getbands(),
                    'dpi': img.info.get('dpi', None),
                    'compression': img.info.get('compression', None)
                }
                
                # EXIF data
                if self.output_options.get('include_exif', True):
                    file_info['exif_data'] = self.extract_exif_data(img)
                
                # Color analysis
                if img.mode in ['RGB', 'RGBA']:
                    colors = img.getcolors(maxcolors=256)
                    file_info['image_info']['color_count'] = len(colors) if colors else 'unknown'
                
                # Thumbnail generation (optional)
                if self.scan_options.get('generate_thumbnails', False):
                    thumbnail_size = self.scan_options.get('thumbnail_size', [150, 150])
                    img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                    # Save thumbnail logic here if needed
            
            self.stats['processed_files'] += 1
            self.stats['total_size_bytes'] += file_info['file_size_bytes']
            
            # Track format statistics
            format_key = file_info['image_info']['format']
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
```

#### **Step 3: JSON Output Handler**
```python
import json
from pathlib import Path

class MediaInfoExporter:
    """
    Handle export of media information to JSON format.
    """
    
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
            json.dump(export_data, f, indent=indent, ensure_ascii=False)
        
        return output_path
```

#### **Step 4: Main Processing Function**
```python
def process_media_scanning(config_path: str = "ptb_parser/json/media_config.json") -> Dict[str, Any]:
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
    config = load_media_config(config_path)
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
```

### **📊 Output JSON Structure**

```json
{
  "metadata": {
    "scan_date": "2024-12-04T10:30:00",
    "scanner_version": "1.0.0",
    "configuration": {
      "input_dir_for_scanning": ["/path/to/uploads"],
      "output_dir_json": ["json/media_info.json"],
      "scan_options": {
        "recursive": true,
        "supported_formats": [".jpg", ".png", ".gif"],
        "max_file_size_mb": 50
      }
    },
    "statistics": {
      "total_files": 150,
      "processed_files": 120,
      "skipped_files": 25,
      "error_files": 5,
      "total_size_bytes": 52428800,
      "processing_time": 45.2
    }
  },
  "summary": {
    "total_directories_scanned": 1,
    "media_files_processed": 120,
    "total_size_mb": 50.0,
    "formats_found": {
      "JPEG": 80,
      "PNG": 30,
      "GIF": 10
    }
  },
  "media_files": [
    {
      "file_path": "/path/to/image.jpg",
      "filename": "image.jpg",
      "file_size_bytes": 1024000,
      "file_size_mb": 1.0,
      "file_hash": "abc123...",
      "mime_type": "image/jpeg",
      "creation_date": "2024-12-04T09:00:00",
      "modification_date": "2024-12-04T09:00:00",
      "image_info": {
        "format": "JPEG",
        "mode": "RGB",
        "size": {
          "width": 1920,
          "height": 1080,
          "aspect_ratio": 1.778
        },
        "dpi": [72, 72],
        "compression": "JPEG"
      },
      "exif_data": {
        "Make": "Canon",
        "Model": "EOS 5D Mark IV",
        "DateTime": "2024:12:04 09:00:00"
      },
      "processing_errors": []
    }
  ]
}
```

### **🚀 Usage Examples**

#### **Basic Usage:**
```python
# Run complete media scanning
results = process_media_scanning()

# Access results
print(f"Found {len(results['media_files'])} media files")
print(f"Total size: {results['scan_summary']['total_size_mb']} MB")
```

#### **Custom Configuration:**
```python
# Load custom configuration
config = load_media_config("custom_media_config.json")

# Initialize scanner with custom settings
scanner = MediaScanner(config)
results = scanner.scan_all_directories()

# Export with custom options
exporter = MediaInfoExporter(config)
output_file = exporter.export_to_json(results)
```

### **🔧 Advanced Features**

#### **Thumbnail Generation:**
```python
# Enable thumbnail generation in config
config['scan_options']['generate_thumbnails'] = True
config['scan_options']['thumbnail_size'] = [150, 150]
```

#### **EXIF Data Extraction:**
```python
# Disable EXIF extraction for performance
config['output_options']['include_exif'] = False
```

#### **File Size Filtering:**
```python
# Set maximum file size limit
config['scan_options']['max_file_size_mb'] = 10  # 10MB limit
```

### **📈 Performance Optimization**

#### **Memory Management:**
- **Stream processing** - Process files one by one
- **Lazy loading** - Load image data only when needed
- **Garbage collection** - Clear memory after each file

#### **Speed Optimization:**
- **Parallel processing** - Use multiprocessing for large directories
- **Caching** - Cache file statistics
- **Early filtering** - Skip files before full analysis

#### **Error Handling:**
- **Graceful degradation** - Continue processing on errors
- **Detailed logging** - Track all issues
- **Recovery options** - Retry failed operations

### **🎯 Benefits**

#### **Data Management:**
- **Complete inventory** - All media files catalogued
- **Metadata extraction** - Rich information about each file
- **Duplicate detection** - Hash-based deduplication
- **Format analysis** - Detailed format statistics

#### **Performance Monitoring:**
- **Processing statistics** - Time and resource usage
- **Error tracking** - Failed operations logging
- **Size analysis** - Storage usage breakdown
- **Format distribution** - File type statistics

#### **Integration Ready:**
- **JSON output** - Easy integration with other systems
- **Structured data** - Consistent data format
- **Extensible design** - Easy to add new features
- **Configuration driven** - Flexible setup options

This comprehensive media scanning solution provides detailed analysis of all images in your directories with rich metadata extraction and flexible output options! 🚀

<!-- PRESERVE end id_part2 -->






<!-- PRESERVE begin id_part3 -->

Modify ptb_parser/scripts/media_scanner.py to minimaze image info 

for each image i need only this info

      "file_path": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1/2025/06/15.jpg",
      "filename": "15.jpg",
      "directory": "/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io/uploads1/2025/06",
      "file_size_bytes": 31149,
      "file_size_mb": 0.03,
      "file_hash": "9b6356a1f127c86729b1588929fa516948b72ac715f76d60eee69d8ef1782627",
      "mime_type": "image/jpeg",
      "creation_date": "2025-07-28T23:46:33.656600",
      "modification_date": "2025-07-27T22:11:53.142438",
      "access_date": "2025-07-29T01:47:16.100329",
      "permissions": "644",
      "size_width": 1024,
      "size_height": 1024,
      "format": "JPEG",
      "mode": "RGB"

<!-- PRESERVE end id_part3 -->





<!-- PRESERVE begin id_part4 -->
oportunity luacning any scripts by reading common config files like 
from media scaner use absolute:
/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/json/media_config.json

for launching run_enhanced_processor.py
use absolute path to config
/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/json/tech_tag_config.json

and etc

for each scripts use only one config.

instead def load_media_config(config_path: str = "ptb_parser/json/media_config.json") -> Dict[str, Any]:

use this
def load_media_config(config_path: str = "/Users/nirsixadmin/Desktop/SvitUA/ptb_parser/json/media_config.json") -> Dict[str, Any]:

end etc.

not needed coommon loader



<!-- PRESERVE end id_part4 -->                         





<!-- PRESERVE begin id_part5 -->           

<!-- PRESERVE end id_part6 -->





<!-- PRESERVE begin id_part7 -->


<!-- PRESERVE end id_part7 -->