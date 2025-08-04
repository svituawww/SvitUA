#!/usr/bin/env python3
"""
id_part6: Enhanced Meta Description Extraction Test
"""

import re
import time
from typing import List, Dict

def extract_meta_description(html_content: str) -> List[str]:
    """
    Extract meta description content from HTML.
    
    Args:
        html_content (str): HTML content to search
        
    Returns:
        List[str]: List of description content values found
    """
    # Find all meta tags with name="description"
    meta_pattern = r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']'
    
    # Find all matches
    matches = re.findall(meta_pattern, html_content, re.IGNORECASE)
    
    return matches

def extract_meta_description_robust(html_content: str) -> List[str]:
    """
    Extract meta description content from HTML with robust quote handling.
    
    Args:
        html_content (str): HTML content to search
        
    Returns:
        List[str]: List of description content values found
    """
    # Find meta tags with description first - more flexible pattern
    meta_pattern = r'<meta\s+name\s*=\s*["\']description["\'][^>]*>'
    meta_matches = re.findall(meta_pattern, html_content, re.IGNORECASE)
    
    descriptions = []
    for meta_tag in meta_matches:
        # Use a hybrid approach: find content attribute position, then extract manually
        content_match = re.search(r'content\s*=\s*["\']', meta_tag, re.IGNORECASE)
        if content_match:
            # Get the position after the content attribute
            start_pos = content_match.end()
            quote_char = meta_tag[start_pos - 1]  # The quote character used
            
            # Find the closing quote (last occurrence of the same quote type)
            end_pos = meta_tag.rfind(quote_char)
            
            if end_pos > start_pos:
                content = meta_tag[start_pos:end_pos]
                descriptions.append(content)
    
    return descriptions

def validate_meta_extraction(html_content: str) -> Dict:
    """
    Validate meta description extraction and return detailed results.
    
    Args:
        html_content (str): HTML content to validate
        
    Returns:
        dict: Validation results with extracted descriptions and metadata
    """
    descriptions = extract_meta_description_robust(html_content)
    
    # Check for other meta tags that should NOT match
    other_meta_pattern = r'<meta\s+name\s*=\s*["\'](?!description)[^"\']+["\']'
    other_meta_matches = re.findall(other_meta_pattern, html_content, re.IGNORECASE)
    
    validation_result = {
        'descriptions_found': descriptions,
        'description_count': len(descriptions),
        'other_meta_tags': other_meta_matches,
        'other_meta_count': len(other_meta_matches),
        'is_clean_extraction': len(other_meta_matches) == 0 or all('description' not in tag.lower() for tag in other_meta_matches)
    }
    
    return validation_result

def test_meta_description_extraction():
    """Test meta description extraction with comprehensive test cases."""
    
    print("🎯 id_part6: Enhanced Meta Description Extraction Test")
    print("=" * 80)
    
    # Test cases from id_part6 specifications
    test_cases = [
        {
            'name': 'Test Case 1: Standard Description Meta',
            'html': '<meta name="description" content="Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об\'єднує людей, які вірять у силу підтримки, солідарності та дій.">',
            'should_match': True,
            'expected_content': 'Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об\'єднує людей, які вірять у силу підтримки, солідарності та дій.'
        },
        {
            'name': 'Test Case 2: Single Quotes',
            'html': '<meta name=\'description\' content=\'This is a description with single quotes\'>',
            'should_match': True,
            'expected_content': 'This is a description with single quotes'
        },
        {
            'name': 'Test Case 3: Mixed Whitespace',
            'html': '<meta  name  =  "description"  content  =  "Description with extra spaces">',
            'should_match': True,
            'expected_content': 'Description with extra spaces'
        },
        {
            'name': 'Test Case 4: Viewport Meta (Should NOT Match)',
            'html': '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            'should_match': False,
            'expected_content': None
        },
        {
            'name': 'Test Case 5: Keywords Meta (Should NOT Match)',
            'html': '<meta name="keywords" content="html, css, javascript">',
            'should_match': False,
            'expected_content': None
        },
        {
            'name': 'Test Case 6: Robots Meta (Should NOT Match)',
            'html': '<meta name="robots" content="noindex, nofollow">',
            'should_match': False,
            'expected_content': None
        },
        {
            'name': 'Test Case 7: Multiple Meta Tags',
            'html': '''<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="This should be extracted">
<meta name="keywords" content="test, example">''',
            'should_match': True,
            'expected_content': 'This should be extracted'
        },
        {
            'name': 'Test Case 8: Case Variations',
            'html': '''<meta NAME="DESCRIPTION" CONTENT="Case insensitive test">
<meta Name="Description" Content="Mixed case test">''',
            'should_match': True,
            'expected_content': 'Case insensitive test'  # First match
        },
        {
            'name': 'Test Case 9: Special Characters in Content',
            'html': '<meta name="description" content="Description with &quot;quotes&quot; &amp; symbols">',
            'should_match': True,
            'expected_content': 'Description with &quot;quotes&quot; &amp; symbols'
        },
        {
            'name': 'Test Case 10: Self-Closing Tag',
            'html': '<meta name="description" content="Self closing tag" />',
            'should_match': True,
            'expected_content': 'Self closing tag'
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 {test_case['name']}")
        print(f"Input: {test_case['html']}")
        
        # Extract descriptions using robust method
        descriptions = extract_meta_description_robust(test_case['html'])
        
        # Validate extraction
        validation = validate_meta_extraction(test_case['html'])
        
        print(f"Extracted: {descriptions}")
        print(f"Count: {validation['description_count']}")
        
        # Check if test passed
        if test_case['should_match']:
            if descriptions and test_case['expected_content'] in descriptions:
                print("✅ PASSED: Description extracted correctly")
                passed_tests += 1
            else:
                print("❌ FAILED: Description should have been extracted")
        else:
            if not descriptions:
                print("✅ PASSED: No description extracted (correct)")
                passed_tests += 1
            else:
                print("❌ FAILED: Description should NOT have been extracted")
        
        # Show validation details
        if validation['other_meta_count'] > 0:
            print(f"Other meta tags found: {validation['other_meta_count']}")
            print(f"Clean extraction: {validation['is_clean_extraction']}")
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    return passed_tests == total_tests

def test_performance():
    """Test performance with large HTML content."""
    
    print("\n🚀 Performance Testing")
    print("=" * 50)
    
    # Create large HTML content
    base_html = '''<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Performance test description">
<meta name="keywords" content="test, performance">
<meta name="robots" content="noindex">'''
    
    # Repeat 1000 times to create large content
    large_html = base_html * 1000
    
    print(f"Large HTML size: {len(large_html)} characters")
    
    # Measure extraction time
    start_time = time.time()
    descriptions = extract_meta_description(large_html)
    end_time = time.time()
    
    extraction_time = end_time - start_time
    print(f"Extraction time: {extraction_time:.4f} seconds")
    print(f"Descriptions found: {len(descriptions)}")
    
    # Performance benchmark
    if extraction_time < 1.0:
        print("✅ Performance: Good (< 1 second)")
    elif extraction_time < 5.0:
        print("⚠️ Performance: Acceptable (< 5 seconds)")
    else:
        print("❌ Performance: Poor (> 5 seconds)")
    
    return extraction_time < 5.0

def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("\n🔍 Edge Case Testing")
    print("=" * 50)
    
    edge_cases = [
        {
            'name': 'Empty HTML',
            'html': '',
            'expected_count': 0
        },
        {
            'name': 'No meta tags',
            'html': '<html><head><title>Test</title></head><body>Content</body></html>',
            'expected_count': 0
        },
        {
            'name': 'Malformed meta tag',
            'html': '<meta name="description" content="Test"',
            'expected_count': 1  # Current regex will match this, which is expected behavior
        },
        {
            'name': 'Multiple descriptions',
            'html': '''<meta name="description" content="First description">
<meta name="description" content="Second description">''',
            'expected_count': 2
        },
        {
            'name': 'Description with newlines',
            'html': '''<meta name="description" content="Description with
newlines and spaces">''',
            'expected_count': 1
        }
    ]
    
    edge_passed = 0
    edge_total = len(edge_cases)
    
    for case in edge_cases:
        print(f"\n📋 {case['name']}")
        descriptions = extract_meta_description(case['html'])
        
        if len(descriptions) == case['expected_count']:
            print(f"✅ PASSED: Found {len(descriptions)} descriptions (expected {case['expected_count']})")
            edge_passed += 1
        else:
            print(f"❌ FAILED: Found {len(descriptions)} descriptions (expected {case['expected_count']})")
    
    print(f"\n📊 Edge Case Results: {edge_passed}/{edge_total} tests passed")
    
    return edge_passed == edge_total

def main():
    """Main function to run all tests."""
    
    print("🎯 id_part6: Enhanced Meta Description Extraction")
    print("=" * 80)
    
    # Run comprehensive tests
    basic_tests_passed = test_meta_description_extraction()
    performance_passed = test_performance()
    edge_cases_passed = test_edge_cases()
    
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    
    print(f"✅ Basic Tests: {'PASSED' if basic_tests_passed else 'FAILED'}")
    print(f"✅ Performance Tests: {'PASSED' if performance_passed else 'FAILED'}")
    print(f"✅ Edge Case Tests: {'PASSED' if edge_cases_passed else 'FAILED'}")
    
    overall_passed = basic_tests_passed and performance_passed and edge_cases_passed
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_passed else '❌ SOME TESTS FAILED'}")
    
    if overall_passed:
        print("\n🚀 id_part6 Implementation: SUCCESSFUL")
        print("✅ Meta description extraction working correctly")
        print("✅ Other meta tags properly excluded")
        print("✅ Performance within acceptable limits")
        print("✅ Edge cases handled properly")
    else:
        print("\n🔧 id_part6 Implementation: NEEDS IMPROVEMENT")
        print("❌ Some tests failed - review implementation")

if __name__ == "__main__":
    main() 