#!/usr/bin/env python3
"""
Perfect Byte-by-Byte HTML Parser
Preserves exact formatting, whitespace, and content
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import uuid

class PerfectHTMLParser:
    def __init__(self):
        self.elements = []
        self.element_counter = 0
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID."""
        return str(uuid.uuid4())[:8]
    
    def parse_html_perfect(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML preserving exact byte-by-byte content."""
        print("🔍 Parsing HTML with perfect byte preservation...")
        
        elements = []
        position = 0
        current_text = ""
        
        i = 0
        while i < len(html_content):
            char = html_content[i]
            
            if char == '<':
                # Check for DOCTYPE
                if html_content[i:i+9] == '<!DOCTYPE':
                    # Save any accumulated text
                    if current_text:
                        elements.append(self.create_text_element(current_text, position - len(current_text), position))
                    
                    # Find DOCTYPE end
                    doctype_end = html_content.find('>', i)
                    if doctype_end != -1:
                        doctype_content = html_content[i:doctype_end + 1]
                        elements.append(self.create_doctype_element(doctype_content, i, doctype_end + 1))
                        i = doctype_end + 1
                        position = i
                        current_text = ""
                        continue
                
                # Check for comment
                elif html_content[i:i+4] == '<!--':
                    # Save any accumulated text
                    if current_text:
                        elements.append(self.create_text_element(current_text, position - len(current_text), position))
                    
                    # Find comment end
                    comment_end = html_content.find('-->', i)
                    if comment_end != -1:
                        comment_content = html_content[i:comment_end + 3]
                        elements.append(self.create_comment_element(comment_content, i, comment_end + 3))
                        i = comment_end + 3
                        position = i
                        current_text = ""
                        continue
                
                # Regular tag
                # Save any accumulated text
                if current_text:
                    elements.append(self.create_text_element(current_text, position - len(current_text), position))
                
                # Find tag end
                tag_end = html_content.find('>', i)
                if tag_end != -1:
                    tag_content = html_content[i:tag_end + 1]
                    tag_element = self.create_tag_element(tag_content, i, tag_end + 1)
                    if tag_element:
                        elements.append(tag_element)
                    i = tag_end + 1
                    position = i
                    current_text = ""
                    continue
            
            current_text += char
            i += 1
            position = i
        
        # Save any remaining text
        if current_text:
            elements.append(self.create_text_element(current_text, position - len(current_text), position))
        
        return elements
    
    def create_text_element(self, content: str, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """Create a text element."""
        element_id = self.generate_uuid()
        
        return {
            "name": "text",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": content,
            "parent_id": None,
            "order": len(self.elements) + 1,
            "level": 1,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "byte_length": len(content.encode('utf-8'))
        }
    
    def create_comment_element(self, content: str, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """Create a comment element."""
        element_id = self.generate_uuid()
        
        return {
            "name": "comment",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": content,
            "parent_id": None,
            "order": len(self.elements) + 1,
            "level": 1,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "byte_length": len(content.encode('utf-8'))
        }
    
    def create_doctype_element(self, content: str, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """Create a DOCTYPE element."""
        element_id = self.generate_uuid()
        
        return {
            "name": "doctype",
            "id": element_id,
            "element_attr_content": content,
            "inner_content": "",
            "parent_id": None,
            "order": len(self.elements) + 1,
            "level": 1,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "byte_length": len(content.encode('utf-8'))
        }
    
    def create_tag_element(self, content: str, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """Create a tag element."""
        # Extract tag info
        tag_match = re.match(r'<(\/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>', content)
        if not tag_match:
            return None
        
        is_closing = bool(tag_match.group(1))
        tag_name = tag_match.group(2)
        
        element_id = self.generate_uuid()
        
        return {
            "name": tag_name,
            "id": element_id,
            "element_attr_content": content,
            "inner_content": "",
            "parent_id": None,
            "order": len(self.elements) + 1,
            "level": 1,
            "is_closing": is_closing,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "byte_length": len(content.encode('utf-8'))
        }
    
    def save_to_json(self, elements: List[Dict[str, Any]], output_file: Path):
        """Save parsed elements to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(elements)} elements to: {output_file}")

def main():
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_file = Path("svituawww.github.io/output/perfect_elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = PerfectHTMLParser()
    
    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML with perfect preservation
        elements = parser.parse_html_perfect(html_content)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        print(f"✅ Parsed {len(elements)} elements using perfect byte preservation")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 