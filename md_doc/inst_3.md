

### Database Schema Structure

**Important Design Decision: No Part Order Storage**

We intentionally exclude `part_order` from the schema because:

1. **Dynamic Order Changes**: Part order can change at any moment during file operations (insertions, deletions, reordering)
2. **Pointer-Based Navigation**: Order is determined by following `next_part_id` and `prev_part_id` pointers, not by stored order values
3. **Eliminates Recalculation Overhead**: No need to update order values for all parts when inserting/removing segments
4. **Consistency Guarantee**: Pointers always reflect the current order, preventing order/pointer mismatches
5. **Performance Optimization**: Avoids expensive bulk updates when chain structure changes

**Order Determination Method:**
```python
def get_part_order(part_id):
    # Traverse backwards to count position
    current_part = part_id
    order = 0
    while current_part.prev_part_id:
        order += 1
        current_part = current_part.prev_part_id
    return order
```

```json
{
  "part_id": "part_123",
  "content": "SFRNTCB3aXRoIHNwZWNpYWwgY2hhcnM6IDw+JiInIGFuZCB1bmljb2RlOiDwn46A",
  "encoding": "base64",
  "original_size": 45,
  "encoded_size": 60,  
  "content_type": only one type,
  "next_part_id": "part_124",
  "prev_part_id": "part_122",
  "file_id": "file_456",  
  "content_hash": "sha256_hash_value",
  "metadata": {
    "contains_images": true,
    "image_count": 2,
    "last_modified": "2025-01-20T10:30:00Z"
  }
}
```


**Content Type Classification:**

Each content type contains only its specific content without overlapping with other types:

- `html`: Pure HTML markup (tags, attributes, structure)
- `js_code`: JavaScript code blocks and functions
- `css_style`: CSS stylesheet rules and declarations
- `url`: URL strings and web addresses
- `text`: Plain text content in any language 


step2

**HTML File Segmentation Strategy**

**Goal:** Cut HTML files into parts by content types defined in Content Type Classification.

**Approaches:**

1. **Parser-Based Segmentation**: Use HTML/JS/CSS parsers to identify and extract different content types while preserving structure and relationships.

2. **Regex Pattern Matching**: Apply regular expressions to detect content boundaries and separate HTML, JavaScript, CSS, URLs, and text content.

3. **DOM Tree Traversal**: Parse HTML into DOM tree, traverse nodes, and group by content type while maintaining hierarchical relationships.

4. **Lexical Analysis**: Tokenize file content and classify tokens by type, then reconstruct segments based on token sequences.

**Recommended Strategy:** Parser-based approach for accuracy, with fallback to regex for edge cases.

<!-- PRESERVE: promt: improve this inst and save length 100 strings for it. Corrected grammar version should be placed below this promt -->



step3
<!-- PRESERVE improve only this part of instruction. use no more then 40 strings for this part. -->
<!-- PRESERVE begin  id_part3 -->
Test parser-based approach with regex fallback. Create Python script to segment HTML by content type, separate with newlines, save to output files. Input: svituawww.github.io/index.html. Output: svituawww.github.io/output/index_newlines.html

Example output format:
part1 type html:
 <title>
part2 type text: 
SVIT UA - Гуманітарна допомога та інтеграція українців у Швеції
part3 type html:
 </title>
part4 type html: 
<meta name="description" content="
part5 type text:
 Гуманітарна допомога, волонтерство та інтеграція — ми поруч із тобою в Швеції. SVIT UA об'єднує людей, які вірять у силу підтримки, солідарності та дій.
part6 type html:
"> <style>

<!-- PRESERVE end  id_part3 -->

step4


<!-- PRESERVE improve only this part of instruction. use no more then 40 strings for this part. -->
<!-- PRESERVE begin  id_part4 -->
Test DOM Tree Traversal approach. Create Python script to segment HTML by content type, separate with newlines, save to output files. Input: svituawww.github.io/index.html. Output: svituawww.github.io/output/index_DOM_newlines.html

Example output format:
part1 type html: <html>
part2 type html: <head>
part3 type text: DOM traversal content
part4 type html: </head>
<!-- PRESERVE end  id_part4 -->



<!-- PRESERVE improve only this part of instruction. use no more then 40 strings for this part. -->
<!-- PRESERVE begin  id_part5 -->
Previous approaches (id_part3, id_part4) results unsatisfactory. Need hybrid/composite multi-level approach. Level 1: Which approach best for splitting entire CSS, HTML tags, JS blocks? 

<!-- PRESERVE end  id_part5 -->


<!-- PRESERVE improve only this part of instruction. use no more then 40 strings for this part. -->
<!-- PRESERVE begin  id_part6 -->

1. **Regex-Based Block Detection** (Primary Method):
   - Use regex patterns to identify complete blocks
   - `<style>...</style>` for CSS blocks
   - `<script>...</script>` for JavaScript blocks
   - `<html>...</html>` for HTML structure

Test this approach. Create Python script and save to output files. Input: svituawww.github.io/index.html. 
Outputs: 
svituawww.github.io/output/index_html_.html
svituawww.github.io/output/index_style_.css
svituawww.github.io/output/index_script_.js

<!-- PRESERVE end  id_part6 -->


<!-- PRESERVE improve only this part of instruction. use no more then 100 strings for this part. -->
<!-- PRESERVE begin  id_part7 -->
Level 1 completed successfully with regex-based block detection. Level 2: HTML Block Segmentation.

**Level 2 Goal**: Extract and identify major HTML structural blocks from the clean HTML output.

**Algorithm Approach**:
1. **Priority-Based Processing**: Process blocks in order of importance (head → header → nav → section → footer)
2. **Non-Overlapping Extraction**: Each HTML element can only belong to one block
3. **Consistency Validation**: Ensure entire_html = sum of all blocks
4. **Conflict Resolution**: When blocks overlap, prioritize the higher-priority block

**HTML Blocks to Extract**:
Based on input JSON configuration data:
- `<head>` - Document head section
- `<header>` - Site header/navigation
- `<section>` - Content sections (hero, services, events, etc.)
- `<footer>` - Site footer
- `<nav>` - Navigation blocks
- `<main>` - Main content area
- `<aside>` - Sidebar content

**JSON Configuration Structure** (`scripts/json/html_blocks_config.json`):
```json
{
  "html_blocks": {
    "head": {
      "start": "<head",
      "end": "</head>",
      "type": "document",
      "category": "metadata",
      "required": true,
      "nesting": "root"
    },
    "header": {
      "start": "<header",
      "end": "</header>",
      "type": "navigation",
      "category": "layout",
      "required": false,
      "nesting": "body"
    },
    "section": {
      "start": "<section",
      "end": "</section>",
      "type": "content",
      "category": "content",
      "required": false,
      "nesting": "body",
      "attributes": ["id", "class"]
    },
    "footer": {
      "start": "<footer",
      "end": "</footer>",
      "type": "navigation",
      "category": "layout",
      "required": false,
      "nesting": "body"
    },
    "nav": {
      "start": "<nav",
      "end": "</nav>",
      "type": "navigation",
      "category": "layout",
      "required": false,
      "nesting": "any"
    },
    "main": {
      "start": "<main",
      "end": "</main>",
      "type": "content",
      "category": "content",
      "required": false,
      "nesting": "body"
    },
    "aside": {
      "start": "<aside",
      "end": "</aside>",
      "type": "content",
      "category": "content",
      "required": false,
      "nesting": "body"
    }
  },
  "processing_options": {
    "include_unidentified": true,
    "generate_hierarchy": true,
    "performance_tracking": true,
    "output_format": "detailed"
  },
  "validation_rules": {
    "allow_overlaps": false,
    "require_complete_coverage": true,
    "priority_order": ["head", "header", "nav", "section", "footer"],
    "consistency_check": true
  }
}
```

**Implementation Requirements**:
1. Create JSON configuration file with HTML block definitions in `scripts/json/html_blocks_config.json`
2. Extend `scripts/html_segmenter_simple_3types.py` with Level 2 functionality
3. Parse `svituawww.github.io/output/index_html_.html` (Level 1 output)
4. Use JSON config to identify and extract each major HTML block
5. **Critical Constraint**: Ensure non-overlapping blocks only - each HTML element can belong to only one block
6. **Block Consistency**: Extract only consistent blocks where entire_html = block1_html + block2_html + block3_html + ... + blockN_html
7. **Priority Order**: Process blocks in priority order (head → header → nav → section → footer) to avoid conflicts
8. Add HTML comments to mark block boundaries with block type and category
9. Save segmented HTML with block highlighting
10. Generate comprehensive block analysis report including:
    - Identified blocks (count, size, type)
    - Unidentified sections (new blocks to add to config)
    - Block hierarchy and nesting analysis
    - Performance metrics (processing time, memory usage)
    - Block overlap validation (must be 0%) 

**Test Level 2**: Create Python script with Level 2 functionality.
Input: `svituawww.github.io/output/index_html_.html`
Outputs: 
- `svituawww.github.io/output/html/index_html_blocks.html` (segmented HTML)
- `svituawww.github.io/output/html/blocks_analysis.json` (block report)

**Expected Output Format**:
```html
<!-- BLOCK_START: head (document) -->
<head>
    <meta charset="UTF-8">
    <!-- ... head content ... -->
</head>
<!-- BLOCK_END: head -->

<!-- BLOCK_START: header (navigation) -->
<header>
    <nav class="container">
    <!-- ... header content ... -->
    </nav>
</header>
<!-- BLOCK_END: header -->

<!-- BLOCK_START: section (content) -->
<section id="home" class="hero">
    <!-- ... section content ... -->
</section>
<!-- BLOCK_END: section -->
```

**Block Analysis Report Format** (`blocks_analysis.json`):
```json
{
  "processing_summary": {
    "total_blocks": 15,
    "identified_blocks": 12,
    "unidentified_sections": 3,
    "processing_time_ms": 245,
    "memory_usage_mb": 2.1,
    "block_overlap_percentage": 0.0,
    "consistency_check": "passed"
  },
  "blocks_by_type": {
    "document": 1,
    "navigation": 3,
    "content": 8
  },
  "blocks_by_category": {
    "metadata": 1,
    "layout": 4,
    "content": 10
  },
  "identified_blocks": [
    {
      "type": "head",
      "category": "metadata",
      "size": 245,
      "start_line": 1,
      "end_line": 8,
      "attributes": {},
      "nesting_level": 0
    },
    {
      "type": "header",
      "category": "layout",
      "size": 1250,
      "start_line": 9,
      "end_line": 45,
      "attributes": {"class": "container"},
      "nesting_level": 1
    }
  ],
  "unidentified_sections": [
    {
      "content": "<div class=\"unknown-block\">...</div>",
      "start_line": 150,
      "end_line": 155,
      "size": 89,
      "suggestion": "Consider adding to config as 'div.unknown-block'"
    }
  ],
  "hierarchy_analysis": {
    "max_nesting_level": 3,
    "block_dependencies": {},
    "structural_integrity": "valid"
  },
  "performance_metrics": {
    "regex_matches": 45,
    "block_processing_time": 180,
    "file_io_time": 65,
    "total_memory_peak": 2.1
  }
}
```


<!-- PRESERVE end  id_part7 -->



<!-- PRESERVE improve only this part of instruction. use no more then 40 strings for this part. -->
<!-- PRESERVE begin  id_part7.1 -->  


can it possible to divide and extract nested blocks like bloks=nav-links in this case of parent=header (layout)
considering this:
5. **Critical Constraint**: Ensure non-overlapping blocks only - each HTML element can belong to only one block
6. **Block Consistency**: Extract only consistent blocks where entire_html = block1_html + block2_html + block3_html + ... + blockN_html

?



**2. Modified Extraction Algorithm:**
- **Step 1**: Extract parent blocks (non-overlapping)
- **Step 2**: Extract nested blocks within each parent
- **Step 3**: Mark nested blocks with parent context

### **✅ Benefits:**
- **Maintains Parent Non-Overlap**: Parent blocks don't overlap
- **Enables Sub-Block Analysis**: Extract meaningful sub-components
- **Preserves Hierarchy**: Clear parent-child relationships
- **Consistent Structure**: entire_html = sum of all blocks
### **📋 Implementation Strategy:**
1. **Two-Pass Processing**: First extract parents, then nested blocks
2. **Hierarchical Markers**: Different comment styles for parent vs nested
3. **Context Preservation**: Nested blocks include parent reference
4. **Validation**: Ensure nested blocks don't cross parent boundaries
This approach allows for **detailed block analysis** while maintaining the **structural integrity** and **non-overlapping constraint** at the parent level.



<!-- BLOCK_START: header (layout) -->

<header>
        <nav class="container">
            <div class="logo">
                <img src="https://svituawww.github.io/uploads1/2025/03/svitua_100x100.png" alt="SVIT UA Logo">
                <h1>SVIT UA</h1>
            </div>
            
     <!-- BLOCK_START: nav-links -->            
            <ul class="nav-links">
                <li><a href="#home">Головна</a></li>
                <li><a href="#services">Допомога</a></li>
                <li><a href="team.html">Про нас</a></li>
                <li><a href="#faq">FAQ</a></li>
                <li><a href="#contact">Контакти</a></li>
            </ul>
     <!-- BLOCK_END: nav-links -->            

            <!-- Mobile Menu Toggle -->
            <button class="mobile-menu-toggle" onclick="toggleMobileMenu()" aria-label="Menu">
                ☰
            </button>
            
            <div style="display: flex; align-items: center; gap: 20px;">
                <div class="language-switch">
                    <a href="#" class="lang-btn active" title="Українська">🇺🇦</a>
                    <a href="#" class="lang-btn" title="Svenska">🇸🇪</a>
                    <a href="#" class="lang-btn" title="English">🇬🇧</a>
                </div>
            </div>
        </nav>

        <!-- Mobile Menu Overlay -->
        <div class="mobile-menu-overlay" onclick="closeMobileMenu()"></div>
        
        <!-- Mobile Menu -->
        <nav class="mobile-menu">
            <button class="mobile-menu-close" onclick="closeMobileMenu()" aria-label="Close Menu">
                ✕
            </button>
            
            <ul class="mobile-nav-links">
                <li><a href="#home" onclick="closeMobileMenu()">Головна</a></li>
                <li><a href="#services" onclick="closeMobileMenu()">Допомога</a></li>
                <li><a href="team.html" onclick="closeMobileMenu()">Про нас</a></li>
                <li><a href="#faq" onclick="closeMobileMenu()">FAQ</a></li>
                <li><a href="#contact" onclick="closeMobileMenu()">Контакти</a></li>
            </ul>

            <div class="mobile-language-section">
                <h4>Мова / Language</h4>
                <div class="mobile-language-switch">
                    <a href="#" class="lang-btn active" title="Українська">🇺🇦</a>
                    <a href="#" class="lang-btn" title="Svenska">🇸🇪</a>
                    <a href="#" class="lang-btn" title="English">🇬🇧</a>
                </div>
            </div>
        </nav>
    </header>
<!-- BLOCK_END: header -->


<!-- PRESERVE end  id_part7.1 -->


<!-- PRESERVE improve only this part of instruction. use no more then 200 strings for this part. -->
<!-- PRESERVE begin  id_part8 -->  

**Level 3: HTML Element Parser**

Parse each HTML element from `svituawww.github.io/output/index_html_.html` into structured JSON.
ouput result is like svituawww.github.io/output/elements_parsed.json.

**Element Structure:**
```html
<element id="jhdfj" class="dfjhjhj">
    [inner content]
</element>
```

**Parsing Rules:**
- `element`: Tag name and attributes between `<` and `>`
- `[inner content]`: Text content and nested HTML elements
- Nesting level: `<body>` = level 1, child = parent level + 1
- Element ID: Generate 8-character UUID

**JSON Structure:**
```json
{
    "name": "element",
    "id": "a1b2c3d4",
    "element_attr_content": "<element id=\"jhdfj\" class=\"dfjhjhj\">",
    "inner_content": "text_before_child_1 <child_1_id> text_between_child_1__and__child_2 <child_2_id>...text_between_child_N-1__and__child_N <child_N_id> text_after_child_N",
    "parent_id": "parent_uuid",
    "order": 1,
    "level": 2
}
```

**Examples:**

**Example 1: No Children (Only Text)**
```html
<title>SVIT UA - Гуманітарна допомога</title>
```
```json
{
    "name": "title",
    "id": "a1b2c3d4",
    "element_attr_content": "<title>",
    "inner_content": "SVIT UA - Гуманітарна допомога",
    "parent_id": "head_uuid",
    "order": 1,
    "level": 2
}
```

**Example 2: Single Child**
```html
<div class="logo">
    <img src="logo.png" alt="Logo">
</div>
```
```json
{
    "name": "div",
    "id": "b2c3d4e5",
    "element_attr_content": "<div class=\"logo\">",
    "inner_content": " <img_uuid> ",
    "parent_id": "header_uuid",
    "order": 1,
    "level": 2
}
```

**Example 3: Multiple Children with Text**
```html
<div class="container">
    Welcome to 
    <h1>SVIT UA</h1>
    - helping Ukrainians
    <p>Contact us</p>
    for support
</div>
```
```json
{
    "name": "div",
    "id": "c3d4e5f6",
    "element_attr_content": "<div class=\"container\">",
    "inner_content": "Welcome to <h1_uuid> - helping Ukrainians <p_uuid> for support",
    "parent_id": "body_uuid",
    "order": 1,
    "level": 1
}
```

**Implementation:**
1. Parse HTML using BeautifulSoup
2. Traverse DOM tree recursively
3. Generate UUID for each element
4. Extract attributes and inner content
5. Store in `svituawww.github.io/output/elements_parsed.json`

<!-- PRESERVE end  id_part8 -->


<!-- PRESERVE improve only this part of instruction. use no more then 100 strings for this part. -->
<!-- PRESERVE begin  id_part9 -->  

**Level 3: HTML Element Reconstructor**

Reverse process of `id_part8` - reconstruct original HTML from parsed JSON elements.

**Input:** `svituawww.github.io/output/elements_parsed.json`
**Output:** `svituawww.github.io/output/reconstructed_html.html`

**Validation Requirement:** 
Compare `svituawww.github.io/output/reconstructed_html.html` with source `svituawww.github.io/output/index_html_.html` - they must be identical.

**Reconstruction Rules:**
- Replace `<uuid>` references with actual element content
- Maintain original element order and nesting
- Preserve text content and whitespace exactly
- Reconstruct complete HTML structure
- Handle self-closing tags properly (`<img>`, `<meta>`, etc.)

**Algorithm:**
1. Load parsed elements from JSON
2. Build element lookup map (UUID → element)
3. Process elements in order (parent first, then children)
4. Replace `<uuid>` references recursively
5. Generate complete HTML document
6. Validate against original source file

**Examples:**

**Example 1: Simple Text Element**
```json
{
    "name": "title",
    "id": "0e04cfee",
    "element_attr_content": "<title>",
    "inner_content": "SVIT UA - Гуманітарна допомога",
    "parent_id": "189f4c81"
}
```
**Reconstructed:**
```html
<title>SVIT UA - Гуманітарна допомога</title>
```

**Example 2: Element with Child**
```json
{
    "name": "div",
    "id": "127e6b25",
    "element_attr_content": "<div class=\"logo\">",
    "inner_content": "<ed497200> <37eeb691>",
    "parent_id": "0d0d01df"
}
```
**Reconstructed:**
```html
<div class="logo">
    <img src="logo.png" alt="Logo">
    <h1>SVIT UA</h1>
</div>
```

**Example 3: Complex Nested Structure**
```json
{
    "name": "body",
    "id": "b51ee973",
    "element_attr_content": "<body>",
    "inner_content": "Header <80535237> Hero Section <684044a4> Footer <6aacb51e>",
    "parent_id": "19878a27"
}
```
**Reconstructed:**
```html
<body>
    Header
    <header>...</header>
    Hero Section
    <section>...</section>
    Footer
    <footer>...</footer>
</body>
```

**Implementation:**
1. Parse JSON elements into memory
2. Create UUID-to-element mapping
3. Process elements recursively
4. Replace UUID references with actual content
5. Generate complete HTML document
6. Validate reconstruction accuracy

**Validation Steps:**
- Compare reconstructed HTML with original source
- Check for identical content and structure
- Verify all elements and attributes are preserved
- Ensure no data loss during parse/reconstruct cycle

<!-- PRESERVE end  id_part9 -->

<!-- PRESERVE improve only this part of instruction. use no more then 300 strings for this part. -->
<!-- PRESERVE begin  id_part10 -->  

**Level 3: HTML Element Parse-Reconstruct Cycle**

develop scripts/html_parse_reconstruct_cycle.py

Combined process of `id_part8` (Parser) and `id_part9` (Reconstructor) to validate complete cycle.

**Configuration-Driven Parse-Reconstruct Cycle**

**JSON Configuration Structure** (`scripts/json/parse_reconstruct_config.json`):
```json
{
  "input_output": {
    "input_file": "svituawww.github.io/output/index_html_.html",
    "output_file": "svituawww.github.io/output/reconstructed_html.html",
    "elements_json": "svituawww.github.io/output/elements_parsed.json"
  },
  "validation_settings": {
    "strict_mode": false,
    "ignore_whitespace": false,
    "ignore_comments": false,
    "functional_equivalence": true,
    "structural_check": true,
    "content_check": true,
    "comparetion_pereachbyte":true
  },
  "processing_options": {
    "performance_tracking": true,
    "detailed_reporting": true,
    "save_intermediate": false,
    "backup_original": true
  },
  "success_criteria": {
    "content_preservation": true,
    "structure_integrity": true,
    "functional_equivalence": true,
    "data_completeness": true
  }
}
```

**Configurable Parameters:**
- **Input/Output Paths**: All file paths configurable via JSON
- **Validation Mode**: Strict (exact match) vs Functional (content-based)
- **Processing Options**: Performance tracking, detailed reporting, backups
- **Success Criteria**: Configurable validation requirements

**Benefits:**
- **Flexibility**: Easy path changes without code modification
- **Validation Control**: Adjust strictness based on requirements
- **Performance Monitoring**: Optional detailed timing and memory tracking
- **Safety**: Automatic backup of original files


**Process Flow:**
1. **Parse Phase** (`scripts/html_element_parser.py`):
   - Parse HTML into structured JSON elements
   - Generate UUIDs for each element
   - Extract attributes and inner content
   - Store in `svituawww.github.io/output/elements_parsed.json`

2. **Reconstruct Phase** (`scripts/html_element_reconstructor.py`):
   - Load parsed elements from JSON
   - Replace UUID references with actual HTML
   - Reconstruct complete HTML document
   - Save to `svituawww.github.io/output/reconstructed_html.html`

3. **Validation Phase**:
   - Compare original vs reconstructed HTML
   - Check content accuracy and structure integrity
   - Verify no data loss in parse/reconstruct cycle

**Success Criteria:**
- **Content Preservation**: All text, attributes, and elements preserved
- **Structure Integrity**: Parent-child relationships maintained
- **Functional Equivalence**: Reconstructed HTML works identically to original
- **Data Completeness**: No information lost during cycle

**Implementation Steps:**
1. Run `python3 run_element_parser.py` (Parser)
2. Run `python3 run_reconstructor.py` (Reconstructor)
3. Validate: `original_html == reconstructed_html` (functionally)
4. Generate cycle analysis report

**Expected Output:**
- `elements_parsed.json`: Structured element data
- `reconstructed_html.html`: Reconstructed HTML document
- Validation report: Success/failure with details
- Cycle summary: Statistics and analysis

**Benefits:**
- **Quality Assurance**: Proves parsing accuracy
- **Data Integrity**: Validates no information loss
- **System Reliability**: Ensures robust HTML processing
- **Debugging**: Identifies issues in parse/reconstruct cycle


<!-- PRESERVE end  id_part10 -->

























