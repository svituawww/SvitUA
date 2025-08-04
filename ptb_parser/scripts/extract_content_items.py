#!/usr/bin/env python3
"""
Content Extraction Module
Extracts specific attributes and content from HTML elements
Enhanced with robust image attribute extraction from id_part4
"""

import re
from typing import Optional, List, Tuple, Dict

class ContentExtractor:
    """Extract specific content and attributes from HTML elements with enhanced image extraction."""
    
    def __init__(self):
        # Enhanced regex patterns for image extraction
        self.img_patterns = {
            'src': r'src\s*=\s*["\']([^"\']+)["\']',
            'alt': r'alt\s*=\s*["\']([^"\']+)["\']',
            'srcset': r'srcset\s*=\s*["\']([^"\']+)["\']',
            'sizes': r'sizes\s*=\s*["\']([^"\']+)["\']'
        }
    
    def extract_a_from_element(self, content_body: str) -> List[tuple]:
        """Extract a from an element.
           example1 = <a href="#" class="lang-btn" title="English">
           example2 = <a href="#contact">
           example3 = <a href="#home" onclick="closeMobileMenu()"> 
           we need to extract href with title or without title           

        """   
        result = []

        # first check if content_body is a link
        if not content_body.startswith('<a'):
            return result
        
        
        # Extract href (always present in <a> tags)
        href_match = re.search(r'href="([^"]+)"', content_body)
        if href_match:
            href = href_match.group(1)
            result.append(("a", "href", href))
        
        # Extract title (optional)
        title_match = re.search(r'title="([^"]+)"', content_body)
        if title_match:
            title = title_match.group(1)
            result.append(("a", "title", title))
        
        return result

    def extract_meta_from_element(self, content_body: str) -> List[tuple]:
        """Extract meta from an element.
           just extract content of meta entire tag
        """        
        result = []

        if not content_body.startswith('<meta'):
            return result
        
        result.append(("meta", "entire_tag", content_body))                
        
        return result

        

    def extract_img_from_element(self, content_body: str) -> List[tuple]:
        """
        Enhanced image attribute extraction with comprehensive regex patterns.
        
        Args:
            content_body (str): HTML content containing img tag
            
        Returns:
            List[tuple]: List of (element_type, attribute_name, attribute_value) tuples
        """
        result = []
        
        # Check if content_body contains an img tag
        if not re.search(r'<img\b', content_body, re.IGNORECASE):
            return result
        
        # Extract each attribute using enhanced patterns
        for attr_name, pattern in self.img_patterns.items():
            match = re.search(pattern, content_body, re.IGNORECASE)
            if match:
                attr_value = match.group(1)
                result.append(("img", attr_name, attr_value))
        
        return result

    def validate_img_extraction(self, content_body: str) -> Dict:
        """
        Validate img extraction and return detailed results.
        
        Args:
            content_body (str): HTML content to validate
            
        Returns:
            Dict: Validation results with extracted attributes and metadata
        """
        extracted = self.extract_img_from_element(content_body)
        
        validation_result = {
            'is_img_tag': bool(re.search(r'<img\b', content_body, re.IGNORECASE)),
            'extracted_attributes': extracted,
            'attribute_count': len(extracted),
            'has_required_src': any(attr[1] == 'src' for attr in extracted),
            'all_attributes': {
                'src': None,
                'alt': None,
                'srcset': None,
                'sizes': None
            }
        }
        
        # Populate found attributes
        for element_type, attr_name, attr_value in extracted:
            if attr_name in validation_result['all_attributes']:
                validation_result['all_attributes'][attr_name] = attr_value
        
        return validation_result

    def extract_content_from_element(self, content_body: str) -> List[tuple]:
        """Extract content type from an element."""
        result = []
        result.extend(self.extract_a_from_element(content_body))
        result.extend(self.extract_img_from_element(content_body))
        result.extend(self.extract_meta_from_element(content_body))
        
        # If no attributes found, return the content as a general element
        if not result:
            result.append(('element', 'general', content_body))
        
        return result

    def develop_template_body(self, content_body: str, content_items_records: List[tuple]) -> str:
        """
        Develop template body from content body by replacing attribute values with UUID placeholders.
        
        Args:
            content_body (str): Original HTML content (e.g., '<img src="image.jpg" alt="Logo">')
            content_items_records (List[tuple]): List of (item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at) tuples
            
        Returns:
            str: Template body with UUID placeholders (e.g., '<img src="uuid_abc123" alt="uuid_def456">')
        """
        import re
        result = content_body
        
        # Sort records by item_id to ensure consistent replacement order
        sorted_records = sorted(content_items_records, key=lambda x: x[0])
        
        for record in sorted_records:
            # Unpack the full database record
            item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
            
            if type_item == 'srcset' and type_element == 'img':
                # Replace the entire srcset attribute with one UUID
                srcset_pattern = rf'srcset\s*=\s*["\']([^"\']+)["\']'
                match = re.search(srcset_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire srcset value with the UUID
                    result = re.sub(srcset_pattern, f'srcset="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'sizes' and type_element == 'img':
                # Replace the entire sizes attribute with one UUID
                sizes_pattern = rf'sizes\s*=\s*["\']([^"\']+)["\']'
                match = re.search(sizes_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire sizes value with the UUID
                    result = re.sub(sizes_pattern, f'sizes="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'src' and type_element == 'img':
                # Replace the entire src attribute with one UUID
                src_pattern = rf'src\s*=\s*["\']([^"\']+)["\']'
                match = re.search(src_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire src value with the UUID
                    result = re.sub(src_pattern, f'src="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'alt' and type_element == 'img':
                # Replace the entire alt attribute with one UUID
                alt_pattern = rf'alt\s*=\s*["\']([^"\']+)["\']'
                match = re.search(alt_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire alt value with the UUID
                    result = re.sub(alt_pattern, f'alt="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'href' and type_element == 'a':
                # Replace the entire href attribute with one UUID
                href_pattern = rf'href\s*=\s*["\']([^"\']+)["\']'
                match = re.search(href_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire href value with the UUID
                    result = re.sub(href_pattern, f'href="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'title' and type_element == 'a':
                # Replace the entire title attribute with one UUID
                title_pattern = rf'title\s*=\s*["\']([^"\']+)["\']'
                match = re.search(title_pattern, result, re.IGNORECASE)
                if match:
                    # Replace the entire title value with the UUID
                    result = re.sub(title_pattern, f'title="uuid_{uuid_item}"', result, flags=re.IGNORECASE)
            elif type_item == 'text' and type_element == 'between_elements':
                # Replace the entire text with one UUID
                result = result.replace(item_body, f'uuid_{uuid_item}')
            elif type_item == 'entire_tag' and type_element == 'meta':
                # Replace the entire meta tag with one UUID any way with or without name="description"
                meta_pattern = rf'<meta[^>]*>'                
                match = re.search(meta_pattern, result, re.IGNORECASE)
                if match:                   
                    # Replace the entire meta tag with the UUID any way with or without name="description"
                    result = result.replace(item_body, f'meta_uuid_{uuid_item}')
            else:
                # Standard replacement for other attributes
                if item_body in result:
                    result = result.replace(item_body, f'uuid_{uuid_item}')

        
        return result

