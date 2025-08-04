#!/usr/bin/env python3
"""
id_part7 Correct Approach: Each srcset URL should be a separate database record
Demonstrates the proper way to handle srcset URLs for UUID replacement
"""

import sys
import os
from pathlib import Path
from typing import List

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from extract_content_items import ContentExtractor

def demonstrate_correct_srcset_approach():
    """Demonstrate the correct approach for srcset handling."""
    
    print("🎯 id_part7: Correct srcset approach demonstration")
    print("=" * 80)
    
    # Original HTML
    content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg" alt="Гуманітарна допомога SVIT UA" 
                             srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w" 
                             sizes="(max-width: 683px) 100vw, 400px">'''
    
    print("📋 Original HTML:")
    print(content_body)
    
    # CORRECT APPROACH: Each URL in srcset should be a separate database record
    print("\n📋 CORRECT Database Records (each URL separate):")
    correct_records = [
        (1, 38, 'uuid_src_1', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'uuid_alt_1', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, 'uuid_srcset_1', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w', '2025-01-01', '2025-01-01'),
        (4, 38, 'uuid_srcset_2', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w', '2025-01-01', '2025-01-01'),
        (5, 38, 'uuid_srcset_3', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w', '2025-01-01', '2025-01-01'),
        (6, 38, 'uuid_srcset_4', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (7, 38, 'uuid_sizes_1', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    for record in correct_records:
        item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
        print(f"  Item {item_id}: {type_element}.{type_item} -> {uuid_item}")
        print(f"      Body: {item_body}")
    
    # WRONG APPROACH: Entire srcset as one record (current implementation)
    print("\n📋 WRONG Database Records (entire srcset as one):")
    wrong_records = [
        (1, 38, 'uuid_src_1', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'uuid_alt_1', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, 'uuid_srcset_1', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, \n                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (4, 38, 'uuid_sizes_1', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    for record in wrong_records:
        item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
        print(f"  Item {item_id}: {type_element}.{type_item} -> {uuid_item}")
        print(f"      Body: {item_body[:80]}{'...' if len(item_body) > 80 else ''}")
    
    print("\n🔍 Analysis:")
    print("  ✅ CORRECT: Each URL gets its own UUID")
    print("  ❌ WRONG: All URLs share the same UUID")
    print("  ✅ CORRECT: Individual URL replacement")
    print("  ❌ WRONG: Complex srcset parsing needed")
    
    return correct_records, wrong_records

def test_correct_implementation():
    """Test the correct implementation approach."""
    
    print("\n" + "=" * 80)
    print("🧪 Testing Correct Implementation")
    print("=" * 80)
    
    # Simulate the correct approach
    def develop_template_body_correct(content_body: str, content_items_records: List[tuple]) -> str:
        """Correct implementation where each URL has its own UUID."""
        import re
        result = content_body
        
        # Sort records by item_id
        sorted_records = sorted(content_items_records, key=lambda x: x[0])
        
        for record in sorted_records:
            item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = record
            
            if type_item == 'srcset_url':
                # Replace individual URL in srcset
                # Find the specific URL and replace it
                url_pattern = re.escape(item_body.split()[0])  # Get just the URL part
                result = re.sub(url_pattern, f'uuid_{uuid_item}', result)
            else:
                # Standard replacement for other attributes
                if item_body in result:
                    result = result.replace(item_body, f'uuid_{uuid_item}')
        
        return result
    
    # Test with correct records
    content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg" alt="Гуманітарна допомога SVIT UA" 
                             srcset="https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w, 
                                     https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w" 
                             sizes="(max-width: 683px) 100vw, 400px">'''
    
    correct_records = [
        (1, 38, 'src_1', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg', '2025-01-01', '2025-01-01'),
        (2, 38, 'alt_1', 'img', 'alt', 'Гуманітарна допомога SVIT UA', '2025-01-01', '2025-01-01'),
        (3, 38, 'srcset_1', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-683x1024.jpg 683w', '2025-01-01', '2025-01-01'),
        (4, 38, 'srcset_2', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-200x300.jpg 200w', '2025-01-01', '2025-01-01'),
        (5, 38, 'srcset_3', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-768x1152.jpg 768w', '2025-01-01', '2025-01-01'),
        (6, 38, 'srcset_4', 'img', 'srcset_url', 'https://svituawww.github.io/uploads1/2025/06/1-1024x1536.jpg 1024w', '2025-01-01', '2025-01-01'),
        (7, 38, 'sizes_1', 'img', 'sizes', '(max-width: 683px) 100vw, 400px', '2025-01-01', '2025-01-01')
    ]
    
    print("📋 Testing correct implementation...")
    result = develop_template_body_correct(content_body, correct_records)
    
    print("📋 Result:")
    print(result)
    
    # Check results
    print("\n✅ Analysis:")
    import re
    unique_uuids = set(re.findall(r'uuid_([a-z0-9_]+)', result))
    print(f"  Unique UUIDs found: {len(unique_uuids)}")
    print(f"  Expected UUIDs: {len(correct_records)}")
    
    # Check for duplicate UUIDs
    all_uuids = re.findall(r'uuid_([a-z0-9_]+)', result)
    duplicates = [uuid for uuid in set(all_uuids) if all_uuids.count(uuid) > 1]
    
    if duplicates:
        print(f"  ❌ Duplicate UUIDs found: {duplicates}")
    else:
        print(f"  ✅ No duplicate UUIDs found")
    
    return result

def main():
    """Main function to demonstrate the correct approach."""
    print("🎯 id_part7: Correct srcset approach demonstration")
    print("=" * 80)
    
    # Demonstrate the correct approach
    correct_records, wrong_records = demonstrate_correct_srcset_approach()
    
    # Test the correct implementation
    result = test_correct_implementation()
    
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print("✅ The issue is in the content extraction process!")
    print("✅ Each URL in srcset should be a separate database record")
    print("✅ Current implementation treats entire srcset as one item")
    print("✅ Need to modify extract_img_from_element to split srcset URLs")
    print("✅ This will give each URL its own unique UUID")

if __name__ == "__main__":
    main() 