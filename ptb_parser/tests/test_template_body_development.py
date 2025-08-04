#!/usr/bin/env python3
"""
Enhanced Template Body Development Testing
Comprehensive test script for develop_template_body function
Implementation of id_part5 from inst_4.md
"""

import sys
import os
import sqlite3
import time
from typing import List, Tuple, Dict, Any
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

class TemplateBodyTester:
    """Comprehensive testing framework for develop_template_body function."""
    
    def __init__(self, db_path: str = "sqllite/tech_html_parser.db"):
        self.db_path = db_path
        self.content_extractor = ContentExtractor()
        
    def test_develop_template_body_standalone(self):
        """Test develop_template_body function with predefined test cases."""
        
        print("🧪 Testing develop_template_body Function (Standalone)")
        print("=" * 60)
        
        test_cases = [
            # Test Case 1: Simple img tag with src and alt
            {
                'name': 'Simple img tag with src and alt',
                'content_body': '<img src="https://example.com/image.jpg" alt="Logo">',
                'content_items_records': [
                    (1, 1, 'bdad656e', 'img', 'src', 'https://example.com/image.jpg', '2025-01-01', '2025-01-01'),
                    (2, 1, '7e92fb3f', 'img', 'alt', 'Logo', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_bdad656e', 'uuid_7e92fb3f']
            },
            
            # Test Case 2: Complex img tag with all attributes
            {
                'name': 'Complex img tag with all attributes',
                'content_body': '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" 
                                    alt="Літературний вечір" 
                                    srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                                            https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w" 
                                    sizes="(max-width: 768px) 100vw, 400px">''',
                'content_items_records': [
                    (1, 1, 'e67ed269', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png', '2025-01-01', '2025-01-01'),
                    (2, 1, '16c025db', 'img', 'alt', 'Літературний вечір', '2025-01-01', '2025-01-01'),
                    (3, 1, 'ece52aa9', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, \n                                            https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w', '2025-01-01', '2025-01-01'),
                    (4, 1, '14d97141', 'img', 'sizes', '(max-width: 768px) 100vw, 400px', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_e67ed269', 'uuid_16c025db', 'uuid_14d97141']
            },
            
            # Test Case 3: Link tag with href and title
            {
                'name': 'Link tag with href and title',
                'content_body': '<a href="#contact" title="Contact Us">Contact</a>',
                'content_items_records': [
                    (1, 1, 'a8f3c2d1', 'a', 'href', '#contact', '2025-01-01', '2025-01-01'),
                    (2, 1, 'b9e4d3c2', 'a', 'title', 'Contact Us', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_a8f3c2d1', 'uuid_b9e4d3c2']
            },
            
            # Test Case 4: Mixed content with multiple elements
            {
                'name': 'Mixed content with multiple elements',
                'content_body': '<div><img src="logo.png" alt="Logo"><a href="#home">Home</a></div>',
                'content_items_records': [
                    (1, 1, 'c7f5e4d3', 'img', 'src', 'logo.png', '2025-01-01', '2025-01-01'),
                    (2, 1, 'd8g6f5e4', 'img', 'alt', 'Logo', '2025-01-01', '2025-01-01'),
                    (3, 1, 'e9h7g6f5', 'a', 'href', '#home', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_c7f5e4d3', 'uuid_d8g6f5e4', 'uuid_e9h7g6f5']
            },
            
            # Test Case 5: Edge cases - special characters and encoding
            {
                'name': 'Special characters and encoding',
                'content_body': '<img src="image.jpg" alt="Special: &quot;quotes&quot; &amp; symbols">',
                'content_items_records': [
                    (1, 1, 'f0i8h7g6', 'img', 'src', 'image.jpg', '2025-01-01', '2025-01-01'),
                    (2, 1, 'g1j9i8h7', 'img', 'alt', 'Special: &quot;quotes&quot; &amp; symbols', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_f0i8h7g6', 'uuid_g1j9i8h7']
            },
            
            # Test Case 6: Empty or missing attributes
            {
                'name': 'Empty or missing attributes',
                'content_body': '<img src="image.jpg">',
                'content_items_records': [
                    (1, 1, 'h2k0j9i8', 'img', 'src', 'image.jpg', '2025-01-01', '2025-01-01')
                ],
                'expected_contains': ['uuid_h2k0j9i8']
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            print(f"Input content_body: {test_case['content_body']}")
            print(f"Input content_items_records: {len(test_case['content_items_records'])} records")
            
            try:
                # Call the function
                result = self.content_extractor.develop_template_body(
                    test_case['content_body'], 
                    test_case['content_items_records']
                )
                
                print(f"Result: {result}")
                
                # Validate result
                validation_passed = True
                for expected in test_case['expected_contains']:
                    if expected not in result:
                        print(f"❌ Expected '{expected}' not found in result")
                        validation_passed = False
                
                if validation_passed:
                    print(f"✅ Test passed")
                    passed_tests += 1
                else:
                    print(f"❌ Test failed")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 Standalone Test Results: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_develop_template_body_with_database(self):
        """Test develop_template_body function with real database content."""
        
        print("\n🗄️ Testing develop_template_body Function (Database Integration)")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get content_tech_html records
                cursor.execute("""
                    SELECT content_id, content_body, type_content
                    FROM content_tech_html 
                    LIMIT 5
                """)
                
                content_records = cursor.fetchall()
                
                if not content_records:
                    print("❌ No content_tech_html records found in database")
                    return False
                
                print(f"📊 Found {len(content_records)} content records to test")
                
                processed_count = 0
                successful_count = 0
                
                for content_record in content_records:
                    content_id, content_body, type_content = content_record
                    
                    # Get content_items for this content_id
                    cursor.execute("""
                        SELECT item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at
                        FROM content_items_tech_html 
                        WHERE content_id = ?
                        ORDER BY item_id
                    """, (content_id,))
                    
                    content_items_records = cursor.fetchall()
                    
                    if not content_items_records:
                        print(f"⚠️  Content ID {content_id}: No content items found")
                        continue
                
                    print(f"\n--- Database Test: Content ID {content_id} ---")
                    print(f"Type: {type_content}")
                    print(f"Content Body: {content_body[:100]}{'...' if len(content_body) > 100 else ''}")
                    print(f"Content Items: {len(content_items_records)} items")
                    
                    try:
                        # Call the function
                        template_body = self.content_extractor.develop_template_body(
                            content_body, 
                            content_items_records
                        )
                        
                        print(f"Template Body: {template_body[:100]}{'...' if len(template_body) > 100 else ''}")
                        
                        # Validate that UUID replacements were made
                        uuid_count = template_body.count('uuid_')
                        if uuid_count > 0:
                            print(f"✅ Success: {uuid_count} UUID replacements made")
                            successful_count += 1
                        else:
                            print(f"⚠️  No UUID replacements found")
                        
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"❌ Error processing content ID {content_id}: {e}")
                
                print(f"\n📊 Database Test Results: {successful_count}/{processed_count} successful")
                return successful_count > 0
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def test_performance_with_large_content(self):
        """Test performance with large content and many attributes."""
        
        print("\n⚡ Testing Performance with Large Content")
        print("=" * 60)
        
        # Create large test content
        large_content = '''<div class="container">
            <img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" 
                 alt="Літературний вечір" 
                 srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                         https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w" 
                 sizes="(max-width: 768px) 100vw, 400px">
            <a href="#contact" title="Contact Us">Contact</a>
            <img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.png" 
                 alt="Гуманітарна допомога SVIT UA" 
                 srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.png 683w" 
                 sizes="(max-width: 683px) 100vw, 400px">
        </div>''' * 100  # Repeat 100 times
        
        large_content_items = [
            (1, 1, 'perf_img_src_001', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png', '2025-01-01', '2025-01-01'),
            (2, 1, 'perf_img_alt_002', 'img', 'alt', 'Літературний вечір', '2025-01-01', '2025-01-01'),
            (3, 1, 'perf_img_srcset_003', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w', '2025-01-01', '2025-01-01'),
            (4, 1, 'perf_img_sizes_004', 'img', 'sizes', '(max-width: 768px) 100vw, 400px', '2025-01-01', '2025-01-01'),
            (5, 1, 'perf_link_href_005', 'a', 'href', '#contact', '2025-01-01', '2025-01-01'),
            (6, 1, 'perf_link_title_006', 'a', 'title', 'Contact Us', '2025-01-01', '2025-01-01'),
            (7, 1, 'perf_img_src2_007', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.png', '2025-01-01', '2025-01-01'),
            (8, 1, 'perf_img_alt2_008', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
            (9, 1, 'perf_img_srcset2_009', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.png 683w', '2025-01-01', '2025-01-01'),
            (10, 1, 'perf_img_sizes2_010', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
        ] * 100  # Repeat 100 times
        
        print(f"📏 Large content size: {len(large_content):,} characters")
        print(f"📦 Content items count: {len(large_content_items):,} items")
        
        start_time = time.time()
        
        try:
            result = self.content_extractor.develop_template_body(large_content, large_content_items)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            uuid_count = result.count('uuid_')
            
            print(f"✅ Performance test completed")
            print(f"   Processing time: {processing_time:.4f} seconds")
            print(f"   UUID replacements: {uuid_count:,}")
            print(f"   Replacements per second: {uuid_count/processing_time:.2f}")
            
            return processing_time < 10.0  # Should complete within 10 seconds
            
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all template body development tests."""
        
        print("🧪 Complete Template Body Development Testing")
        print("=" * 80)
        
        # Test 1: Standalone testing
        standalone_passed = self.test_develop_template_body_standalone()
        
        # Test 2: Database integration testing
        database_passed = self.test_develop_template_body_with_database()
        
        # Test 3: Performance testing
        performance_passed = self.test_performance_with_large_content()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"✅ Standalone Tests: {'PASSED' if standalone_passed else 'FAILED'}")
        print(f"✅ Database Integration: {'PASSED' if database_passed else 'FAILED'}")
        print(f"✅ Performance Tests: {'PASSED' if performance_passed else 'FAILED'}")
        
        overall_passed = standalone_passed and database_passed and performance_passed
        print(f"\n🎯 Overall Result: {'ALL TESTS PASSED' if overall_passed else 'SOME TESTS FAILED'}")
        
        return overall_passed


def main():
    """Main function to run template body development tests."""
    tester = TemplateBodyTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Template body development testing completed successfully!")
    else:
        print("\n❌ Template body development testing failed!")
    
    return success


if __name__ == "__main__":
    main() 