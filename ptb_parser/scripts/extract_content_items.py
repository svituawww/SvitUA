#!/usr/bin/env python3
"""
Content Extraction Module
Extracts specific attributes and content from HTML elements
"""

import re
from typing import Optional

class ContentExtractor:
    """Extract specific content and attributes from HTML elements."""
    
    def extract_href_from_element(self, content_body: str) -> Optional[str]:
        """Extract href from an element."""
        href_pattern = r'href="([^"]+)"'
        match = re.search(href_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_src_from_element(self, content_body: str) -> Optional[str]:
        """Extract src from an element."""
        src_pattern = r'src="([^"]+)"'
        match = re.search(src_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_alt_from_element(self, content_body: str) -> Optional[str]:
        """Extract alt from an element."""
        alt_pattern = r'alt="([^"]+)"'
        match = re.search(alt_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_rel_from_element(self, content_body: str) -> Optional[str]:
        """Extract rel from an element."""
        rel_pattern = r'rel="([^"]+)"'
        match = re.search(rel_pattern, content_body)
        if match:
            return match.group(1)
        return None

    def extract_content_from_element(self, content_body: str) -> str:
        """Extract content type from an element."""
        if 'href' in content_body.lower():
            return 'href'
        if 'src' in content_body.lower():
            return 'src'
        if 'alt' in content_body.lower():
            return 'alt'
        if 'rel' in content_body.lower():
            return 'rel'
        return content_body 