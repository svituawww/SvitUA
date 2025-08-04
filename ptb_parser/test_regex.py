#!/usr/bin/env python3
"""
Enhanced Image Attribute Extraction Testing Framework
Implementation of id_part4 testing requirements
"""

import re
from typing import List, Dict, Tuple, Optional

class ImageAttributeExtractor:
    """Enhanced image attribute extraction with comprehensive testing."""
    
    def __init__(self):
        # Comprehensive regex patterns for testing
        self.patterns = {
            'src': [
                r'src\s*=\s*["\']([^"\']+)["\']',  # Handles both single and double quotes
                r'src\s*=\s*["\']([^"\']+)["\']',  # Alternative with better whitespace handling
            ],
            'alt': [
                r'alt\s*=\s*["\']([^"\']+)["\']',
                r'alt\s*=\s*["\']([^"\']+)["\']',
            ],
            'srcset': [
                r'srcset\s*=\s*["\']([^"\']+)["\']',
                r'srcset\s*=\s*["\']([^"\']+)["\']',
            ],
            'sizes': [
                r'sizes\s*=\s*["\']([^"\']+)["\']',
                r'sizes\s*=\s*["\']([^"\']+)["\']',
            ]
        }
    
    def extract_img_from_element(self, content_body: str) -> List[Tuple[str, str, str]]:
        """
        Extract all img attributes from an element with enhanced regex patterns.
        
        Args:
            content_body (str): HTML content containing img tag
            
        Returns:
            List[Tuple[str, str, str]]: List of (element_type, attribute_name, attribute_value) tuples
        """
        result = []
        
        # Check if content_body contains an img tag
        if not re.search(r'<img\b', content_body, re.IGNORECASE):
            return result
        
        # Enhanced regex patterns with better whitespace and quote handling
        patterns = {
            'src': r'src\s*=\s*["\']([^"\']+)["\']',
            'alt': r'alt\s*=\s*["\']([^"\']+)["\']',
            'srcset': r'srcset\s*=\s*["\']([^"\']+)["\']',
            'sizes': r'sizes\s*=\s*["\']([^"\']+)["\']'
        }
        
        # Extract each attribute
        for attr_name, pattern in patterns.items():
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
    
    def test_regex_patterns(self) -> None:
        """Test function for validation with comprehensive test cases."""
        test_cases = [
            # Test Case 1: Complex img tag with all attributes
            '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Літературний вечір" 
                 srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                         https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
                         https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
                         https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
                         https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
                 sizes="(max-width: 768px) 100vw, 400px">''',
            
            # Test Case 2: Simple img tag
            '<img src="image.jpg" alt="Simple image">',
            
            # Test Case 3: img tag with single quotes
            "<img src='image.png' alt='Single quoted' srcset='image.png 1x'>",
            
            # Test Case 4: img tag with mixed quotes and spaces
            '<img  src = "image.jpg"  alt = "Mixed spacing"  srcset = "image.jpg 1x"  sizes = "100vw" >',
            
            # Test Case 5: img tag with no alt attribute
            '<img src="image.jpg" srcset="image.jpg 1x, image@2x.jpg 2x">',
            
            # Test Case 6: Not an img tag (should return empty)
            '<div class="container">Not an image</div>',
            
            # Test Case 7: Malformed img tag
            '<img src="broken" alt="Broken" srcset="broken" sizes="broken">',
            
            # Test Case 8: img tag with special characters
            '<img src="image.jpg" alt="Special chars: &quot;quotes&quot; &amp; &lt;tags&gt;" srcset="image.jpg 1x">'
        ]
        
        print("Enhanced Image Attribute Extraction Testing")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input: {test_case}")
            
            # Test with comprehensive patterns
            for attr, pattern_list in self.patterns.items():
                for j, pattern in enumerate(pattern_list):
                    match = re.search(pattern, test_case, re.IGNORECASE)
                    if match:
                        print(f"  {attr} (pattern {j+1}): {match.group(1)}")
                    else:
                        print(f"  {attr} (pattern {j+1}): Not found")
            
            # Test with enhanced extraction method
            print(f"\n  Enhanced Extraction Results:")
            extracted = self.extract_img_from_element(test_case)
            for element_type, attr_name, attr_value in extracted:
                print(f"    {attr_name}: {attr_value}")
            
            # Test validation
            validation = self.validate_img_extraction(test_case)
            print(f"  Validation: is_img={validation['is_img_tag']}, "
                  f"has_src={validation['has_required_src']}, "
                  f"attr_count={validation['attribute_count']}")
    
    def performance_test(self, iterations: int = 1000) -> Dict:
        """
        Performance testing with large HTML content.
        
        Args:
            iterations (int): Number of iterations for performance test
            
        Returns:
            Dict: Performance metrics
        """
        import time
        
        # Create a large test case
        large_html = '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" 
                        alt="Літературний вечір" 
                        srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                                https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
                                https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
                                https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
                                https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
                        sizes="(max-width: 768px) 100vw, 400px">''' * 100
        
        start_time = time.time()
        
        for _ in range(iterations):
            self.extract_img_from_element(large_html)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        return {
            'iterations': iterations,
            'total_time': total_time,
            'avg_time_per_iteration': avg_time,
            'iterations_per_second': iterations / total_time
        }
    
    def edge_case_test(self) -> None:
        """Test edge cases and error conditions."""
        print("\n" + "=" * 60)
        print("EDGE CASE TESTING")
        print("=" * 60)
        
        edge_cases = [
            # Empty string
            "",
            # Whitespace only
            "   \n\t  ",
            # Malformed HTML
            "<img src= alt=>",
            # Nested quotes
            '<img src="image.jpg" alt="Quote: \'nested\' here">',
            # Very long attributes
            f'<img src="{"x" * 1000}" alt="{"y" * 1000}">',
            # Unicode characters
            '<img src="image.jpg" alt="Unicode: 中文 Español Français">',
            # Multiple img tags (should extract from first)
            '<img src="first.jpg"><img src="second.jpg">',
            # Self-closing tag
            '<img src="image.jpg" />',
            # Mixed case
            '<IMG SRC="image.jpg" ALT="Mixed case">'
        ]
        
        for i, test_case in enumerate(edge_cases, 1):
            print(f"\n--- Edge Case {i} ---")
            print(f"Input: {repr(test_case)}")
            
            try:
                extracted = self.extract_img_from_element(test_case)
                validation = self.validate_img_extraction(test_case)
                
                print(f"  Extracted: {extracted}")
                print(f"  Is img tag: {validation['is_img_tag']}")
                print(f"  Has src: {validation['has_required_src']}")
                
            except Exception as e:
                print(f"  Error: {e}")


def main():
    """Main function to run all tests."""
    extractor = ImageAttributeExtractor()
    
    # Run comprehensive regex pattern testing
    extractor.test_regex_patterns()
    
    # Run edge case testing
    extractor.edge_case_test()
    
    # Run performance testing
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTING")
    print("=" * 60)
    
    performance_results = extractor.performance_test(iterations=1000)
    print(f"Performance Results:")
    print(f"  Iterations: {performance_results['iterations']}")
    print(f"  Total Time: {performance_results['total_time']:.4f} seconds")
    print(f"  Average Time per Iteration: {performance_results['avg_time_per_iteration']:.6f} seconds")
    print(f"  Iterations per Second: {performance_results['iterations_per_second']:.2f}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main() 