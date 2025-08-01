#!/usr/bin/env python3
"""
Binary Stream HTML Parser
Processes HTML as raw bytes to preserve exact formatting
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import uuid

class BinaryHTMLParser:
    def __init__(self):
        self.elements = []
        self.element_counter = 0
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID."""
        return str(uuid.uuid4())[:8]
    
    def parse_html_binary(self, html_content: bytes) -> List[Dict[str, Any]]:
        """Parse HTML as binary stream."""
        print("🔍 Parsing HTML as binary stream...")
        
        # Convert to string for easier processing
        content_str = html_content.decode('utf-8')
        
        # Use string regex patterns
        patterns = [
            (r'<!--.*?-->', 'comment'),
            (r'<[^>]+>', 'tag'),
            (r'[^<]+', 'text')
        ]
        
        # Process content character by character to preserve exact formatting
        elements = []
        position = 0
        current_text = ""
        
        i = 0
        while i < len(content_str):
            char = content_str[i]
            
            if char == '<':
                # Check for comment
                if content_str[i:i+4] == '<!--':
                    # Save any accumulated text
                    if current_text.strip():
                        elements.append(self.create_text_element(current_text, position - len(current_text), position))
                    
                    # Find comment end
                    comment_end = content_str.find('-->', i)
                    if comment_end != -1:
                        comment_content = content_str[i:comment_end + 3]
                        elements.append(self.create_comment_element(comment_content, i, comment_end + 3))
                        i = comment_end + 3
                        position = i
                        current_text = ""
                        continue
                
                # Regular tag
                # Save any accumulated text
                if current_text.strip():
                    elements.append(self.create_text_element(current_text, position - len(current_text), position))
                
                # Find tag end
                tag_end = content_str.find('>', i)
                if tag_end != -1:
                    tag_content = content_str[i:tag_end + 1]
                    tag_element = self.create_tag_element(tag_content, i, tag_end + 1)
                    if tag_element:  # Only add if not None
                        elements.append(tag_element)
                    i = tag_end + 1
                    position = i
                    current_text = ""
                    continue
            
            current_text += char
            i += 1
            position = i
        
        # Save any remaining text
        if current_text.strip():
            elements.append(self.create_text_element(current_text, position - len(current_text), position))
        
        return elements
        
        elements = []
        position = 0
        
        # Find all matches with their positions
        all_matches = []
        for pattern, match_type in patterns:
            for match in re.finditer(pattern, content_str, re.DOTALL):
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'content': match.group(0),
                    'type': match_type
                })
        
        # Sort by position
        all_matches.sort(key=lambda x: x['start'])
        
        # Process matches
        for match in all_matches:
            if match['type'] == 'tag':
                element = self.process_tag_match(match, position)
            elif match['type'] == 'comment':
                element = self.process_comment_match(match, position)
            elif match['type'] == 'text':
                element = self.process_text_match(match, position)
            
            if element:
                elements.append(element)
                position += 1
        
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
    
    def process_tag_match(self, match: Dict[str, Any], position: int) -> Dict[str, Any]:
        """Process a tag match."""
        content = match['content']
        
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
            "order": position + 1,
            "level": 1,
            "is_closing": is_closing,
            "start_pos": match['start'],
            "end_pos": match['end'],
            "byte_length": len(content.encode('utf-8'))
        }
    
    def process_comment_match(self, match: Dict[str, Any], position: int) -> Dict[str, Any]:
        """Process a comment match."""
        content = match['content']
        
        element_id = self.generate_uuid()
        
        return {
            "name": "comment",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": content,
            "parent_id": None,
            "order": position + 1,
            "level": 1,
            "start_pos": match['start'],
            "end_pos": match['end'],
            "byte_length": len(content.encode('utf-8'))
        }
    
    def process_text_match(self, match: Dict[str, Any], position: int) -> Dict[str, Any]:
        """Process a text match."""
        content = match['content']
        
        # Skip empty text
        if not content.strip():
            return None
        
        element_id = self.generate_uuid()
        
        return {
            "name": "text",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": content,
            "parent_id": None,
            "order": position + 1,
            "level": 1,
            "start_pos": match['start'],
            "end_pos": match['end'],
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
    output_file = Path("svituawww.github.io/output/binary_elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = BinaryHTMLParser()
    
    try:
        # Read HTML content as binary
        with open(input_file, 'rb') as f:
            html_content = f.read()
        
        # Parse HTML as binary
        elements = parser.parse_html_binary(html_content)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        print(f"✅ Parsed {len(elements)} elements using binary approach")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 