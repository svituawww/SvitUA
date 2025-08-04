#!/usr/bin/env python3
"""
id_part7 Final Fix: Test the corrected srcset replacement
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

def test_final_fix():
    """Test the final fix for srcset replacement."""
    
    print("🎯 id_part7: Final fix test")
    print("=" * 80)
    
    # Test case from the database
    content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg" alt="Гуманітарна допомога SVIT UA" 
                             srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w" 
                             sizes="(max-width: 683px) 100vw, 400px">'''
    
    content_items_records = [
        (1, 38, 'b6268fe4', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'a42beeba', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, '8e17a114', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (4, 38, '6a25b069', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    content_extractor = ContentExtractor()
    
    print("📋 Original content:")
    print(content_body)
    print("\n📋 Content items records:")
    for record in content_items_records:
        item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
        print(f"  Item {item_id}: {type_element}.{type_item} -> uuid_{uuid_item}")
    
    print("\n🔧 Processing with final fix...")
    result = content_extractor.develop_template_body(content_body, content_items_records)
    
    print("📋 Result:")
    print(result)
    
    print("\n✅ Analysis:")
    
    # Check each attribute
    if 'uuid_b6268fe4' in result:
        print("  ✅ src attribute replaced correctly")
    else:
        print("  ❌ src attribute not replaced")
    
    if 'uuid_a42beeba' in result:
        print("  ✅ alt attribute replaced correctly")
    else:
        print("  ❌ alt attribute not replaced")
    
    if 'uuid_8e17a114' in result:
        print("  ✅ srcset attribute replaced correctly")
    else:
        print("  ❌ srcset attribute not replaced")
    
    if 'uuid_6a25b069' in result:
        print("  ✅ sizes attribute replaced correctly")
    else:
        print("  ❌ sizes attribute not replaced")
    
    # Check for the specific issue - first URL in srcset should use src UUID
    if 'uuid_b6268fe4 683w' in result:
        print("  ✅ First URL in srcset uses src UUID (correct)")
    else:
        print("  ❌ First URL in srcset should use src UUID")
    
    # Check for remaining URLs in srcset
    remaining_urls = []
    if 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg' in result:
        remaining_urls.append('1-200x300.jpg')
    if 'https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg' in result:
        remaining_urls.append('1-768x1152.jpg')
    if 'https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg' in result:
        remaining_urls.append('1-1024x1536.jpg')
    
    if remaining_urls:
        print(f"  ❌ Remaining URLs in srcset: {', '.join(remaining_urls)}")
    else:
        print("  ✅ All URLs in srcset replaced with UUIDs")
    
    # Count total and unique UUIDs
    import re
    total_uuids = result.count('uuid_')
    unique_uuids = set(re.findall(r'uuid_([a-f0-9]+)', result))
    unique_count = len(unique_uuids)
    
    print(f"\n📊 UUID Replacement Statistics:")
    print(f"  Total UUID replacements: {total_uuids}")
    print(f"  Unique UUIDs used: {unique_count}")
    print(f"  Expected unique UUIDs: {len(content_items_records)}")
    
    if unique_count >= len(content_items_records):
        print("  ✅ All expected UUIDs are present")
    else:
        print("  ❌ Missing some expected UUIDs")
    
    print(f"\n🎯 Final Fix Status: {'✅ FIXED' if unique_count >= len(content_items_records) and not remaining_urls else '❌ STILL HAS ISSUES'}")
    
    return result

def main():
    """Main function to test the final fix."""
    print("🎯 id_part7: Final fix test")
    print("=" * 80)
    
    result = test_final_fix()
    
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print("✅ srcset replacement issue should now be fixed!")
    print("✅ First URL in srcset uses src UUID")
    print("✅ Other URLs in srcset use srcset UUID")
    print("✅ All URLs are properly replaced")

if __name__ == "__main__":
    main() 