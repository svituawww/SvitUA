#!/usr/bin/env python3
"""
id_part7 Testing: Fix srcset replacement issue
Demonstrates the problem with srcset replacement and tests the fix
"""

import sys
import os
from pathlib import Path
from typing import List

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

def test_srcset_replacement_issue():
    """Test the current srcset replacement issue."""
    
    print("🔍 Testing srcset replacement issue (id_part7)")
    print("=" * 60)
    
    # Test case from the database
    content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg" alt="Гуманітарна допомога SVIT UA" 
                             srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w" 
                             sizes="(max-width: 683px) 100vw, 400px">'''
    
    content_items_records = [
        (1, 38, '026cae67', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'b70f83ff', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, '516d7fdb', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (4, 38, '26311762', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    content_extractor = ContentExtractor()
    
    print("📋 Original content:")
    print(content_body)
    print("\n📋 Content items records:")
    for record in content_items_records:
        item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
        print(f"  Item {item_id}: {type_element}.{type_item} = '{item_body[:50]}{'...' if len(item_body) > 50 else ''}' -> uuid_{uuid_item}")
    
    # Test current implementation
    print("\n🔍 Testing current implementation...")
    result = content_extractor.develop_template_body(content_body, content_items_records)
    
    print("📋 Current result:")
    print(result)
    
    # Check what's wrong
    print("\n❌ Issues found:")
    if 'uuid_026cae67' in result:
        print("  ✅ src replaced correctly")
    else:
        print("  ❌ src not replaced")
    
    if 'uuid_b70f83ff' in result:
        print("  ✅ alt replaced correctly")
    else:
        print("  ❌ alt not replaced")
    
    if 'uuid_516d7fdb' in result:
        print("  ✅ srcset replaced correctly")
    else:
        print("  ❌ srcset not replaced")
    
    if 'uuid_26311762' in result:
        print("  ✅ sizes replaced correctly")
    else:
        print("  ❌ sizes not replaced")
    
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
        print("  ✅ All URLs in srcset replaced")
    
    return result

def test_enhanced_srcset_replacement():
    """Test enhanced srcset replacement that handles multiple URLs."""
    
    print("\n🔧 Testing enhanced srcset replacement...")
    print("=" * 60)
    
    # Enhanced implementation
    def develop_template_body_enhanced(content_body: str, content_items_records: List[tuple]) -> str:
        """
        Enhanced template body development with proper srcset handling.
        """
        import re
        result = content_body
        
        # Sort records by item_id to ensure consistent replacement order
        sorted_records = sorted(content_items_records, key=lambda x: x[0])
        
        for record in sorted_records:
            # Unpack the full database record
            item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
            
            if type_item == 'srcset':
                # Special handling for srcset - replace all URLs in the srcset
                srcset_pattern = rf'srcset\s*=\s*["\']([^"\']+)["\']'
                match = re.search(srcset_pattern, result, re.IGNORECASE)
                if match:
                    srcset_value = match.group(1)
                    # Split srcset into individual URLs
                    urls = [url.strip() for url in srcset_value.split(',')]
                    new_urls = []
                    
                    for url in urls:
                        # Extract the URL part (before the descriptor like '683w')
                        url_parts = url.strip().split()
                        if url_parts:
                            original_url = url_parts[0]
                            descriptor = ' '.join(url_parts[1:]) if len(url_parts) > 1 else ''
                            
                            # Check if this URL matches our item_body
                            if original_url in item_body:
                                # Replace with UUID
                                new_url = f'uuid_{uuid_item}'
                                if descriptor:
                                    new_url += f' {descriptor}'
                                new_urls.append(new_url)
                            else:
                                # Keep original URL
                                new_urls.append(url)
                    
                    # Replace the entire srcset value
                    new_srcset_value = ', '.join(new_urls)
                    result = re.sub(srcset_pattern, f'srcset="{new_srcset_value}"', result, flags=re.IGNORECASE)
            else:
                # Standard replacement for other attributes
                if item_body in result:
                    result = result.replace(item_body, f'uuid_{uuid_item}')
        
        return result
    
    # Test case
    content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg" alt="Гуманітарна допомога SVIT UA" 
                             srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w" 
                             sizes="(max-width: 683px) 100vw, 400px">'''
    
    content_items_records = [
        (1, 38, '026cae67', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'b70f83ff', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, '516d7fdb', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (4, 38, '26311762', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    print("📋 Testing enhanced implementation...")
    result = develop_template_body_enhanced(content_body, content_items_records)
    
    print("📋 Enhanced result:")
    print(result)
    
    # Check results
    print("\n✅ Enhanced implementation check:")
    if 'uuid_026cae67' in result:
        print("  ✅ src replaced correctly")
    else:
        print("  ❌ src not replaced")
    
    if 'uuid_b70f83ff' in result:
        print("  ✅ alt replaced correctly")
    else:
        print("  ❌ alt not replaced")
    
    if 'uuid_516d7fdb' in result:
        print("  ✅ srcset replaced correctly")
    else:
        print("  ❌ srcset not replaced")
    
    if 'uuid_26311762' in result:
        print("  ✅ sizes replaced correctly")
    else:
        print("  ❌ sizes not replaced")
    
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
        print("  ✅ All URLs in srcset replaced")
    
    return result

def main():
    """Main function to test srcset replacement fix."""
    print("🧪 id_part7: Fix srcset replacement issue")
    print("=" * 80)
    
    # Test current implementation
    current_result = test_srcset_replacement_issue()
    
    # Test enhanced implementation
    enhanced_result = test_enhanced_srcset_replacement()
    
    print("\n" + "=" * 80)
    print("📊 COMPARISON RESULTS")
    print("=" * 80)
    
    # Compare results
    current_srcset_replaced = 'uuid_516d7fdb' in current_result
    enhanced_srcset_replaced = 'uuid_516d7fdb' in enhanced_result
    
    current_remaining_urls = 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg' in current_result
    enhanced_remaining_urls = 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg' in enhanced_result
    
    print(f"Current Implementation:")
    print(f"  srcset replaced: {'✅' if current_srcset_replaced else '❌'}")
    print(f"  remaining URLs: {'❌' if current_remaining_urls else '✅'}")
    
    print(f"\nEnhanced Implementation:")
    print(f"  srcset replaced: {'✅' if enhanced_srcset_replaced else '❌'}")
    print(f"  remaining URLs: {'❌' if enhanced_remaining_urls else '✅'}")
    
    if enhanced_srcset_replaced and not enhanced_remaining_urls:
        print("\n🎯 Enhanced implementation fixes the srcset replacement issue!")
    else:
        print("\n❌ Enhanced implementation still has issues")

if __name__ == "__main__":
    main() 