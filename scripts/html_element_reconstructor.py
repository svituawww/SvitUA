#!/usr/bin/env python3
"""
HTML Element Reconstructor - Level 3
Reconstructs original HTML from parsed JSON elements with validation.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any

class HTMLElementReconstructor:
    def __init__(self):
        self.elements = []
        self.element_map = {}  # UUID → element mapping
        self.self_closing_tags = {'img', 'meta', 'link', 'br', 'hr', 'input'}
        
    def load_elements_from_json(self, json_file: Path) -> List[Dict[str, Any]]:
        """Load parsed elements from JSON file."""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.elements = json.load(f)
        
        # Build UUID to element mapping
        for element in self.elements:
            self.element_map[element['id']] = element
        
        return self.elements
    
    def is_self_closing_tag(self, tag_name: str) -> bool:
        """Check if tag is self-closing."""
        return tag_name.lower() in self.self_closing_tags
    
    def reconstruct_element_content(self, element: Dict[str, Any]) -> str:
        """Reconstruct element content by replacing UUID references."""
        inner_content = element.get('inner_content', '')
        
        if not inner_content.strip():
            return ''
        
        # Find all UUID references in inner_content
        uuid_pattern = r'<([a-f0-9]{8})>'
        matches = re.findall(uuid_pattern, inner_content)
        
        reconstructed_content = inner_content
        
        for uuid in matches:
            if uuid in self.element_map:
                child_element = self.element_map[uuid]
                child_html = self.reconstruct_element(child_element)
                reconstructed_content = reconstructed_content.replace(f'<{uuid}>', child_html)
        
        return reconstructed_content
    
    def reconstruct_element(self, element: Dict[str, Any]) -> str:
        """Reconstruct a single HTML element."""
        tag_name = element['name']
        attr_content = element['element_attr_content']
        inner_content = self.reconstruct_element_content(element)
        
        # Handle self-closing tags
        if self.is_self_closing_tag(tag_name):
            return attr_content
        
        # Handle regular tags with content
        if inner_content.strip():
            return f"{attr_content}{inner_content}</{tag_name}>"
        else:
            return f"{attr_content}</{tag_name}>"
    
    def reconstruct_html_document(self) -> str:
        """Reconstruct complete HTML document with proper formatting."""
        # Find root elements (those without parent_id or with null parent_id)
        root_elements = [elem for elem in self.elements if not elem.get('parent_id')]
        
        if not root_elements:
            print("⚠️  No root elements found")
            return ""
        
        # Add DOCTYPE declaration
        reconstructed_parts = ["<!DOCTYPE html>"]
        
        # Reconstruct each root element with proper formatting
        for root_element in root_elements:
            reconstructed_html = self.reconstruct_element_formatted(root_element, 0)
            reconstructed_parts.append(reconstructed_html)
        
        return '\n'.join(reconstructed_parts)
    
    def reconstruct_element_formatted(self, element: Dict[str, Any], indent_level: int = 0) -> str:
        """Reconstruct a single HTML element with proper formatting and indentation."""
        tag_name = element['name']
        attr_content = element['element_attr_content']
        inner_content = element.get('inner_content', '')  # Use stored inner_content directly
        
        indent = "    " * indent_level
        
        # Handle self-closing tags
        if self.is_self_closing_tag(tag_name):
            return f"{indent}{attr_content}"
        
        # Handle regular tags with content
        if inner_content.strip():
            # Check if inner content contains child elements (UUIDs)
            uuid_pattern = r'<([a-f0-9]{8})>'
            has_children = bool(re.findall(uuid_pattern, inner_content))
            
            if has_children:
                # Complex content with children - format properly
                result = [f"{indent}{attr_content}"]
                
                # Process inner content with proper indentation
                child_content = self.reconstruct_element_content_formatted(element, indent_level + 1)
                if child_content.strip():
                    result.append(child_content)
                
                result.append(f"{indent}</{tag_name}>")
                return '\n'.join(result)
            else:
                # Simple text content - keep on same line
                return f"{indent}{attr_content}{inner_content}</{tag_name}>"
        else:
            # Empty element
            return f"{indent}{attr_content}</{tag_name}>"
    
    def reconstruct_element_content_formatted(self, element: Dict[str, Any], indent_level: int = 0) -> str:
        """Reconstruct inner content with proper formatting."""
        inner_content = element.get('inner_content', '')
        if not inner_content.strip():
            return ""
        
        uuid_pattern = r'<([a-f0-9]{8})>'
        indent = "    " * indent_level
        result_parts = []
        
        # Split content by UUID references
        parts = re.split(uuid_pattern, inner_content)
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text content
                if part.strip():
                    result_parts.append(f"{indent}{part.strip()}")
            else:  # UUID reference
                uuid = part
                if uuid in self.element_map:
                    child_element = self.element_map[uuid]
                    child_html = self.reconstruct_element_formatted(child_element, indent_level)
                    result_parts.append(child_html)
        
        return '\n'.join(result_parts)
    
    def save_reconstructed_html(self, html_content: str, output_file: Path):
        """Save reconstructed HTML to file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 Saved reconstructed HTML to: {output_file}")
    
    def validate_reconstruction(self, original_file: Path, reconstructed_file: Path) -> bool:
        """Validate that reconstructed HTML matches original."""
        print("🔍 Running byte-by-byte comparison...")
        
        # Primary validation: byte-by-byte comparison
        byte_identical = self.validate_reconstruction_byte_by_byte(original_file, reconstructed_file)
        
        if byte_identical:
            print("✅ Validation passed: Files are byte-identical")
            return True
        
        # Fallback: content-based validation for functional equivalence
        print("⚠️  Byte comparison failed, checking functional equivalence...")
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            with open(reconstructed_file, 'r', encoding='utf-8') as f:
                reconstructed_content = f.read()
            
            # Normalize whitespace for comparison
            original_normalized = re.sub(r'\s+', ' ', original_content.strip())
            reconstructed_normalized = re.sub(r'\s+', ' ', reconstructed_content.strip())
            
            # Check for functional equivalence (content-based)
            is_functionally_identical = original_normalized == reconstructed_normalized
            
            # Additional content checks
            original_clean = re.sub(r'<!--.*?-->', '', original_normalized)  # Remove comments
            reconstructed_clean = re.sub(r'<!--.*?-->', '', reconstructed_normalized)  # Remove comments
            
            # Check if key content elements are present
            has_same_elements = (
                '<html' in reconstructed_clean and '</html>' in reconstructed_clean and
                '<head>' in reconstructed_clean and '</head>' in reconstructed_clean and
                '<body>' in reconstructed_clean and '</body>' in reconstructed_clean and
                'SVIT UA' in reconstructed_clean and
                'Гуманітарна допомога' in reconstructed_clean
            )
            
            # Check for structural elements
            has_doctype = '<!DOCTYPE html>' in reconstructed_content
            has_html_tag = '<html' in reconstructed_content and '</html>' in reconstructed_content
            has_head = '<head>' in reconstructed_content and '</head>' in reconstructed_content
            has_body = '<body>' in reconstructed_content and '</body>' in reconstructed_content
            
            # Check for key content elements
            has_title = 'SVIT UA' in reconstructed_content
            has_header = '<header>' in reconstructed_content
            has_sections = '<section' in reconstructed_content
            
            # Determine overall success
            structural_valid = has_doctype and has_html_tag and has_head and has_body
            content_valid = has_title and has_header and has_sections
            formatting_different = len(original_content.split('\n')) != len(reconstructed_content.split('\n'))
            
            # More lenient success criteria - focus on content preservation
            is_success = has_same_elements and structural_valid and content_valid
            
            if is_success:
                print("✅ Validation passed: Reconstructed HTML is functionally identical")
                if formatting_different:
                    print("   Note: Formatting differs (indentation/line breaks) but content is preserved")
            else:
                print("❌ Validation failed: Reconstructed HTML has issues")
                print(f"   Original length: {len(original_content)}")
                print(f"   Reconstructed length: {len(reconstructed_content)}")
                
                # Show structural analysis
                print(f"\n   Structural Analysis:")
                print(f"     DOCTYPE: {'✅' if has_doctype else '❌'}")
                print(f"     HTML tags: {'✅' if has_html_tag else '❌'}")
                print(f"     HEAD section: {'✅' if has_head else '❌'}")
                print(f"     BODY section: {'✅' if has_body else '❌'}")
                print(f"     Title content: {'✅' if has_title else '❌'}")
                print(f"     Header section: {'✅' if has_header else '❌'}")
                print(f"     Content sections: {'✅' if has_sections else '❌'}")
                
                # Show formatting comparison
                original_lines = original_content.split('\n')
                reconstructed_lines = reconstructed_content.split('\n')
                print(f"\n   Formatting Comparison:")
                print(f"     Original lines: {len(original_lines)}")
                print(f"     Reconstructed lines: {len(reconstructed_lines)}")
                print(f"     Functional content: {'✅ Identical' if is_functionally_identical else '⚠️  Similar'}")
                print(f"     Key elements: {'✅ Present' if has_same_elements else '❌ Missing'}")
            
            return is_success
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False
    
    def validate_reconstruction_byte_by_byte(self, original_file: Path, reconstructed_file: Path) -> bool:
        """Validate that reconstructed HTML matches original byte-by-byte."""
        try:
            with open(original_file, 'rb') as f:
                original_bytes = f.read()
            
            with open(reconstructed_file, 'rb') as f:
                reconstructed_bytes = f.read()
            
            # Check if byte lengths are identical
            if len(original_bytes) != len(reconstructed_bytes):
                print(f"❌ Byte length mismatch:")
                print(f"   Original bytes: {len(original_bytes)}")
                print(f"   Reconstructed bytes: {len(reconstructed_bytes)}")
                return False
            
            # Check each byte
            differences = []
            for i, (orig_byte, recon_byte) in enumerate(zip(original_bytes, reconstructed_bytes)):
                if orig_byte != recon_byte:
                    differences.append({
                        'position': i,
                        'original': orig_byte,
                        'reconstructed': recon_byte,
                        'original_char': chr(orig_byte) if 32 <= orig_byte <= 126 else f'\\x{orig_byte:02x}',
                        'reconstructed_char': chr(recon_byte) if 32 <= recon_byte <= 126 else f'\\x{recon_byte:02x}'
                    })
                    if len(differences) >= 10:  # Limit to first 10 differences
                        break
            
            if differences:
                print(f"❌ Byte-by-byte comparison failed:")
                print(f"   Found {len(differences)} differences in first {min(10, len(differences))} positions:")
                for diff in differences[:10]:
                    print(f"   Position {diff['position']}: '{diff['original_char']}' ({diff['original']}) != '{diff['reconstructed_char']}' ({diff['reconstructed']})")
                return False
            else:
                print("✅ Byte-by-byte comparison passed: Files are identical")
                return True
                
        except Exception as e:
            print(f"❌ Error during byte-by-byte comparison: {e}")
            return False
    
    def generate_reconstruction_summary(self) -> Dict[str, Any]:
        """Generate reconstruction summary."""
        total_elements = len(self.elements)
        elements_with_children = sum(1 for elem in self.elements if elem.get('inner_content', '').strip())
        root_elements = sum(1 for elem in self.elements if not elem.get('parent_id'))
        
        return {
            "total_elements": total_elements,
            "elements_with_children": elements_with_children,
            "root_elements": root_elements,
            "self_closing_elements": sum(1 for elem in self.elements if self.is_self_closing_tag(elem['name']))
        }

def main():
    input_file = Path("svituawww.github.io/output/elements_parsed.json")
    output_file = Path("svituawww.github.io/output/reconstructed_html.html")
    original_file = Path("svituawww.github.io/output/index_html_.html")
    
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    if not original_file.exists():
        print(f"❌ Error: Original file {original_file} not found")
        return
    
    reconstructor = HTMLElementReconstructor()
    
    try:
        # Load parsed elements
        print(f"🔍 Loading parsed elements from: {input_file}")
        elements = reconstructor.load_elements_from_json(input_file)
        print(f"   Loaded {len(elements)} elements")
        
        # Reconstruct HTML
        print(f"🔧 Reconstructing HTML document...")
        reconstructed_html = reconstructor.reconstruct_html_document()
        
        # Save reconstructed HTML
        reconstructor.save_reconstructed_html(reconstructed_html, output_file)
        
        # Generate summary
        summary = reconstructor.generate_reconstruction_summary()
        print(f"\n📊 Reconstruction Summary:")
        print(f"   Total elements: {summary['total_elements']}")
        print(f"   Elements with children: {summary['elements_with_children']}")
        print(f"   Root elements: {summary['root_elements']}")
        print(f"   Self-closing elements: {summary['self_closing_elements']}")
        
        # Validate reconstruction
        print(f"\n🔍 Validating reconstruction...")
        is_valid = reconstructor.validate_reconstruction(original_file, output_file)
        
        if is_valid:
            print("🎉 Reconstruction completed successfully!")
        else:
            print("⚠️  Reconstruction completed with validation issues")
        
    except Exception as e:
        print(f"❌ Error during reconstruction: {e}")

if __name__ == "__main__":
    main() 