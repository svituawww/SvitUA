#!/usr/bin/env python3
"""
Debug Meta Extraction - Test single quotes and special characters
"""

import re

def test_meta_extraction():
    """Test meta description extraction with single quotes and special characters."""
    
    print("🔍 Debug Meta Extraction Test")
    print("=" * 50)
    
    # Test case with single quotes in content
    test_html = '<meta name="description" content="Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об\'єднує людей, які вірять у силу підтримки, солідарності та дій.">'
    
    print(f"Input HTML: {test_html}")
    print()
    
    # Check if content contains single quotes
    content_start = test_html.find('content="') + 9
    content_end = test_html.rfind('"')
    content = test_html[content_start:content_end]
    
    print(f"Extracted content: {content}")
    has_single_quote = "об'єднує" in content
    print(f"Contains single quote: {has_single_quote}")
    print(f"Single quote position: {content.find(chr(39))}")
    print()
    
    # Test different regex patterns
    patterns = [
        r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']',
        r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']*(?:"[^"]*"[^"\']*)*)["\']',
        r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']*(?:\'[^\']*\'[^"\']*)*)["\']',
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern}")
        matches = re.findall(pattern, test_html, re.IGNORECASE)
        print(f"Matches: {matches}")
        if matches:
            print(f"First match length: {len(matches[0])}")
            print(f"First match: {matches[0]}")
        print()
    
    # Test with a simpler approach - find the content attribute specifically
    print("🔧 Alternative approach:")
    
    # Find meta tags with description
    meta_matches = re.findall(r'<meta\s+name\s*=\s*["\']description["\'][^>]*>', test_html, re.IGNORECASE)
    print(f"Meta tags found: {len(meta_matches)}")
    
    for meta_tag in meta_matches:
        print(f"Meta tag: {meta_tag}")
        
        # Extract content attribute
        content_match = re.search(r'content\s*=\s*["\']([^"\']+)["\']', meta_tag)
        if content_match:
            print(f"Content (simple): {content_match.group(1)}")
        else:
            print("No content found with simple pattern")
    
    print()
    
    # Test with HTML parser approach
    print("🔧 HTML-like parsing approach:")
    
    # Find the content attribute value more carefully
    content_pattern = r'content\s*=\s*["\']([^"\']*(?:\'[^\']*\'[^"\']*)*)["\']'
    content_matches = re.findall(content_pattern, test_html, re.IGNORECASE)
    print(f"Content matches: {content_matches}")
    
    if content_matches:
        print(f"Full content: {content_matches[0]}")
        print(f"Content length: {len(content_matches[0])}")

if __name__ == "__main__":
    test_meta_extraction() 