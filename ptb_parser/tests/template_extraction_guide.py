#!/usr/bin/env python3
"""
Template Extraction and Replacement Guide
Based on lessons learned from id_part6 and previous implementations
"""

import re
from typing import List, Dict, Tuple

class TemplateExtractor:
    """
    Right approach for template extraction and replacement
    """
    
    def __init__(self):
        # Store extraction patterns for different HTML elements
        self.extraction_patterns = {
            'meta_description': r'<meta\s+name\s*=\s*["\']description["\'][^>]*>',
            'img_src': r'<img[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>',
            'img_alt': r'<img[^>]*alt\s*=\s*["\']([^"\']+)["\'][^>]*>',
            'img_srcset': r'<img[^>]*srcset\s*=\s*["\']([^"\']+)["\'][^>]*>',
            'img_sizes': r'<img[^>]*sizes\s*=\s*["\']([^"\']+)["\'][^>]*>',
            'a_href': r'<a[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>',
            'a_title': r'<a[^>]*title\s*=\s*["\']([^"\']+)["\'][^>]*>'
        }
    
    def extract_content_robust(self, html_content: str, content_type: str) -> List[str]:
        """
        Robust extraction method (like id_part6 approach)
        
        Args:
            html_content (str): HTML content to search
            content_type (str): Type of content to extract (meta_description, img_src, etc.)
            
        Returns:
            List[str]: List of extracted content values
        """
        if content_type not in self.extraction_patterns:
            return []
        
        # Step 1: Find all matching elements
        pattern = self.extraction_patterns[content_type]
        element_matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        # Step 2: Extract attribute values using hybrid approach
        extracted_values = []
        
        for element in element_matches:
            if content_type == 'meta_description':
                # Use the robust approach from id_part6
                content_match = re.search(r'content\s*=\s*["\']', element, re.IGNORECASE)
                if content_match:
                    start_pos = content_match.end()
                    quote_char = element[start_pos - 1]
                    end_pos = element.rfind(quote_char)
                    
                    if end_pos > start_pos:
                        content = element[start_pos:end_pos]
                        extracted_values.append(content)
            else:
                # For other attributes, use the captured group
                if isinstance(element, tuple):
                    extracted_values.extend(element)
                else:
                    extracted_values.append(element)
        
        return extracted_values
    
    def create_template_body(self, html_content: str, content_items_records: List[Tuple]) -> str:
        """
        Create template body by replacing content with UUIDs
        
        Args:
            html_content (str): Original HTML content
            content_items_records (List[Tuple]): Database records with UUIDs
            
        Returns:
            str: Template body with UUID replacements
        """
        result = html_content
        
        # Sort records by item_id for consistent replacement
        sorted_records = sorted(content_items_records, key=lambda x: x[0])
        
        for record in sorted_records:
            # Unpack database record
            item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
            
            if type_item == 'srcset':
                # Special handling for srcset (like id_part7)
                srcset_pattern = rf'srcset\s*=\s*["\']([^"\']+)["\']'
                match = re.search(srcset_pattern, result, re.IGNORECASE)
                if match:
                    # Replace entire srcset with one UUID
                    result = re.sub(srcset_pattern, f'srcset="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            else:
                # Standard replacement for other attributes
                if item_body in result:
                    result = result.replace(item_body, f'uuid_{uuid_item}')
        
        return result
    
    def extract_and_replace_workflow(self, html_content: str) -> Dict:
        """
        Complete workflow: Extract content and create template
        
        Args:
            html_content (str): HTML content to process
            
        Returns:
            Dict: Results with extracted content and template
        """
        results = {
            'extracted_content': {},
            'template_body': html_content,
            'uuid_mappings': {}
        }
        
        # Step 1: Extract all types of content
        for content_type in self.extraction_patterns.keys():
            extracted = self.extract_content_robust(html_content, content_type)
            results['extracted_content'][content_type] = extracted
        
        # Step 2: Generate UUIDs for extracted content
        import uuid
        uuid_counter = 0
        
        for content_type, content_list in results['extracted_content'].items():
            for content in content_list:
                # Generate unique UUID (8 characters like in the project)
                unique_id = str(uuid.uuid4())[:8]
                results['uuid_mappings'][content] = unique_id
                
                # Replace in template
                results['template_body'] = results['template_body'].replace(
                    content, f'uuid_{unique_id}'
                )
        
        return results

def demonstrate_right_approach():
    """Demonstrate the right approach with examples."""
    
    print("🎯 Right Approach for Template Extraction and Replacement")
    print("=" * 80)
    
    # Example HTML content
    html_content = '''<html>
<head>
    <meta name="description" content="Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об'єднує людей, які вірять у силу підтримки, солідарності та дій.">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <img src="https://example.com/image.jpg" alt="Logo" srcset="https://example.com/image.jpg 1x, https://example.com/image@2x.jpg 2x" sizes="100vw">
    <a href="#contact" title="Contact Us">Contact</a>
</body>
</html>'''
    
    extractor = TemplateExtractor()
    
    print("📋 Original HTML:")
    print(html_content)
    print()
    
    # Step 1: Extract content
    print("🔍 Step 1: Extract Content")
    print("-" * 40)
    
    for content_type in ['meta_description', 'img_src', 'img_alt', 'img_srcset', 'a_href']:
        extracted = extractor.extract_content_robust(html_content, content_type)
        print(f"{content_type}: {extracted}")
    
    print()
    
    # Step 2: Create template
    print("🔧 Step 2: Create Template")
    print("-" * 40)
    
    # Simulate database records
    content_items_records = [
        (1, 1, 'abc12345', 'meta', 'description', 'Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об\'єднує людей, які вірять у силу підтримки, солідарності та дій.', '2025-01-01', '2025-01-01'),
        (2, 1, 'def67890', 'img', 'src', 'https://example.com/image.jpg', '2025-01-01', '2025-01-01'),
        (3, 1, 'ghi11111', 'img', 'alt', 'Logo', '2025-01-01', '2025-01-01'),
        (4, 1, 'jkl22222', 'img', 'srcset', 'https://example.com/image.jpg 1x, https://example.com/image@2x.jpg 2x', '2025-01-01', '2025-01-01'),
        (5, 1, 'mno33333', 'a', 'href', '#contact', '2025-01-01', '2025-01-01')
    ]
    
    template_body = extractor.create_template_body(html_content, content_items_records)
    
    print("Template Body:")
    print(template_body)
    print()
    
    # Step 3: Complete workflow
    print("🚀 Step 3: Complete Workflow")
    print("-" * 40)
    
    workflow_results = extractor.extract_and_replace_workflow(html_content)
    
    print("Extracted Content:")
    for content_type, content_list in workflow_results['extracted_content'].items():
        if content_list:
            print(f"  {content_type}: {content_list}")
    
    print("\nUUID Mappings:")
    for content, uuid_val in workflow_results['uuid_mappings'].items():
        print(f"  {content[:50]}... -> uuid_{uuid_val}")
    
    print("\nFinal Template:")
    print(workflow_results['template_body'])

if __name__ == "__main__":
    demonstrate_right_approach() 