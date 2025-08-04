#!/usr/bin/env python3
"""
Test Updated Extraction Implementation
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

def test_updated_extraction():
    """Test the updated extraction implementation."""
    
    print("🎯 Test Updated Extraction Implementation")
    print("=" * 80)
    
    # Test case with single quotes in content (the problematic case)
    test_content = '''<meta name="description" content="Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об'єднує людей, які вірять у силу підтримки, солідарності та дій.">'''
    
    content_extractor = ContentExtractor()
    
    print("📋 Test Content:")
    print(test_content)
    print()
    
    # Extract content using the updated method
    extracted = content_extractor.extract_content_from_element(test_content)
    
    print("🔍 Extracted Content:")
    for element_type, attr_name, attr_value in extracted:
        print(f"  {element_type}.{attr_name}: {attr_value}")
        print(f"  Length: {len(attr_value)}")
        has_apostrophe = "об'єднує" in attr_value
        print(f"  Contains apostrophe: {has_apostrophe}")
    
    print()
    
    # Test with mixed case
    test_content_2 = '''<meta NAME="DESCRIPTION" CONTENT="Test with mixed case">'''
    print("📋 Test Content 2 (Mixed Case):")
    print(test_content_2)
    
    extracted_2 = content_extractor.extract_content_from_element(test_content_2)
    print("🔍 Extracted Content 2:")
    for element_type, attr_name, attr_value in extracted_2:
        print(f"  {element_type}.{attr_name}: {attr_value}")
    
    print()
    
    # Test with single quotes
    test_content_3 = '''<meta name='description' content='Test with single quotes'>'''
    print("📋 Test Content 3 (Single Quotes):")
    print(test_content_3)
    
    extracted_3 = content_extractor.extract_content_from_element(test_content_3)
    print("🔍 Extracted Content 3:")
    for element_type, attr_name, attr_value in extracted_3:
        print(f"  {element_type}.{attr_name}: {attr_value}")
    
    print()
    
    # Test with mixed whitespace
    test_content_4 = '''<meta  name  =  "description"  content  =  "Test with extra spaces">'''
    print("📋 Test Content 4 (Mixed Whitespace):")
    print(test_content_4)
    
    extracted_4 = content_extractor.extract_content_from_element(test_content_4)
    print("🔍 Extracted Content 4:")
    for element_type, attr_name, attr_value in extracted_4:
        print(f"  {element_type}.{attr_name}: {attr_value}")
    
    print()
    
    # Summary
    print("📊 Summary:")
    test1_passed = extracted and "об'єднує" in extracted[0][2]
    test2_passed = extracted_2 and "Test with mixed case" in extracted_2[0][2]
    test3_passed = extracted_3 and "Test with single quotes" in extracted_3[0][2]
    test4_passed = extracted_4 and "Test with extra spaces" in extracted_4[0][2]
    
    print(f"  Test 1 (Apostrophe): {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  Test 2 (Mixed Case): {'PASSED' if test2_passed else 'FAILED'}")
    print(f"  Test 3 (Single Quotes): {'PASSED' if test3_passed else 'FAILED'}")
    print(f"  Test 4 (Whitespace): {'PASSED' if test4_passed else 'FAILED'}")

if __name__ == "__main__":
    test_updated_extraction() 