#!/usr/bin/env python3
"""
Debug srcset URL comparison
"""

# Test case
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

print("🔍 Debug srcset URL comparison")
print("=" * 60)

# Get src URL
src_url = None
for record in content_items_records:
    if record[4] == 'src':  # type_item == 'src'
        src_url = record[5]  # item_body
        break

print(f"📋 src URL: {src_url}")

# Parse srcset URLs
import re
srcset_pattern = rf'srcset\s*=\s*["\']([^"\']+)["\']'
match = re.search(srcset_pattern, content_body, re.IGNORECASE)
if match:
    srcset_value = match.group(1)
    urls = [url.strip() for url in srcset_value.split(',')]
    
    print(f"📋 srcset value: {srcset_value}")
    print(f"📋 URLs in srcset:")
    
    for i, url in enumerate(urls):
        url_parts = url.strip().split()
        if url_parts:
            original_url = url_parts[0]
            descriptor = ' '.join(url_parts[1:]) if len(url_parts) > 1 else ''
            
            print(f"  URL {i+1}: {original_url}")
            print(f"    Descriptor: {descriptor}")
            print(f"    Matches src: {original_url == src_url}")
            print(f"    src_url: {src_url}")
            print(f"    original_url: {original_url}")
            print(f"    Equal: {original_url == src_url}")
            print() 