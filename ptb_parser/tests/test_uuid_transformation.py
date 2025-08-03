#!/usr/bin/env python3
"""
UUID-Based HTML Content Replacement Test - id_part5 Implementation
Demonstrates HTML content transformation into UUIDs with mapping system
"""

import sys
import json
import uuid
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add parent directory to path to import from scripts
sys.path.append(str(Path(__file__).parent.parent))

class HTMLUUIDTransformer:
    """Transform HTML content into UUIDs with mapping for reconstruction."""
    
    def __init__(self):
        self.content_mapping = {}  # UUID -> Original Content
        self.uuid_counter = 0
        self.generated_uuids = set()
    
    def generate_unique_uuid(self, content_type: str = "content") -> str:
        """Generate unique UUID with prefix for content type."""
        while True:
            # Generate UUID with prefix
            unique_id = f"uuid_{uuid.uuid4()}"
            
            # Ensure uniqueness
            if unique_id not in self.generated_uuids:
                self.generated_uuids.add(unique_id)
                return unique_id
    
    def extract_text_content(self, html_content: str) -> List[Tuple[str, int, int]]:
        """Extract text content with positions from HTML."""
        text_segments = []
        
        # Pattern to match text content (not within tags)
        pattern = r'>([^<]+)<'
        matches = re.finditer(pattern, html_content)
        
        for match in matches:
            text = match.group(1).strip()
            if text:  # Only non-empty text
                text_segments.append((text, match.start(1), match.end(1)))
        
        return text_segments
    
    def extract_attributes(self, html_content: str) -> List[Tuple[str, str, int, int]]:
        """Extract attribute values with positions from HTML."""
        attributes = []
        
        # Pattern to match attribute values
        pattern = r'(\w+)\s*=\s*["\']([^"\']+)["\']'
        matches = re.finditer(pattern, html_content)
        
        for match in matches:
            attr_name = match.group(1)
            attr_value = match.group(2)
            attributes.append((attr_name, attr_value, match.start(2), match.end(2)))
        
        return attributes
    
    def transform_html_content(self, html_file_path: str) -> Dict[str, Any]:
        """Transform HTML content into UUIDs with mapping."""
        
        # Read HTML file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"📄 Processing HTML file: {html_file_path}")
        print(f"📊 Original content length: {len(html_content)} characters")
        
        # Extract text content
        text_segments = self.extract_text_content(html_content)
        print(f"🔍 Found {len(text_segments)} text segments")
        
        # Extract attributes
        attributes = self.extract_attributes(html_content)
        print(f"🎯 Found {len(attributes)} attributes")
        
        # Transform text content
        transformed_html = html_content
        text_mappings = {}
        
        for text, start_pos, end_pos in text_segments:
            if text.strip():  # Only process non-empty text
                uuid_text = self.generate_unique_uuid("text")
                text_mappings[uuid_text] = {
                    'type': 'text',
                    'original': text,
                    'position': (start_pos, end_pos)
                }
                
                # Replace in HTML (handle position shifts)
                transformed_html = self.replace_at_position(
                    transformed_html, start_pos, end_pos, uuid_text
                )
        
        # Transform attribute values
        attr_mappings = {}
        
        for attr_name, attr_value, start_pos, end_pos in attributes:
            if attr_value.strip():  # Only process non-empty values
                uuid_attr = self.generate_unique_uuid("attribute")
                attr_mappings[uuid_attr] = {
                    'type': 'attribute',
                    'name': attr_name,
                    'original': attr_value,
                    'position': (start_pos, end_pos)
                }
                
                # Replace in HTML
                transformed_html = self.replace_at_position(
                    transformed_html, start_pos, end_pos, uuid_attr
                )
        
        # Combine all mappings
        self.content_mapping = {**text_mappings, **attr_mappings}
        
        return {
            'transformed_html': transformed_html,
            'content_mapping': self.content_mapping,
            'text_segments': len(text_segments),
            'attributes': len(attributes),
            'total_replacements': len(self.content_mapping)
        }
    
    def replace_at_position(self, content: str, start: int, end: int, replacement: str) -> str:
        """Replace content at specific position."""
        return content[:start] + replacement + content[end:]
    
    def save_transformed_files(self, original_path: Path, result: Dict[str, Any]) -> Dict[str, str]:
        """Save transformed HTML and mapping files."""
        
        # Generate unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(original_path.read_bytes()).hexdigest()[:8]
        
        # Save transformed HTML to test output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        transformed_filename = f"uuid_transformed_{original_path.stem}_{content_hash}_{timestamp}.html"
        transformed_path = output_dir / transformed_filename
        
        with open(transformed_path, 'w', encoding='utf-8') as f:
            f.write(result['transformed_html'])
        
        # Save mapping JSON to output directory
        mapping_filename = f"uuid_mapping_{original_path.stem}_{content_hash}_{timestamp}.json"
        mapping_path = output_dir / mapping_filename
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(result['content_mapping'], f, indent=2, ensure_ascii=False)
        
        return {
            'transformed_html': str(transformed_path),
            'mapping_html': str(transformed_path),
            'mapping_json': str(mapping_path)
        }
    
    def reconstruct_original_content(self, transformed_html: str, mapping: Dict[str, Any]) -> str:
        """Reconstruct original HTML from UUIDs using mapping."""
        
        reconstructed_html = transformed_html
        
        # Replace UUIDs back to original content
        for uuid_key, mapping_data in mapping.items():
            original_content = mapping_data['original']
            reconstructed_html = reconstructed_html.replace(uuid_key, original_content)
        
        return reconstructed_html

def test_simple_html_transformation():
    """Test UUID transformation with a simple HTML example."""
    
    print("🧪 Simple HTML UUID Transformation Test")
    print("=" * 50)
    
    # Create simple test HTML
    test_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <style>
        .container {
            background-color: #f0f0f0;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    some content
    <div class="container" src="page1.html">
    </div>
    some content
</body>
</html>"""
    
    # Save test HTML file
    test_file = Path(__file__).parent / "test_simple.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"📄 Created test HTML file: {test_file}")
    
    # Initialize transformer
    transformer = HTMLUUIDTransformer()
    
    # Transform HTML content
    result = transformer.transform_html_content(str(test_file))
    
    # Display results
    print(f"\n📊 Transformation Results:")
    print("-" * 40)
    print(f"Text segments processed: {result['text_segments']}")
    print(f"Attributes processed: {result['attributes']}")
    print(f"Total replacements: {result['total_replacements']}")
    
    # Show all mappings
    print(f"\n🔍 Content Mappings:")
    print("-" * 40)
    
    for uuid_key, mapping_data in result['content_mapping'].items():
        print(f"   {uuid_key} → '{mapping_data['original']}' ({mapping_data['type']})")
    
    # Show transformed HTML sample
    print(f"\n📄 Transformed HTML Sample:")
    print("-" * 40)
    lines = result['transformed_html'].split('\n')
    for i, line in enumerate(lines[:10]):  # Show first 10 lines
        print(f"   {i+1:2d}: {line}")
    
    # Test reconstruction
    print(f"\n🔄 Testing Reconstruction:")
    print("-" * 40)
    
    reconstructed_html = transformer.reconstruct_original_content(
        result['transformed_html'], result['content_mapping']
    )
    
    # Compare
    print(f"Original length: {len(test_html)} characters")
    print(f"Reconstructed length: {len(reconstructed_html)} characters")
    print(f"Reconstruction successful: {test_html == reconstructed_html}")
    
    # Clean up
    test_file.unlink()
    
    return result

def test_real_html_transformation():
    """Test UUID transformation on real HTML file."""
    
    print("\n🧪 Real HTML UUID Transformation Test")
    print("=" * 50)
    
    # Path to HTML file
    html_file_path = Path(__file__).parent.parent / "input" / "index_html_.html"
    
    if not html_file_path.exists():
        print(f"❌ File not found: {html_file_path}")
        return None
    
    # Initialize transformer
    transformer = HTMLUUIDTransformer()
    
    # Transform HTML content
    result = transformer.transform_html_content(str(html_file_path))
    
    # Display results
    print(f"\n📊 Transformation Results:")
    print("-" * 40)
    print(f"Text segments processed: {result['text_segments']}")
    print(f"Attributes processed: {result['attributes']}")
    print(f"Total replacements: {result['total_replacements']}")
    
    # Show sample mappings
    print(f"\n🔍 Sample Content Mappings:")
    print("-" * 40)
    
    sample_count = 0
    for uuid_key, mapping_data in result['content_mapping'].items():
        if sample_count < 5:  # Show first 5 mappings
            print(f"   {uuid_key} → '{mapping_data['original']}' ({mapping_data['type']})")
            sample_count += 1
        else:
            break
    
    # Save transformed files
    saved_files = transformer.save_transformed_files(html_file_path, result)
    
    print(f"\n💾 Files saved:")
    print(f"   Transformed HTML: {saved_files['transformed_html']}")
    print(f"   Mapping JSON: {saved_files['mapping_json']}")
    
    # Test reconstruction
    print(f"\n🔄 Testing Reconstruction:")
    print("-" * 40)
    
    reconstructed_html = transformer.reconstruct_original_content(
        result['transformed_html'], result['content_mapping']
    )
    
    # Compare lengths
    original_length = len(Path(html_file_path).read_text(encoding='utf-8'))
    reconstructed_length = len(reconstructed_html)
    
    print(f"Original length: {original_length} characters")
    print(f"Reconstructed length: {reconstructed_length} characters")
    print(f"Reconstruction successful: {original_length == reconstructed_length}")
    
    return {
        'result': result,
        'saved_files': saved_files,
        'reconstruction_success': original_length == reconstructed_length
    }

def test_uuid_uniqueness():
    """Test UUID uniqueness and generation."""
    
    print("\n🔐 UUID Uniqueness Test")
    print("=" * 30)
    
    transformer = HTMLUUIDTransformer()
    generated_uuids = set()
    
    # Generate multiple UUIDs
    for i in range(100):
        uuid_val = transformer.generate_unique_uuid()
        if uuid_val in generated_uuids:
            print(f"❌ Duplicate UUID found: {uuid_val}")
            return False
        generated_uuids.add(uuid_val)
    
    print(f"✅ Generated {len(generated_uuids)} unique UUIDs")
    print(f"   Sample UUIDs: {list(generated_uuids)[:3]}")
    
    return True

def main():
    """Run all UUID transformation tests."""
    print("🧪 UUID-Based HTML Transformation Test Suite - id_part5")
    print("=" * 70)
    
    # Test simple HTML transformation
    simple_result = test_simple_html_transformation()
    
    # Test real HTML transformation
    real_result = test_real_html_transformation()
    
    # Test UUID uniqueness
    uniqueness_result = test_uuid_uniqueness()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("-" * 30)
    print(f"Simple HTML Test: {'✅ Passed' if simple_result else '❌ Failed'}")
    print(f"Real HTML Test: {'✅ Passed' if real_result else '❌ Failed'}")
    print(f"UUID Uniqueness Test: {'✅ Passed' if uniqueness_result else '❌ Failed'}")
    
    if real_result:
        print(f"\n✅ UUID transformation completed successfully!")
        print(f"📄 Transformed HTML: {real_result['saved_files']['transformed_html']}")
        print(f"📋 Mapping file: {real_result['saved_files']['mapping_json']}")
    else:
        print(f"\n❌ UUID transformation failed!")

if __name__ == "__main__":
    main() 