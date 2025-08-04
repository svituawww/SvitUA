#!/usr/bin/env python3
"""
Debug Case Issues - Test the failing test cases
"""

import re

def test_failing_cases():
    """Test the failing test cases specifically."""
    
    print("🔍 Debug Failing Test Cases")
    print("=" * 50)
    
    # Test Case 3: Mixed Whitespace
    test_case_3 = '<meta  name  =  "description"  content  =  "Description with extra spaces">'
    print(f"Test Case 3: {test_case_3}")
    
    meta_pattern = r'<meta\s+name\s*=\s*["\']description["\'][^>]*>'
    matches = re.findall(meta_pattern, test_case_3, re.IGNORECASE)
    print(f"Meta matches: {matches}")
    
    if matches:
        meta_tag = matches[0]
        print(f"Meta tag: {meta_tag}")
        
        # Extract content
        content_start = meta_tag.find('content="')
        if content_start == -1:
            content_start = meta_tag.find("content='")
        
        if content_start != -1:
            quote_start = meta_tag.find('"', content_start + 8)
            if quote_start == -1:
                quote_start = meta_tag.find("'", content_start + 8)
            
            if quote_start != -1:
                quote_char = meta_tag[quote_start]
                content_end = meta_tag.rfind(quote_char)
                
                if content_end > quote_start:
                    content = meta_tag[quote_start + 1:content_end]
                    print(f"Extracted content: {content}")
    
    print()
    
    # Test Case 8: Case Variations
    test_case_8 = '''<meta NAME="DESCRIPTION" CONTENT="Case insensitive test">
<meta Name="Description" Content="Mixed case test">'''
    print(f"Test Case 8: {test_case_8}")
    
    matches = re.findall(meta_pattern, test_case_8, re.IGNORECASE)
    print(f"Meta matches: {len(matches)}")
    
    for i, meta_tag in enumerate(matches):
        print(f"Meta tag {i+1}: {meta_tag}")
        
        # Extract content
        content_start = meta_tag.find('content="')
        if content_start == -1:
            content_start = meta_tag.find("content='")
        
        if content_start != -1:
            quote_start = meta_tag.find('"', content_start + 8)
            if quote_start == -1:
                quote_start = meta_tag.find("'", content_start + 8)
            
            if quote_start != -1:
                quote_char = meta_tag[quote_start]
                content_end = meta_tag.rfind(quote_char)
                
                if content_end > quote_start:
                    content = meta_tag[quote_start + 1:content_end]
                    print(f"Extracted content {i+1}: {content}")

if __name__ == "__main__":
    test_failing_cases() 