# Media Scanner Implementation

## Overview

The Media Scanner is a comprehensive Python-based media scanning system that uses the Pillow library to collect detailed information about images in specified directories. It provides rich metadata extraction, flexible configuration options, and JSON output for further analysis.

## Features

### 🎯 Core Features
- **Multi-format Support**: JPEG, PNG, GIF, BMP, TIFF, WebP
- **Comprehensive Metadata**: File info, image properties, EXIF data
- **Flexible Configuration**: Customizable scanning options
- **Performance Monitoring**: Processing time and statistics
- **JSON Output**: Structured data for analysis
- **Error Handling**: Graceful error handling and logging

### 📊 Information Collected
- **Basic File Info**: Path, size, dates, permissions, hash
- **Image Properties**: Format, mode, dimensions, aspect ratio
- **Technical Details**: Bands, DPI, compression, color count
- **EXIF Data**: Camera info, GPS, timestamps (when available)
- **File Statistics**: Creation, modification, access dates

## Installation

### Prerequisites
```bash
# Install Pillow library
pip install Pillow

# Or using requirements.txt
pip install -r requirements.txt
```

### Dependencies
- Python 3.7+
- Pillow (PIL) library
- Standard library modules (json, os, hashlib, etc.)

## Quick Start

### Basic Usage
```python
from media_scanner import process_media_scanning

# Run with default configuration
results = process_media_scanning()
print(f"Found {len(results['media_files'])} media files")
```

### Command Line Usage
```bash
# Run the main scanner
python3 ptb_parser/scripts/run_media_scanner.py

# Run examples
python3 ptb_parser/scripts/media_scanner_example.py

# Run tests
python3 ptb_parser/scripts/test_media_scanner.py
```

## Configuration

### Default Configuration
The scanner uses `ptb_parser/json/media_config.json` for configuration:

```json
{
  "input_dir_for_scanning": [
    "svituawww.github.io/uploads1"
  ],
  "output_dir_json": [
    "ptb_parser/json/media_info.json"
  ],
  "scan_options": {
    "recursive": true,
    "include_hidden": false,
    "supported_formats": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "max_file_size_mb": 50,
    "generate_thumbnails": false,
    "thumbnail_size": [150, 150],
    "exclude_patterns": ["*thumb*", "*temp*", "*backup*"]
  },
  "output_options": {
    "include_thumbnails": false,
    "include_exif": true,
    "include_file_stats": true,
    "compress_json": false,
    "pretty_print": true
  }
}
```

### Configuration Options

#### Scan Options
- `recursive`: Scan subdirectories (boolean)
- `include_hidden`: Include hidden files (boolean)
- `supported_formats`: List of file extensions to process
- `max_file_size_mb`: Maximum file size limit
- `generate_thumbnails`: Create thumbnails (boolean)
- `thumbnail_size`: Thumbnail dimensions [width, height]
- `exclude_patterns`: Patterns to exclude from scanning

#### Output Options
- `include_thumbnails`: Include thumbnail data in output
- `include_exif`: Extract EXIF metadata
- `include_file_stats`: Include file statistics
- `compress_json`: Compress JSON output
- `pretty_print`: Format JSON with indentation

## Usage Examples

### Example 1: Basic Scanning
```python
from media_scanner import MediaConfigLoader, MediaScanner

# Load configuration
config = MediaConfigLoader.load_media_config()

# Initialize scanner
scanner = MediaScanner(config)

# Scan directory
files = scanner.scan_directory("/path/to/images")
print(f"Found {len(files)} media files")
```

### Example 2: Custom Configuration
```python
custom_config = {
    "input_dir_for_scanning": ["/path/to/images"],
    "output_dir_json": ["output.json"],
    "scan_options": {
        "recursive": True,
        "supported_formats": [".jpg", ".png"],
        "max_file_size_mb": 10
    }
}

scanner = MediaScanner(custom_config)
results = scanner.scan_all_directories()
```

### Example 3: File Analysis
```python
# Analyze file types and sizes
formats = {}
total_size = 0

for file in files:
    format_name = file['image_info']['format']
    formats[format_name] = formats.get(format_name, 0) + 1
    total_size += file['file_size_bytes']

print(f"Formats: {formats}")
print(f"Total size: {total_size / (1024*1024):.1f} MB")
```

## Output Structure

### JSON Output Format
```json
{
  "metadata": {
    "scan_date": "2025-08-07T12:37:51.003691",
    "scanner_version": "1.0.0",
    "configuration": { ... },
    "statistics": {
      "total_files": 91,
      "processed_files": 91,
      "skipped_files": 0,
      "error_files": 0,
      "total_size_bytes": 13739786,
      "processing_time": 0.616709
    }
  },
  "summary": {
    "total_directories_scanned": 1,
    "media_files_processed": 91,
    "total_size_mb": 13.1,
    "formats_found": {
      "PNG": 18,
      "JPEG": 73
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
      "image_info": {
        "format": "JPEG",
        "mode": "RGB",
        "size": {
          "width": 1920,
          "height": 1080,
          "aspect_ratio": 1.778
        },
        "bands": ["R", "G", "B"],
        "dpi": [72, 72]
      },
      "exif_data": {
        "Make": "Canon",
        "Model": "EOS 5D Mark IV"
      }
    }
  ]
}
```

## Performance

### Benchmarks
- **Processing Speed**: ~160 files/second
- **Memory Usage**: Efficient streaming processing
- **File Size Limit**: Configurable (default: 50MB)
- **Supported Formats**: All Pillow-supported formats

### Optimization Tips
1. **Limit file size**: Set `max_file_size_mb` to avoid large files
2. **Disable EXIF**: Set `include_exif: false` for faster processing
3. **Filter formats**: Limit `supported_formats` to needed types
4. **Exclude patterns**: Use `exclude_patterns` to skip unwanted files

## Error Handling

### Common Issues
- **File access errors**: Logged and skipped
- **Corrupted images**: Error logged, processing continues
- **Memory issues**: Large files are skipped if over limit
- **JSON serialization**: Custom encoder handles bytes objects

### Recovery Options
- **Partial processing**: Continues on individual file errors
- **Detailed logging**: All errors are logged with context
- **Statistics tracking**: Error counts in output summary

## Advanced Features

### Custom JSON Encoder
The scanner includes a custom JSON encoder to handle:
- Bytes objects (converted to hex strings)
- Non-serializable objects (converted to strings)
- Complex data structures

### Hash Generation
Each file gets a SHA-256 hash for:
- Duplicate detection
- File integrity verification
- Database indexing

### EXIF Extraction
When available, extracts:
- Camera make and model
- GPS coordinates
- Date/time information
- Technical settings

## Integration

### Database Integration
```python
# Save results to database
import sqlite3

conn = sqlite3.connect('media.db')
cursor = conn.cursor()

for file in results['media_files']:
    cursor.execute("""
        INSERT INTO media_files 
        (filename, path, size, format, width, height, hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        file['filename'],
        file['file_path'],
        file['file_size_bytes'],
        file['image_info']['format'],
        file['image_info']['size']['width'],
        file['image_info']['size']['height'],
        file['file_hash']
    ))

conn.commit()
```

### Web API Integration
```python
# Return results as API response
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/scan-media')
def scan_media():
    results = process_media_scanning()
    return jsonify(results['summary'])
```

## Troubleshooting

### Common Problems

#### 1. "Object of type bytes is not JSON serializable"
**Solution**: The custom JSON encoder handles this automatically.

#### 2. "File too large" warnings
**Solution**: Increase `max_file_size_mb` in configuration.

#### 3. Slow processing
**Solution**: 
- Disable EXIF extraction
- Limit supported formats
- Use exclude patterns

#### 4. Memory errors
**Solution**: 
- Reduce file size limit
- Process directories separately
- Use streaming approach

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run scanner with debug output
results = process_media_scanning()
```

## Contributing

### Adding New Features
1. Extend the `MediaScanner` class
2. Add configuration options
3. Update the JSON encoder if needed
4. Add tests and examples

### Testing
```bash
# Run all tests
python3 ptb_parser/scripts/test_media_scanner.py

# Run examples
python3 ptb_parser/scripts/media_scanner_example.py
```

## License

This implementation is part of the SvitUA project and follows the project's licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example scripts
3. Examine the test suite
4. Check the configuration options

---

**Media Scanner v1.0.0** - Comprehensive media scanning with Pillow library
