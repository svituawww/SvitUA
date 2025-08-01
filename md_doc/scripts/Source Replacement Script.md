# SVIT UA Image Source Replacement Script

## Task Description
Create a new Python script that replaces image source references in HTML files based on the scan report data.

## Source Data
- **Input File:** `svituawww.github.io/database/reports/image_scan_report.json`
- **Contains:** Complete mapping of old `src` paths to new `new_src` URLs

## Script Requirements

### 1. **Read Scan Report**
- Load `image_scan_report.json`
- Extract `src` → `new_src` mappings
- Group by `file_path` for efficient processing

### 2. **File Processing**
- Process each HTML file listed in `file_path`
- Replace all occurrences of `src` with corresponding `new_src`
- Handle different source types:
  - `img_tag` - Replace `src` attribute in `<img>` tags
  - `js_reference` - Replace image URLs in JavaScript objects
  - `srcset` - Replace URLs in responsive image sets
  - `css_background` - Replace background image URLs

### 3. **Replacement Logic**
```python
# Example mappings from report:
"src": "uploads/2025/06/logo.png" 
"new_src": "https://svituawww.github.io/uploads1/2025/06/logo.png"

# Replace in HTML:
<img src="uploads/2025/06/logo.png"> 
# becomes:
<img src="https://svituawww.github.io/uploads1/2025/06/logo.png">
```

### 3.1 **Context Validation**
- **Check if "context"** from scan report matches the found string before replacement
- **Validate context** to ensure we're replacing the correct instance
- **Example context matching:**
  ```python
  # From scan report:
  "context": "<img src=\"uploads/2025/06/logo.png\" alt=\"Logo\">"
  
  # In HTML file, find exact match:
  <img src="uploads/2025/06/logo.png" alt="Logo">
  
  # Only replace if context matches exactly
  ```
- **Prevents false positives** and incorrect replacements
- **Ensures accuracy** of replacement operations

### 4. **Safety Features**
- **Backup original files** before modification
- **Validate file paths** exist before processing
- **Log all replacements** for audit trail
- **Handle errors gracefully** (missing files, permission issues)

### 5. **Output Requirements**
- **Modified HTML files** with updated image sources
- **Replacement report** showing what was changed
- **Backup directory** with original files
- **Summary statistics** (files processed, replacements made, errors)

## Expected Script Structure
```python
class ImageSourceReplacer:
    def load_scan_report(self)
    def create_backup(self, file_path)
    def replace_in_file(self, file_path, replacements)
    def generate_report(self)
    def main()
```

## File Locations to Process
- `svituawww.github.io/index.html`
- `svituawww.github.io/team.html`
- `svituawww.github.io/en/*.html` (if exists)
- `svituawww.github.io/sv/*.html` (if exists)

## Success Criteria
- ✅ All `src` references replaced with `new_src`
- ✅ Original files backed up
- ✅ Detailed replacement log generated
- ✅ No data loss or corruption
- ✅ Script can be run multiple times safely