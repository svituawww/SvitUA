#!/usr/bin/env python3
"""
Custom HTML Parser - Plain Text Approach
Preserves exact formatting, whitespace, and comments
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import uuid

class CustomHTMLParser:
    def __init__(self):
        self.elements = []
        self.element_counter = 0
        self.element_map = {}  # content_hash -> element_id
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID."""
        return str(uuid.uuid4())[:8]
    
    def parse_html_as_text(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML as plain text while preserving exact formatting."""
        print("🔍 Parsing HTML as plain text...")
        
        # Split content into chunks: tags, comments, and text
        chunks = self.split_html_content(html_content)
        
        # Process each chunk
        for chunk in chunks:
            if chunk['type'] == 'tag':
                self.process_tag_chunk(chunk)
            elif chunk['type'] == 'comment':
                self.process_comment_chunk(chunk)
            elif chunk['type'] == 'text':
                self.process_text_chunk(chunk)
        
        return self.elements
    
    def split_html_content(self, content: str) -> List[Dict[str, Any]]:
        """Split HTML content into tags, comments, and text chunks."""
        chunks = []
        position = 0
        
        # Pattern to match HTML tags and comments
        pattern = r'(<!--.*?-->)|(<[^>]+>)'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            start, end = match.span()
            
            # Add text before the match
            if start > position:
                text_content = content[position:start]
                if text_content.strip():  # Only add non-empty text
                    chunks.append({
                        'type': 'text',
                        'content': text_content,
                        'start': position,
                        'end': start
                    })
            
            # Add the matched tag or comment
            matched_content = match.group(0)
            if matched_content.startswith('<!--'):
                chunks.append({
                    'type': 'comment',
                    'content': matched_content,
                    'start': start,
                    'end': end
                })
            else:
                chunks.append({
                    'type': 'tag',
                    'content': matched_content,
                    'start': start,
                    'end': end
                })
            
            position = end
        
        # Add remaining text
        if position < len(content):
            remaining_text = content[position:]
            if remaining_text.strip():
                chunks.append({
                    'type': 'text',
                    'content': remaining_text,
                    'start': position,
                    'end': len(content)
                })
        
        return chunks
    
    def process_tag_chunk(self, chunk: Dict[str, Any]):
        """Process HTML tag chunk."""
        tag_content = chunk['content']
        
        # Extract tag name and attributes
        tag_match = re.match(r'<(\/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>', tag_content)
        if not tag_match:
            return
        
        is_closing = bool(tag_match.group(1))
        tag_name = tag_match.group(2)
        attributes = tag_match.group(3)
        
        element_id = self.generate_uuid()
        
        element_data = {
            "name": tag_name,
            "id": element_id,
            "element_attr_content": tag_content,
            "inner_content": "",  # Will be filled later
            "parent_id": None,  # Will be determined by nesting
            "order": self.element_counter + 1,
            "level": 1,
            "is_closing": is_closing,
            "start_pos": chunk['start'],
            "end_pos": chunk['end']
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
    
    def process_comment_chunk(self, chunk: Dict[str, Any]):
        """Process HTML comment chunk."""
        comment_content = chunk['content']
        
        element_id = self.generate_uuid()
        
        element_data = {
            "name": "comment",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": comment_content,
            "parent_id": None,
            "order": self.element_counter + 1,
            "level": 1,
            "is_closing": False,
            "start_pos": chunk['start'],
            "end_pos": chunk['end']
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
    
    def process_text_chunk(self, chunk: Dict[str, Any]):
        """Process text chunk."""
        text_content = chunk['content']
        
        element_id = self.generate_uuid()
        
        element_data = {
            "name": "text",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": text_content,
            "parent_id": None,
            "order": self.element_counter + 1,
            "level": 1,
            "is_closing": False,
            "start_pos": chunk['start'],
            "end_pos": chunk['end']
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
    
    def save_to_json(self, elements: List[Dict[str, Any]], output_file: Path):
        """Save parsed elements to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(elements)} elements to: {output_file}")

def main():
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_file = Path("svituawww.github.io/output/custom_elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = CustomHTMLParser()
    
    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML as plain text
        elements = parser.parse_html_as_text(html_content)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        print(f"✅ Parsed {len(elements)} elements using custom plain text approach")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 