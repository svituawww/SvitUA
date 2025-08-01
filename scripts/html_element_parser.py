#!/usr/bin/env python3
"""
HTML Element Parser - Level 3
Parses HTML elements into structured JSON with UUIDs and parent-child relationships.
"""

import re
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
from bs4 import BeautifulSoup, Tag, NavigableString, Comment

class HTMLElementParser:
    def __init__(self):
        self.elements = []
        self.element_counter = 0
        self.element_map = {}  # Map Tag objects to UUIDs
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID for element ID."""
        return str(uuid.uuid4())[:8]
    
    def get_element_attributes(self, element: Tag) -> str:
        """Extract element tag with attributes."""
        attrs = []
        for key, value in element.attrs.items():
            if isinstance(value, list):
                value = ' '.join(value)
            attrs.append(f'{key}="{value}"')
        
        attr_str = ' '.join(attrs)
        return f"<{element.name}{' ' + attr_str if attr_str else ''}>"
    
    def extract_inner_content(self, element: Tag) -> str:
        """Extract inner content, replacing child elements with UUID references while preserving ALL text and comments exactly."""
        content_parts = []
        
        for child in element.children:
            if isinstance(child, NavigableString):
                # Text content - preserve EXACTLY as it appears (including whitespace, empty lines)
                text = str(child)
                content_parts.append(text)
            elif isinstance(child, Comment):
                # HTML comments - preserve exactly as they appear
                comment_text = str(child)
                content_parts.append(comment_text)
            elif isinstance(child, Tag):
                # Child element - replace with UUID reference
                child_uuid = self.element_map.get(child)
                if child_uuid:
                    content_parts.append(f"<{child_uuid}>")
        
        return ''.join(content_parts)  # Join without any modification to preserve exact formatting
    
    def parse_element(self, element: Tag, parent_id: str = None, level: int = 1) -> Dict[str, Any]:
        """Parse a single HTML element."""
        element_id = self.generate_uuid()
        
        # Store element reference for UUID lookup
        self.element_map[element] = element_id
        
        # Extract element data
        element_data = {
            "name": element.name,
            "id": element_id,
            "element_attr_content": self.get_element_attributes(element),
            "inner_content": "",  # Will be filled after all children are processed
            "parent_id": parent_id,
            "order": self.element_counter + 1,
            "level": level
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
        
        # Process children recursively - only process Tag children
        for child in element.children:
            if isinstance(child, Tag):
                self.parse_element(child, element_id, level + 1)
        
        # Now extract inner content after all children have UUIDs
        element_data["inner_content"] = self.extract_inner_content(element)
        
        return element_data
    
    def parse_html_file(self, input_file: Path) -> List[Dict[str, Any]]:
        """Parse HTML file and return structured element data."""
        print(f"🔍 Parsing HTML elements from: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Start parsing from root elements - only process Tag elements
        for element in soup.find_all(recursive=False):
            if isinstance(element, Tag):
                self.parse_element(element, parent_id=None, level=1)
        
        return self.elements
    
    def save_to_json(self, elements: List[Dict[str, Any]], output_file: Path):
        """Save parsed elements to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(elements)} elements to: {output_file}")
    
    def generate_summary(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate parsing summary."""
        elements_by_level = {}
        elements_by_name = {}
        
        for elem in elements:
            level = elem['level']
            name = elem['name']
            
            elements_by_level[level] = elements_by_level.get(level, 0) + 1
            elements_by_name[name] = elements_by_name.get(name, 0) + 1
        
        return {
            "total_elements": len(elements),
            "max_level": max(elements_by_level.keys()) if elements_by_level else 0,
            "elements_by_level": elements_by_level,
            "elements_by_name": elements_by_name,
            "has_children": any(elem['inner_content'].strip() for elem in elements)
        }

def main():
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_file = Path("svituawww.github.io/output/elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = HTMLElementParser()
    
    try:
        # Parse HTML elements
        elements = parser.parse_html_file(input_file)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        # Generate and display summary
        summary = parser.generate_summary(elements)
        print(f"\n📊 Parsing Summary:")
        print(f"   Total elements: {summary['total_elements']}")
        print(f"   Max nesting level: {summary['max_level']}")
        print(f"   Elements with children: {summary['has_children']}")
        print(f"   Top element types: {dict(list(summary['elements_by_name'].items())[:5])}")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 