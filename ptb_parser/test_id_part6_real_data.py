#!/usr/bin/env python3
"""
id_part6 Testing: Real Database Data with srcset and sizes
Comprehensive testing using actual content_tech_html and content_items_tech_html data
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

class RealDataTester:
    """Comprehensive testing framework for real database data with srcset and sizes."""
    
    def __init__(self, db_path: str = "sqllite/tech_html_parser.db"):
        self.db_path = db_path
        self.content_extractor = ContentExtractor()
        
    def test_real_srcset_sizes_data(self):
        """Test develop_template_body function with real database data containing srcset and sizes."""
        
        print("🧪 Testing Real Database Data with srcset and sizes (id_part6)")
        print("=" * 80)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get content_tech_html records with srcset and sizes
                cursor.execute("""
                    SELECT content_id, content_body, type_content
                    FROM content_tech_html 
                    WHERE content_body LIKE '%srcset%' OR content_body LIKE '%sizes%'
                    ORDER BY content_id
                    LIMIT 10
                """)
                
                content_records = cursor.fetchall()
                
                if not content_records:
                    print("❌ No content_tech_html records with srcset/sizes found")
                    return False
                
                print(f"📊 Found {len(content_records)} content records with srcset/sizes")
                
                test_results = []
                
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
                    
                    print(f"\n--- Real Data Test: Content ID {content_id} ---")
                    print(f"Type: {type_content}")
                    print(f"Content Body Preview: {content_body[:150]}{'...' if len(content_body) > 150 else ''}")
                    print(f"Content Items: {len(content_items_records)} items")
                    
                    # Analyze the content items
                    srcset_count = sum(1 for record in content_items_records if record[4] == 'srcset')
                    sizes_count = sum(1 for record in content_items_records if record[4] == 'sizes')
                    src_count = sum(1 for record in content_items_records if record[4] == 'src')
                    alt_count = sum(1 for record in content_items_records if record[4] == 'alt')
                    
                    print(f"  📊 Attributes: src={src_count}, alt={alt_count}, srcset={srcset_count}, sizes={sizes_count}")
                    
                    try:
                        # Call the function
                        template_body = self.content_extractor.develop_template_body(
                            content_body, 
                            content_items_records
                        )
                        
                        print(f"Template Body Preview: {template_body[:150]}{'...' if len(template_body) > 150 else ''}")
                        
                        # Validate UUID replacements
                        uuid_count = template_body.count('uuid_')
                        expected_uuid_count = len(content_items_records)
                        
                        # For srcset, we expect more replacements because multiple URLs are replaced
                        # Count unique UUIDs used
                        import re
                        unique_uuids = set(re.findall(r'uuid_([a-f0-9]+)', template_body))
                        unique_uuid_count = len(unique_uuids)
                        
                        # Check for specific attribute replacements
                        srcset_replaced = 'uuid_' in template_body and 'srcset' in template_body
                        sizes_replaced = 'uuid_' in template_body and 'sizes' in template_body
                        
                        print(f"  ✅ UUID replacements: {uuid_count} total, {unique_uuid_count} unique")
                        print(f"  ✅ srcset replaced: {srcset_replaced}")
                        print(f"  ✅ sizes replaced: {sizes_replaced}")
                        
                        # Store test result
                        test_results.append({
                            'content_id': content_id,
                            'type_content': type_content,
                            'items_count': len(content_items_records),
                            'uuid_replacements': uuid_count,
                            'unique_uuids': unique_uuid_count,
                            'expected_replacements': expected_uuid_count,
                            'srcset_replaced': srcset_replaced,
                            'sizes_replaced': sizes_replaced,
                            'success': uuid_count > 0 and unique_uuid_count >= expected_uuid_count
                        })
                        
                    except Exception as e:
                        print(f"❌ Error processing content ID {content_id}: {e}")
                        test_results.append({
                            'content_id': content_id,
                            'type_content': type_content,
                            'items_count': len(content_items_records),
                            'uuid_replacements': 0,
                            'expected_replacements': len(content_items_records),
                            'srcset_replaced': False,
                            'sizes_replaced': False,
                            'success': False,
                            'error': str(e)
                        })
                
                # Summary
                print(f"\n" + "=" * 80)
                print("📊 REAL DATA TEST RESULTS SUMMARY")
                print("=" * 80)
                
                successful_tests = sum(1 for result in test_results if result['success'])
                total_tests = len(test_results)
                
                print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
                print(f"📊 Total UUID Replacements: {sum(r['uuid_replacements'] for r in test_results)}")
                print(f"📊 Total Expected Replacements: {sum(r['expected_replacements'] for r in test_results)}")
                
                # Detailed results
                for result in test_results:
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    print(f"  {status} Content ID {result['content_id']}: {result['uuid_replacements']}/{result['expected_replacements']} replacements")
                    if result.get('error'):
                        print(f"    Error: {result['error']}")
                
                return successful_tests == total_tests
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def test_specific_srcset_sizes_cases(self):
        """Test specific complex srcset and sizes cases from the database."""
        
        print("\n🔍 Testing Specific srcset/sizes Cases")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Test specific content_ids with complex srcset/sizes
                test_cases = [
                    {
                        'content_id': 38,
                        'description': 'Complex srcset with 4 URLs and sizes'
                    },
                    {
                        'content_id': 57,
                        'description': 'LinkedIn seminar with 5 URLs in srcset'
                    },
                    {
                        'content_id': 62,
                        'description': 'Stockholm Tech Show with complex srcset'
                    },
                    {
                        'content_id': 67,
                        'description': 'Literary evening with multiple srcset URLs'
                    }
                ]
                
                passed_tests = 0
                total_tests = len(test_cases)
                
                for test_case in test_cases:
                    content_id = test_case['content_id']
                    description = test_case['description']
                    
                    print(f"\n--- Test Case: {description} (Content ID {content_id}) ---")
                    
                    # Get content body
                    cursor.execute("""
                        SELECT content_body, type_content
                        FROM content_tech_html 
                        WHERE content_id = ?
                    """, (content_id,))
                    
                    content_result = cursor.fetchone()
                    if not content_result:
                        print(f"❌ Content ID {content_id} not found")
                        continue
                    
                    content_body, type_content = content_result
                    
                    # Get content items
                    cursor.execute("""
                        SELECT item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at
                        FROM content_items_tech_html 
                        WHERE content_id = ?
                        ORDER BY item_id
                    """, (content_id,))
                    
                    content_items_records = cursor.fetchall()
                    
                    if not content_items_records:
                        print(f"❌ No content items for Content ID {content_id}")
                        continue
                    
                    print(f"Content Body: {content_body[:100]}{'...' if len(content_body) > 100 else ''}")
                    print(f"Content Items: {len(content_items_records)} items")
                    
                    # Show the content items
                    for record in content_items_records:
                        item_id, _, uuid_item, type_element, type_item, item_body, _, _ = record
                        print(f"  Item {item_id}: {type_element}.{type_item} = '{item_body[:50]}{'...' if len(item_body) > 50 else ''}' -> uuid_{uuid_item}")
                    
                    try:
                        # Call the function
                        template_body = self.content_extractor.develop_template_body(
                            content_body, 
                            content_items_records
                        )
                        
                        print(f"Template Body: {template_body[:200]}{'...' if len(template_body) > 200 else ''}")
                        
                        # Validate specific replacements
                        uuid_count = template_body.count('uuid_')
                        expected_count = len(content_items_records)
                        
                        # Count unique UUIDs used
                        import re
                        unique_uuids = set(re.findall(r'uuid_([a-f0-9]+)', template_body))
                        unique_uuid_count = len(unique_uuids)
                        
                        if unique_uuid_count >= expected_count:
                            print(f"✅ Test passed: {uuid_count} total, {unique_uuid_count} unique UUIDs")
                            passed_tests += 1
                        else:
                            print(f"❌ Test failed: {uuid_count} total, {unique_uuid_count} unique UUIDs")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                print(f"\n📊 Specific Test Results: {passed_tests}/{total_tests} passed")
                return passed_tests == total_tests
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def test_performance_with_real_data(self):
        """Test performance with real database data."""
        
        print("\n⚡ Performance Testing with Real Data")
        print("=" * 60)
        
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all content with srcset/sizes
                cursor.execute("""
                    SELECT cth.content_id, cth.content_body, cth.type_content,
                           COUNT(cith.item_id) as item_count
                    FROM content_tech_html cth
                    LEFT JOIN content_items_tech_html cith ON cth.content_id = cith.content_id
                    WHERE cth.content_body LIKE '%srcset%' OR cth.content_body LIKE '%sizes%'
                    GROUP BY cth.content_id
                    ORDER BY item_count DESC
                    LIMIT 20
                """)
                
                performance_records = cursor.fetchall()
                
                if not performance_records:
                    print("❌ No performance test data found")
                    return False
                
                print(f"📊 Testing performance with {len(performance_records)} records")
                
                total_items = 0
                total_replacements = 0
                start_time = time.time()
                
                for record in performance_records:
                    content_id, content_body, type_content, item_count = record
                    
                    # Get content items
                    cursor.execute("""
                        SELECT item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at
                        FROM content_items_tech_html 
                        WHERE content_id = ?
                        ORDER BY item_id
                    """, (content_id,))
                    
                    content_items_records = cursor.fetchall()
                    
                    if content_items_records:
                        try:
                            template_body = self.content_extractor.develop_template_body(
                                content_body, 
                                content_items_records
                            )
                            
                            uuid_count = template_body.count('uuid_')
                            total_items += len(content_items_records)
                            total_replacements += uuid_count
                            
                        except Exception as e:
                            print(f"⚠️  Error processing content ID {content_id}: {e}")
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"✅ Performance test completed")
                print(f"   Processing time: {processing_time:.4f} seconds")
                print(f"   Total items processed: {total_items}")
                print(f"   Total UUID replacements: {total_replacements}")
                print(f"   Replacements per second: {total_replacements/processing_time:.2f}")
                print(f"   Records per second: {len(performance_records)/processing_time:.2f}")
                
                return processing_time < 5.0  # Should complete within 5 seconds
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all id_part6 tests."""
        
        print("🧪 Complete id_part6 Testing: Real Database Data with srcset and sizes")
        print("=" * 80)
        
        # Test 1: Real srcset/sizes data testing
        real_data_passed = self.test_real_srcset_sizes_data()
        
        # Test 2: Specific srcset/sizes cases
        specific_cases_passed = self.test_specific_srcset_sizes_cases()
        
        # Test 3: Performance testing with real data
        performance_passed = self.test_performance_with_real_data()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ID_PART6 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"✅ Real Data Tests: {'PASSED' if real_data_passed else 'FAILED'}")
        print(f"✅ Specific Cases: {'PASSED' if specific_cases_passed else 'FAILED'}")
        print(f"✅ Performance Tests: {'PASSED' if performance_passed else 'FAILED'}")
        
        overall_passed = real_data_passed and specific_cases_passed and performance_passed
        print(f"\n🎯 Overall Result: {'ALL TESTS PASSED' if overall_passed else 'SOME TESTS FAILED'}")
        
        return overall_passed


def main():
    """Main function to run id_part6 tests."""
    tester = RealDataTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ id_part6 testing completed successfully!")
    else:
        print("\n❌ id_part6 testing failed!")
    
    return success


if __name__ == "__main__":
    main() 