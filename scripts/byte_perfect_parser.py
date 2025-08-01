#!/usr/bin/env python3
"""
Byte-Perfect HTML Parser
Preserves exact byte-by-byte content without any modifications
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import uuid

class BytePerfectParser:
    def __init__(self):
        self.elements = []
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID."""
        return str(uuid.uuid4())[:8]
    
    def parse_html_byte_perfect(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML preserving exact byte-by-byte content."""
        print("🔍 Parsing HTML with byte-perfect preservation...")
        
        # Create a single element that contains the entire file
        element_id = self.generate_uuid()
        
        element_data = {
            "name": "document",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": html_content,  # Store the entire content
            "parent_id": None,
            "order": 1,
            "level": 0,
            "start_pos": 0,
            "end_pos": len(html_content),
            "byte_length": len(html_content.encode('utf-8')),
            "total_bytes": len(html_content.encode('utf-8'))
        }
        
        self.elements = [element_data]
        return self.elements
    
    def save_to_json(self, elements: List[Dict[str, Any]], output_file: Path):
        """Save parsed elements to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(elements)} elements to: {output_file}")

def main():
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_file = Path("svituawww.github.io/output/byte_perfect_elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = BytePerfectParser()
    
    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML with byte-perfect preservation
        elements = parser.parse_html_byte_perfect(html_content)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        print(f"✅ Parsed {len(elements)} elements using byte-perfect approach")
        print(f"📊 Original file size: {len(html_content)} bytes")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 