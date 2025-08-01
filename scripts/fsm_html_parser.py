#!/usr/bin/env python3
"""
Finite State Machine HTML Parser
Processes character by character to preserve exact formatting
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

class FSMHTMLParser:
    def __init__(self):
        self.elements = []
        self.element_counter = 0
        self.current_element = None
        self.state = 'TEXT'  # TEXT, TAG, COMMENT, ATTRIBUTE
        self.buffer = ""
        self.position = 0
        self.line = 1
        self.column = 1
        
    def generate_uuid(self) -> str:
        """Generate 8-character UUID."""
        return str(uuid.uuid4())[:8]
    
    def parse_html_fsm(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse HTML using Finite State Machine approach."""
        print("🔍 Parsing HTML with FSM (character by character)...")
        
        self.elements = []
        self.element_counter = 0
        self.state = 'TEXT'
        self.buffer = ""
        self.position = 0
        self.line = 1
        self.column = 1
        
        for char in html_content:
            self.process_character(char)
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        
        # Process any remaining buffer
        if self.buffer.strip():
            self.finalize_text_element()
        
        return self.elements
    
    def process_character(self, char: str):
        """Process a single character based on current state."""
        if self.state == 'TEXT':
            self.process_text_char(char)
        elif self.state == 'TAG':
            self.process_tag_char(char)
        elif self.state == 'COMMENT':
            self.process_comment_char(char)
        elif self.state == 'ATTRIBUTE':
            self.process_attribute_char(char)
    
    def process_text_char(self, char: str):
        """Process character in TEXT state."""
        if char == '<':
            # Check for comment start
            if self.buffer.endswith('<!--'):
                self.state = 'COMMENT'
                self.buffer += char
            else:
                # Start of tag
                if self.buffer.strip():
                    self.finalize_text_element()
                self.state = 'TAG'
                self.buffer = char
        else:
            self.buffer += char
    
    def process_tag_char(self, char: str):
        """Process character in TAG state."""
        if char == '>':
            self.buffer += char
            self.finalize_tag_element()
            self.state = 'TEXT'
            self.buffer = ""
        elif char == '"' or char == "'":
            self.state = 'ATTRIBUTE'
            self.buffer += char
        else:
            self.buffer += char
    
    def process_comment_char(self, char: str):
        """Process character in COMMENT state."""
        self.buffer += char
        if self.buffer.endswith('-->'):
            self.finalize_comment_element()
            self.state = 'TEXT'
            self.buffer = ""
    
    def process_attribute_char(self, char: str):
        """Process character in ATTRIBUTE state."""
        self.buffer += char
        if char == '"' or char == "'":
            self.state = 'TAG'
    
    def finalize_text_element(self):
        """Finalize a text element."""
        if not self.buffer.strip():
            return
        
        element_id = self.generate_uuid()
        element_data = {
            "name": "text",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": self.buffer,
            "parent_id": None,
            "order": self.element_counter + 1,
            "level": 1,
            "start_pos": self.position - len(self.buffer),
            "end_pos": self.position,
            "line": self.line,
            "column": self.column - len(self.buffer)
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
        self.buffer = ""
    
    def finalize_tag_element(self):
        """Finalize a tag element."""
        element_id = self.generate_uuid()
        
        # Determine if it's opening or closing tag
        is_closing = self.buffer.startswith('</')
        tag_name = self.extract_tag_name(self.buffer)
        
        element_data = {
            "name": tag_name,
            "id": element_id,
            "element_attr_content": self.buffer,
            "inner_content": "",
            "parent_id": None,
            "order": self.element_counter + 1,
            "level": 1,
            "is_closing": is_closing,
            "start_pos": self.position - len(self.buffer),
            "end_pos": self.position,
            "line": self.line,
            "column": self.column - len(self.buffer)
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
    
    def finalize_comment_element(self):
        """Finalize a comment element."""
        element_id = self.generate_uuid()
        
        element_data = {
            "name": "comment",
            "id": element_id,
            "element_attr_content": "",
            "inner_content": self.buffer,
            "parent_id": None,
            "order": self.element_counter + 1,
            "level": 1,
            "start_pos": self.position - len(self.buffer),
            "end_pos": self.position,
            "line": self.line,
            "column": self.column - len(self.buffer)
        }
        
        self.elements.append(element_data)
        self.element_counter += 1
    
    def extract_tag_name(self, tag_content: str) -> str:
        """Extract tag name from tag content."""
        # Remove < and >
        tag_content = tag_content.strip('<>')
        
        # Handle closing tags
        if tag_content.startswith('/'):
            tag_content = tag_content[1:]
        
        # Extract first word (tag name)
        parts = tag_content.split()
        return parts[0] if parts else "unknown"
    
    def save_to_json(self, elements: List[Dict[str, Any]], output_file: Path):
        """Save parsed elements to JSON file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(elements)} elements to: {output_file}")

def main():
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_file = Path("svituawww.github.io/output/fsm_elements_parsed.json")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    parser = FSMHTMLParser()
    
    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML with FSM
        elements = parser.parse_html_fsm(html_content)
        
        # Save to JSON
        parser.save_to_json(elements, output_file)
        
        print(f"✅ Parsed {len(elements)} elements using FSM approach")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")

if __name__ == "__main__":
    main() 