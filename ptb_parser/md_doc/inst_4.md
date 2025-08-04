<!-- File Processing → Brackets → Elements → Validation → Content Extraction → Summary -->


<!-- PRESERVE begin id_part1 -->

create this table

CREATE TABLE content_tech_html (
    content_id INTEGER,           -- Auto-incremental per file_id
    techhtml_id_start INTEGER,          
    techhtml_id_end INTEGER,
    file_id INTEGER NOT NULL,
    pos_start INTEGER NOT NULL,
    pos_end INTEGER NOT NULL,
    content_body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (file_id, content_id),  -- Composite primary key
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (techhtml_id_start) REFERENCES tech_html_elements(techhtml_id),
    FOREIGN KEY (techhtml_id_end) REFERENCES tech_html_elements(techhtml_id)    
);



SELECT pos_open_ttag, pos_close_ttag, file_id, type_ttag, name_tech_tag_html  FROM tech_html_elements  LIMIT 5;

lets create loop by each reacord and element in sql query and print it


<!-- PRESERVE end id_part1 -->


<!-- PRESERVE begin id_part2 -->

check all parametrs with name limit 
by defualt fetch all refactor any limit to means all


 in 
 ptb_parser/scripts/enhanced_file_processor.py
 ptb_parser/scripts/enhanced_tech_html_parser.py




CREATE TABLE content_items_tech_html (
                    item_id INTEGER,    -- Auto-incremental per content_id
                    content_id INTEGER,
                    type_content VARCHAR(15) DEFAULT 'img_src',  -- Content item type classification
                    item_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Last update timestamp
                    PRIMARY KEY (item_id, content_id),  -- Composite primary key
                    FOREIGN KEY (content_id) REFERENCES content_tech_html(content_id)    
                )


<!-- PRESERVE end id_part2 -->


<!-- PRESERVE begin id_part3 -->
SELECT 
content_tech_html.content_id, content_tech_html.content_body, 
content_items_tech_html.item_body,
content_items_tech_html.type_element, content_items_tech_html.type_item 
from content_tech_html 
left join content_items_tech_html on content_tech_html.content_id = content_items_tech_html.content_id

<!-- PRESERVE end id_part3 -->

<!-- PRESERVE begin id_part4 -->

implement all testing first in  ptb_parser/test_regex.py

## Enhanced Image Attribute Extraction

### Test Cases for Comprehensive Regex Development

**Test Case 1: Complex img tag with all attributes**
```html
<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Літературний вечір" 
     srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
             https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
             https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
             https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
             https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
     sizes="(max-width: 768px) 100vw, 400px">
```

**Test Case 2: Simple img tag**
```html
<img src="image.jpg" alt="Simple image">
```

**Test Case 3: img tag with single quotes**
```html
<img src='image.png' alt='Single quoted' srcset='image.png 1x'>
```

**Test Case 4: img tag with mixed quotes and spaces**
```html
<img  src = "image.jpg"  alt = "Mixed spacing"  srcset = "image.jpg 1x"  sizes = "100vw" >
```

**Test Case 5: img tag with no alt attribute**
```html
<img src="image.jpg" srcset="image.jpg 1x, image@2x.jpg 2x">
```

### Required Extraction Attributes:
- `src` (required)
- `alt` (optional)
- `srcset` (optional)
- `sizes` (optional)

### Enhanced Regex Patterns for Testing:

```python
import re

# Comprehensive regex patterns for testing
patterns = {
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

# Test function for validation
def test_regex_patterns():
    test_cases = [
        # Test Case 1
        '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Літературний вечір" 
             srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                     https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
                     https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
                     https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
                     https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
             sizes="(max-width: 768px) 100vw, 400px">''',
        # Test Case 2
        '<img src="image.jpg" alt="Simple image">',
        # Test Case 3
        "<img src='image.png' alt='Single quoted' srcset='image.png 1x'>",
        # Test Case 4
        '<img  src = "image.jpg"  alt = "Mixed spacing"  srcset = "image.jpg 1x"  sizes = "100vw" >',
        # Test Case 5
        '<img src="image.jpg" srcset="image.jpg 1x, image@2x.jpg 2x">'
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case}")
        
        for attr, pattern_list in patterns.items():
            for j, pattern in enumerate(pattern_list):
                match = re.search(pattern, test_case, re.IGNORECASE)
                if match:
                    print(f"  {attr} (pattern {j+1}): {match.group(1)}")
                else:
                    print(f"  {attr} (pattern {j+1}): Not found")

# Run tests
if __name__ == "__main__":
    test_regex_patterns()
```

### Enhanced Extraction Method (After Testing):

```python
def extract_img_from_element(self, content_body: str) -> List[tuple]:
    """
    Extract all img attributes from an element with enhanced regex patterns.
    
    Args:
        content_body (str): HTML content containing img tag
        
    Returns:
        List[tuple]: List of (element_type, attribute_name, attribute_value) tuples
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

# Additional validation method
def validate_img_extraction(self, content_body: str) -> dict:
    """
    Validate img extraction and return detailed results.
    
    Args:
        content_body (str): HTML content to validate
        
    Returns:
        dict: Validation results with extracted attributes and metadata
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
```

### Testing and Validation Steps:

1. **Run the test_regex_patterns() function** with all test cases
2. **Validate extraction accuracy** for each test case
3. **Check edge cases** like missing attributes, different quote styles
4. **Performance testing** with large HTML content
5. **Integration testing** with actual database content

### Implementation Notes:

- Use `re.IGNORECASE` flag for case-insensitive matching
- Handle both single and double quotes
- Account for variable whitespace around attributes
- Validate that src attribute is always present (required for img tags)
- Consider srcset parsing for individual image sources and descriptors
- Add error handling for malformed HTML


<!-- PRESERVE end id_part4 -->                         


<!-- PRESERVE begin id_part5 -->           

consider
ptb_parser/project_config.json



## Enhanced Template Body Development Testing

### Overview
Develop comprehensive test script for the `develop_template_body` function that transforms HTML content by replacing attribute values with UUID placeholders based on content_items_records from the database.

### Database Schema Understanding
```sql
TABLE content_items_tech_html (
    item_id INTEGER,    -- Auto-incremental per content_id
    content_id INTEGER,
    uuid_item VARCHAR(36),  -- UUID for replacement
    type_element VARCHAR(10) DEFAULT 'img',  -- element type classification
    type_item VARCHAR(15) DEFAULT 'src',  -- element item type classification
    item_body TEXT,  -- Original attribute value
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (item_id, content_id),
    FOREIGN KEY (content_id) REFERENCES content_tech_html(content_id)    
)
```

### Function Signature

ptb_parser/scripts/extract_content_items.py

```python
def develop_template_body(self, content_body: str, content_items_records: List[tuple]) -> str:
    """
    Develop template body from content body by replacing attribute values with UUID placeholders.
    
    Args:
        content_body (str): Original HTML content (e.g., '<img src="image.jpg" alt="Logo">')
        content_items_records (List[tuple]): List of (item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at) tuples
        
    Returns:
        str: Template body with UUID placeholders (e.g., '<img src="uuid_abc123" alt="uuid_def456">')
    """
```

### Key Understanding: UUID Replacement Logic
The function should:
1. **Extract the `uuid_item`** from each database record
2. **Find the original attribute value** (`item_body`) in the HTML content
3. **Replace it with `uuid_{uuid_item}`** format
4. **Handle multiple attributes** for the same element

### Database Query and Record Processing
```python
def get_content_items_by_content_id(self, content_id: int, limit: int = 0) -> List[tuple]:
    """Get content items for a specific content_id"""
    # Returns: (item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at)

# Record processing:
content_items_records = get_content_items_by_content_id(content_id, limit)
# Each record: (item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at)
```

### Test Cases for Comprehensive Testing

**Test Case 1: Simple img tag with src and alt**
```python
content_body = '<img src="https://example.com/image.jpg" alt="Logo">'
content_items_records = [
    (1, 1, 'bdad656e', 'img', 'src', 'https://example.com/image.jpg', '2025-01-01', '2025-01-01'),
    (2, 1, '7e92fb3f', 'img', 'alt', 'Logo', '2025-01-01', '2025-01-01')
]
# Expected: '<img src="uuid_bdad656e" alt="uuid_7e92fb3f">'
```

**Test Case 2: Complex img tag with all attributes**
```python
content_body = '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" 
                    alt="Літературний вечір" 
                    srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                            https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w" 
                    sizes="(max-width: 768px) 100vw, 400px">'''
content_items_records = [
    (1, 1, 'e67ed269', 'img', 'src', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png', '2025-01-01', '2025-01-01'),
    (2, 1, '16c025db', 'img', 'alt', 'Літературний вечір', '2025-01-01', '2025-01-01'),
    (3, 1, 'ece52aa9', 'img', 'srcset', 'https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w', '2025-01-01', '2025-01-01'),
    (4, 1, '14d97141', 'img', 'sizes', '(max-width: 768px) 100vw, 400px', '2025-01-01', '2025-01-01')
]
# Expected: '<img src="uuid_e67ed269" alt="uuid_16c025db" srcset="uuid_ece52aa9" sizes="uuid_14d97141">'
```

**Test Case 3: Link tag with href and title**
```python
content_body = '<a href="#contact" title="Contact Us">Contact</a>'
content_items_records = [
    (1, 1, 'a8f3c2d1', 'a', 'href', '#contact', '2025-01-01', '2025-01-01'),
    (2, 1, 'b9e4d3c2', 'a', 'title', 'Contact Us', '2025-01-01', '2025-01-01')
]
# Expected: '<a href="uuid_a8f3c2d1" title="uuid_b9e4d3c2">Contact</a>'
```

**Test Case 4: Mixed content with multiple elements**
```python
content_body = '<div><img src="logo.png" alt="Logo"><a href="#home">Home</a></div>'
content_items_records = [
    (1, 1, 'c7f5e4d3', 'img', 'src', 'logo.png', '2025-01-01', '2025-01-01'),
    (2, 1, 'd8g6f5e4', 'img', 'alt', 'Logo', '2025-01-01', '2025-01-01'),
    (3, 1, 'e9h7g6f5', 'a', 'href', '#home', '2025-01-01', '2025-01-01')
]
# Expected: '<div><img src="uuid_c7f5e4d3" alt="uuid_d8g6f5e4"><a href="uuid_e9h7g6f5">Home</a></div>'
```

**Test Case 5: Edge cases - special characters and encoding**
```python
content_body = '<img src="image.jpg" alt="Special: &quot;quotes&quot; &amp; symbols">'
content_items_records = [
    (1, 1, 'f0i8h7g6', 'img', 'src', 'image.jpg', '2025-01-01', '2025-01-01'),
    (2, 1, 'g1j9i8h7', 'img', 'alt', 'Special: &quot;quotes&quot; &amp; symbols', '2025-01-01', '2025-01-01')
]
# Expected: '<img src="uuid_f0i8h7g6" alt="uuid_g1j9i8h7">'
```

**Test Case 6: Empty or missing attributes**
```python
content_body = '<img src="image.jpg">'
content_items_records = [
    (1, 1, 'h2k0j9i8', 'img', 'src', 'image.jpg', '2025-01-01', '2025-01-01')
]
# Expected: '<img src="uuid_h2k0j9i8">'
```

### Testing Requirements

1. **Standalone Testing**: Test with predefined test cases using full database records
2. **Database Integration**: Test with real content from SQLite database
3. **Performance Testing**: Test with large content (100x repeated HTML)
4. **Edge Case Testing**: Test with special characters and malformed content
5. **Validation Testing**: Verify UUID replacements are correct

### Database Integration Testing

The test script should include comprehensive database integration testing that:

1. **Connects to existing SQLite database**
2. **Retrieves real content_tech_html records**
3. **Extracts content_items_tech_html data with correct structure:**
   ```sql
   SELECT item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at
   FROM content_items_tech_html 
   WHERE content_id = ?
   ORDER BY item_id
   ```
4. **Processes records correctly:**
   ```python
   item_id, content_id, uuid_item, type_element, type_item, item_body, created_at, updated_at = content_item_record
   # Use uuid_item for replacement: uuid_{uuid_item}
   ```
5. **Tests develop_template_body with real data**
6. **Validates UUID replacements**
7. **Reports success/failure statistics**

### Performance Testing

The test script should include performance testing with:

1. **Large content (100x repeated HTML)**
2. **Many content items (1000+ attributes)**
3. **Processing time measurement**
4. **UUID replacement counting**
5. **Performance benchmarks**

### Expected Results

- **Standalone tests**: All 6 test cases should pass
- **Database integration**: Should process real content successfully
- **Performance**: Should handle large content within reasonable time
- **UUID replacements**: Should correctly replace attribute values with `uuid_{uuid_item}` format

### Implementation Notes

- **Robust error handling** for malformed content
- **Performance optimization** for large datasets
- **Comprehensive validation** of replacement accuracy
- **Database integration** with existing schema
- **Detailed reporting** of test results
- **UUID format**: Always use `uuid_{uuid_item}` format for replacements

<!-- PRESERVE end id_part5 -->                         








<!-- PRESERVE begin id_part6 -->

## Enhanced Meta Description Extraction

### Objective
Develop a precise regex pattern to extract **only** `<meta name="description">` tags while **excluding** all other meta tags (viewport, keywords, robots, etc.).

### Requirements
1. **Target**: Extract only `<meta name="description" content="...">` tags
2. **Exclude**: All other meta tags (`<meta name="viewport">`, `<meta name="keywords">`, etc.)
3. **Handle**: Various quote styles (single/double quotes)
4. **Handle**: Whitespace variations
5. **Handle**: Case-insensitive matching
6. **Extract**: The content attribute value

### Regex Pattern Development

#### Pattern 1: Basic Description Meta Tag
```python
# Basic pattern for meta description
description_pattern = r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']'
```

#### Pattern 2: Enhanced with Whitespace Handling
```python
# Enhanced pattern with better whitespace handling
description_pattern = r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']'
```

#### Pattern 3: Case-Insensitive Version
```python
# Case-insensitive pattern
description_pattern = r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']'
```

### Test Cases for Comprehensive Validation

#### Test Case 1: Standard Description Meta
```html
<meta name="description" content="Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об'єднує людей, які вірять у силу підтримки, солідарності та дій.">
```
**Expected**: Extract content value

#### Test Case 2: Single Quotes
```html
<meta name='description' content='This is a description with single quotes'>
```
**Expected**: Extract content value

#### Test Case 3: Mixed Whitespace
```html
<meta  name  =  "description"  content  =  "Description with extra spaces">
```
**Expected**: Extract content value

#### Test Case 4: Viewport Meta (Should NOT Match)
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
**Expected**: No match

#### Test Case 5: Keywords Meta (Should NOT Match)
```html
<meta name="keywords" content="html, css, javascript">
```
**Expected**: No match

#### Test Case 6: Robots Meta (Should NOT Match)
```html
<meta name="robots" content="noindex, nofollow">
```
**Expected**: No match

#### Test Case 7: Multiple Meta Tags
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="This should be extracted">
<meta name="keywords" content="test, example">
```
**Expected**: Extract only the description content

#### Test Case 8: Case Variations
```html
<meta NAME="DESCRIPTION" CONTENT="Case insensitive test">
<meta Name="Description" Content="Mixed case test">
```
**Expected**: Extract content values

#### Test Case 9: Special Characters in Content
```html
<meta name="description" content="Description with &quot;quotes&quot; &amp; symbols">
```
**Expected**: Extract content with HTML entities

#### Test Case 10: Self-Closing Tag
```html
<meta name="description" content="Self closing tag" />
```
**Expected**: Extract content value

### Implementation Function

```python
import re

def extract_meta_description(html_content: str) -> List[str]:
    """
    Extract meta description content from HTML.
    
    Args:
        html_content (str): HTML content to search
        
    Returns:
        List[str]: List of description content values found
    """
    # Enhanced regex pattern for meta description
    description_pattern = r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\']([^"\']+)["\']'
    
    # Find all matches
    matches = re.findall(description_pattern, html_content, re.IGNORECASE)
    
    return matches

def validate_meta_extraction(html_content: str) -> dict:
    """
    Validate meta description extraction and return detailed results.
    
    Args:
        html_content (str): HTML content to validate
        
    Returns:
        dict: Validation results with extracted descriptions and metadata
    """
    descriptions = extract_meta_description(html_content)
    
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
```

### Testing Requirements

1. **Positive Testing**: Verify description meta tags are extracted
2. **Negative Testing**: Verify other meta tags are NOT extracted
3. **Edge Case Testing**: Test with various quote styles and whitespace
4. **Performance Testing**: Test with large HTML content
5. **Integration Testing**: Test with real HTML files

### Expected Results

- **Test Cases 1-3, 7-10**: Should extract description content
- **Test Cases 4-6**: Should NOT extract anything
- **All cases**: Should handle various formatting styles
- **Performance**: Should work efficiently with large content

### Implementation Notes

- Use `re.IGNORECASE` flag for case-insensitive matching
- Handle both single and double quotes
- Account for variable whitespace around attributes
- Ensure only `name="description"` tags are matched
- Extract the `content` attribute value
- Handle HTML entities in content values
- Support self-closing tags

<!-- PRESERVE end id_part6 -->


<!-- PRESERVE begin id_part7 -->


<!-- PRESERVE end id_part7 -->