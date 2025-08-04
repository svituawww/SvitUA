#!/usr/bin/env python3
"""
id_part7 Implementation Test: Replace entire srcset with one UUID
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

def test_id_part7_implementation():
    """Test the id_part7 implementation according to specifications."""
    
    print("🎯 id_part7: Implementation Test")
    print("=" * 80)
    
    # Test case from id_part7 specifications
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
    
    print("📋 Input (from id_part7 specifications):")
    print(content_body)
    print("\n📋 Expected Output (from id_part7 specifications):")
    print('<img src="uuid_b6268fe4" alt="uuid_a42beeba" \n     srcset="uuid_8e17a114" \n     sizes="uuid_6a25b069">')
    
    print("\n🔧 Processing with id_part7 implementation...")
    result = content_extractor.develop_template_body(content_body, content_items_records)
    
    print("\n📋 Actual Result:")
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
    
    # Check for the key requirement - entire srcset replaced with one UUID
    if 'srcset="uuid_8e17a114"' in result:
        print("  ✅ Entire srcset replaced with one UUID (correct)")
    else:
        print("  ❌ srcset should be replaced with one UUID")
    
    # Check for remaining URLs in srcset
    remaining_urls = []
    if 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg' in result:
        remaining_urls.append('1-683x1024.jpg')
    if 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg' in result:
        remaining_urls.append('1-200x300.jpg')
    if 'https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg' in result:
        remaining_urls.append('1-768x1152.jpg')
    if 'https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg' in result:
        remaining_urls.append('1-1024x1536.jpg')
    
    if remaining_urls:
        print(f"  ❌ Remaining URLs in srcset: {', '.join(remaining_urls)}")
    else:
        print("  ✅ All URLs in srcset replaced with single UUID")
    
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
    
    status = '✅ CORRECT' if 'srcset="uuid_8e17a114"' in result and not remaining_urls else '❌ INCORRECT'
    print(f"\n🎯 id_part7 Implementation Status: {status}")
    
    return result

def main():
    """Main function to test id_part7 implementation."""
    print("🎯 id_part7: Implementation Test")
    print("=" * 80)
    
    result = test_id_part7_implementation()
    
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print("✅ id_part7 implementation should replace entire srcset with one UUID")
    print("✅ No individual URL processing in srcset")
    print("✅ Simple attribute replacement for srcset")

if __name__ == "__main__":
    main() 