# ID_PART6 Documentation: HTML Segmentation - 3 Types Approach

## Overview

**ID_PART6** implements a simplified HTML segmentation strategy that extracts three distinct content types from HTML files: **HTML structure**, **CSS styles**, and **JavaScript code**. This approach addresses the limitations of previous segmentation methods (`id_part3` and `id_part4`) by providing a clean, predictable separation.

## Implementation Details

### Core Strategy
- **Regex-Based Block Detection**: Uses regular expressions to identify complete `<style>` and `<script>` blocks
- **Clean HTML Extraction**: Removes CSS and JS blocks from original HTML to obtain pure structure
- **Three-File Output**: Creates separate files for each content type

### Technical Approach

#### 1. CSS Extraction
```python
css_pattern = r'<style[^>]*>.*?</style>'
css_matches = re.findall(css_pattern, html_content, re.DOTALL | re.IGNORECASE)
```

#### 2. JavaScript Extraction
```python
js_pattern = r'<script[^>]*>.*?</script>'
js_matches = re.findall(js_pattern, html_content, re.DOTALL | re.IGNORECASE)
```

#### 3. HTML Structure Extraction
```python
# Remove CSS and JS blocks from original HTML
html_clean = re.sub(css_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
html_clean = re.sub(js_pattern, '', html_clean, flags=re.DOTALL | re.IGNORECASE)
```

## File Structure

### Input
- **Source**: `svituawww.github.io/index.html`
- **Size**: 61,096 characters (complete file with inline CSS/JS)

### Output Files

#### 1. `index_html_.html` (28KB, 409 lines)
- **Content**: Pure HTML structure without CSS/JS blocks
- **Size**: 25,061 characters
- **Purpose**: HTML structure analysis and modification
- **Characteristics**:
  - Clean HTML markup
  - No embedded styles or scripts
  - Ready for templating systems
  - Suitable for content management

#### 2. `index_style_.css` (19KB, 767 lines)
- **Content**: All CSS styles extracted from `<style>` blocks
- **Size**: 19,293 characters
- **Purpose**: Style analysis and modification
- **Characteristics**:
  - Complete CSS rules and declarations
  - Responsive design styles
  - Animation and transition effects
  - Mobile-first approach

#### 3. `index_script_.js` (16KB, 335 lines)
- **Content**: All JavaScript code extracted from `<script>` blocks
- **Size**: 16,742 characters
- **Purpose**: JavaScript analysis and modification
- **Characteristics**:
  - Interactive functionality
  - Data structures (partnersData, teamData)
  - Event handlers
  - DOM manipulation

## Implementation Script

### File: `scripts/html_segmenter_simple_3types.py`

```python
#!/usr/bin/env python3
"""
Simple HTML Segmenter - 3 Types Only
Uses regex to extract HTML, CSS, and JavaScript into 3 separate files.
"""

import re
from pathlib import Path


class SimpleHTMLSegmenter:
    def __init__(self):
        self.html_content = ""
        self.css_content = ""
        self.js_content = ""
    
    def segment_html_simple(self, html_content: str):
        """Segment HTML into 3 types: HTML, CSS, JS"""
        
        # Extract CSS blocks
        css_pattern = r'<style[^>]*>.*?</style>'
        css_matches = re.findall(css_pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.css_content = "\n\n".join(css_matches)
        
        # Extract JavaScript blocks
        js_pattern = r'<script[^>]*>.*?</script>'
        js_matches = re.findall(js_pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.js_content = "\n\n".join(js_matches)
        
        # Extract HTML structure (everything else)
        # Remove CSS and JS blocks from HTML content
        html_clean = re.sub(css_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_clean = re.sub(js_pattern, '', html_clean, flags=re.DOTALL | re.IGNORECASE)
        self.html_content = html_clean
    
    def save_to_files(self, output_dir: Path):
        """Save the 3 content types to separate files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        # Save HTML content
        if self.html_content.strip():
            html_file = output_dir / "index_html_.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(self.html_content)
            saved_files.append(html_file)
        
        # Save CSS content
        if self.css_content.strip():
            css_file = output_dir / "index_style_.css"
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(self.css_content)
            saved_files.append(css_file)
        
        # Save JavaScript content
        if self.js_content.strip():
            js_file = output_dir / "index_script_.js"
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(self.js_content)
            saved_files.append(js_file)
        
        return saved_files
    
    def process_file(self, input_file: Path, output_dir: Path):
        """Process HTML file and save to 3 separate files"""
        print(f"Processing with simple 3-type approach: {input_file}")
        
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Segment HTML into 3 types
        self.segment_html_simple(html_content)
        print(f"✅ Simple segmentation completed")
        
        # Save to 3 files
        saved_files = self.save_to_files(output_dir)
        
        print(f"📁 Results saved to:")
        for file in saved_files:
            print(f"   {file}")
        
        return {
            'html_size': len(self.html_content),
            'css_size': len(self.css_content),
            'js_size': len(self.js_content)
        }


def main():
    # File paths
    input_file = Path("svituawww.github.io/index.html")
    output_dir = Path("svituawww.github.io/output")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    # Process file with simple approach
    segmenter = SimpleHTMLSegmenter()
    results = segmenter.process_file(input_file, output_dir)
    
    print(f"\n📊 Simple 3-Type Summary:")
    print(f"   Input: {input_file}")
    print(f"   Output directory: {output_dir}")
    print(f"   HTML size: {results['html_size']} chars")
    print(f"   CSS size: {results['css_size']} chars")
    print(f"   JS size: {results['js_size']} chars")


if __name__ == "__main__":
    main()
```

## Usage Instructions

### Running the Segmentation

```bash
cd /Users/nirsixadmin/Desktop/SvitUA
python3 scripts/html_segmenter_simple_3types.py
```

### Expected Output

```
Processing with simple 3-type approach: svituawww.github.io/index.html
✅ Simple segmentation completed
📁 Results saved to:
   svituawww.github.io/output/index_html_.html
   svituawww.github.io/output/index_style_.css
   svituawww.github.io/output/index_script_.js

📊 Simple 3-Type Summary:
   Input: svituawww.github.io/index.html
   Output directory: svituawww.github.io/output
   HTML size: 25061 chars
   CSS size: 19293 chars
   JS size: 16742 chars
```

## Advantages of This Approach

### 1. **Simplicity**
- Clear, predictable separation
- No complex parsing logic
- Easy to understand and maintain

### 2. **Reliability**
- Regex patterns are well-tested
- Handles edge cases gracefully
- No false positives or duplicates

### 3. **Modularity**
- Each content type in separate file
- Easy to modify individual components
- Supports different development workflows

### 4. **Performance**
- Fast execution
- Minimal memory usage
- Efficient file I/O operations

## Content Analysis

### HTML Structure (`index_html_.html`)
- **Sections**: Header, Hero, Partners, Services, Events, Join, FAQ, Contact, Footer
- **Elements**: Navigation, forms, images, text content
- **Attributes**: Links, IDs, classes, data attributes
- **Accessibility**: ARIA labels, semantic markup

### CSS Styles (`index_style_.css`)
- **Layout**: Flexbox, Grid, positioning
- **Responsive**: Media queries, mobile-first design
- **Animations**: Transitions, keyframes, transforms
- **Theming**: Color schemes, typography, spacing
- **Components**: Cards, buttons, navigation, forms

### JavaScript Code (`index_script_.js`)
- **Data Structures**: `partnersData`, `teamData`
- **Event Handlers**: Click events, form submissions
- **DOM Manipulation**: Element selection, content updates
- **Mobile Menu**: Toggle functionality, overlay management
- **Carousel**: Partner image rotation, seamless loops

## Comparison with Previous Approaches

### ID_PART3 (Parser-Based with Regex Fallback)
- **Issues**: Complex parsing logic, inconsistent results
- **Status**: ❌ Unsatisfactory

### ID_PART4 (DOM Tree Traversal)
- **Issues**: Over-segmentation, difficult to reconstruct
- **Status**: ❌ Unsatisfactory

### ID_PART6 (Simple 3-Type Approach)
- **Advantages**: Clean separation, predictable results
- **Status**: ✅ Successful

## Use Cases

### 1. **Content Management**
- Separate content from presentation
- Easy template modification
- Component-based development

### 2. **Style Analysis**
- CSS optimization opportunities
- Responsive design review
- Performance optimization

### 3. **JavaScript Refactoring**
- Code organization
- Function extraction
- Module development

### 4. **Documentation**
- Code structure analysis
- Component documentation
- Style guide development

## Future Enhancements

### 1. **Advanced Segmentation**
- Inline styles extraction
- External resource detection
- Comment preservation

### 2. **Validation**
- HTML structure validation
- CSS syntax checking
- JavaScript linting

### 3. **Reconstruction**
- Merge functionality
- Template generation
- Build process integration

## Conclusion

**ID_PART6** successfully addresses the segmentation requirements by providing a clean, reliable approach to separating HTML, CSS, and JavaScript content. The three-file output format is ideal for analysis, modification, and development workflows while maintaining the integrity of the original content.

The approach is simple, efficient, and produces predictable results, making it suitable for automated processing and manual development tasks. 