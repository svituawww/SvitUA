<!-- PRESERVE begin id_part1 -->
<!-- PRESERVE improve only this part of instruction. use no more then 150 strings for this part. -->

## Enhanced Symbol Collection with Context Data

### Current Implementation
We have the symbol scanning function:
```python
# Get symbols for this file
symbols = self.scan_bytes_for_symbols(file_path)
```

"context_length_before_after_symbol": 5 - set its value in ptb_parser/json/tech_tag_config.json

### Enhanced Data Structure
Extend the symbol collection to include contextual data by looping through symbols and forming enhanced JSON data:

```json
{
  "symbols_collected_withdata": [
    {
      "id": 1,
      "order": 1,
      "symbol": "<",
      "chars_5_before": "text ",
      "chars_5_after": "html>",
      "pos_in_file": 0,
      "full_context": "text <html>"
    }
  ]
}
```

### Implementation Requirements

context_length_before_after_symbol - further use more shorter name of var 

1. **Context Extraction**:
   - `chars_5_before`: Extract 5 characters before symbol position (from `pos_in_file - context_length_before_after_symbol` to `pos_in_file`)
   - `chars_5_after`: Extract 5 characters after symbol position (from `pos_in_file` to `pos_in_file + context_length_before_after_symbol`)
   - Handle edge cases (beginning/end of file) only with existing in file chars, if it is out to range then not padding

2. **Enhanced Fields**:
   - `context_length_before_after_symbol`: Set to 5 (configurable from tech_tag_config.json)
   - `full_context`: Complete context string combining before + symbol + after

3. **File Output**:
   - Save enhanced data to: `ptb_parser/json/all_opcl_dt_bytes.json`
   - Maintain existing structure while adding `symbols_collected_withdata` array




### Visual Examples

**Example 1 - Opening Tag:**
```
Input:  
        0|1|2|3|4|5|6|7|8|9|0|1|2|3|4|5|6|7
        H|e|l|l|o| |<|h|t|m|l|>| |w|o|r|l|d
                    ^
Symbol: "<" at position 6
Context extraction:
- chars_5_before: positions 1-5 →
         |1|2|3|4|5|
         |H|e|l|l|o|

- chars_5_after: positions 7-11 → 
         |7|8|9|0|1|
         |h|t|m|l|>|

Result: {
  "chars_5_before": "Hello",
  "chars_5_after": "html>",
  "symbol": "<",
  "pos_in_file": 6,
  "full_context": "Hello<html>"
}
```

**Example 2 - Closing Tag:**
```
Input:  
        0|1|2|3|4|5|6|7|8|9|0|1|2|3|4|5|6|7
        <|d|i|v|>|c|o|n|t|e|n|t|<|/|d|i|v|>
            ^
Symbol: ">" at position 4
Context extraction:
- chars_5_before: positions -1-3 →
         |-1|0|1|2|3|
         ||<|d|i|v|

- chars_5_after: positions 5-9 → 
         |5|6|7|8|9|
         |>|c|o|n|t|

Result: {
  "chars_5_before": "<div",
  "chars_5_after": ">cont",
  "symbol": ">",
  "pos_in_file": 4,
  "full_context": "<div>cont"
}
```

**Example 3 - Edge Case (Beginning):**
```
Input:  
        0|1|2|3|4|5|6|7|8|9|0|1|2|3|4|5
        <|!|D|O|C|T|Y|P|E| |h|t|m|l|>|
        ^
Symbol: "<" at position 0
Context extraction:
- chars_5_before: positions -5-(-1) →
       empty or ""

- chars_5_after: positions 1-5 → 
         |1|2|3|4|5|
         |!|D|O|C|T|

Result: {
  "chars_5_before": "     ",
  "chars_5_after": "!DOCT",
  "symbol": "<",
  "pos_in_file": 0,
  "full_context": "     <!DOCT"
}
```



**Example 4 - Edge Case (End of File):**
```
Input:  
        0|1|2|3|4|5|6|7|8|9
        t|e|x|t| |<|b|r|>|
                    ^
Symbol: ">" at position 8
Context extraction:
- chars_5_before: positions 3-7 →
         |3|4|5|6|7|
         |t| |<|b|r|

- chars_5_after: positions 9-13 → 
         |9|
         | |

Array presentation:
input 
  str[0] = "t"
  str[1] = "e"
  str[2] = "x"
  str[3] = "t"
  str[4] = " "
  str[5] = "<"
  str[6] = "b"
  str[7] = "r"
  str[8] = ">"
  str[9] = " "

chars_5_before array: ["t", " ", "<", "b", "r"] (positions 3-7)
chars_5_after array: [" "] (position 9 only, no padding for positions 10-13)

Result: {
  "chars_5_before": "t <br",
  "chars_5_after": " ",
  "symbol": ">",
  "pos_in_file": 8,
  "full_context": "t <br> "
}
```

### Processing Logic
1. Read file content as string
2. For each symbol in `symbols` array:   
   - Calculate context boundaries using `context_length_before_after_symbol`
   - Extract before/after characters
   - Handle edge cases with padding
   - Create enhanced symbol object
3. Save to JSON file with new structure

<!-- PRESERVE end id_part1 -->




<!-- PRESERVE begin id_part2 -->

## Comment Detection and Type Classification

### Context Analysis for Comment Detection

Based on the enhanced symbol data with context, we can detect HTML comments by analyzing the character patterns in `chars_5_before` and `chars_5_after`.

### Comment Opening Detection

**Example - Opening Comment:**
```json
{
  "id": 1,
  "order": 1,
  "symbol": "<",
  "pos_in_file": 0,
  "chars_5_before": "",
  "chars_5_after": "!-- <",
  "full_context": "<!-- <"
}
```

**Detection Logic:**
- `symbol`: "<" (opening symbol)
- `chars_5_after[0]`: "!" 
- `chars_5_after[1]`: "-"
- `chars_5_after[2]`: "-"

**Condition:** If `symbol == "<"` AND `chars_5_after[0:3] == "!--"`, then `type_tech_tag = "comm_open"`

### Comment Closing Detection

**Example - Closing Comment:**
```json
{
  "id": 6,
  "order": 6,
  "symbol": ">",
  "pos_in_file": 103,
  "chars_5_before": "4> --",
  "chars_5_after": "",
  "full_context": "4> -->"
}
```

**Detection Logic:**
- `symbol`: ">" (closing symbol)
- `chars_5_before[3]`: "-"
- `chars_5_before[4]`: "-"

**Condition:** If `symbol == ">"` AND `chars_5_before[-2:] == "--"`, then `type_tech_tag = "comm_close"`

### Implementation Requirements

1. **Enhanced Symbol Processing**:
   - Analyze `chars_5_before` and `chars_5_after` for comment patterns
   - Add `type_tech_tag` field to each symbol
   - Set values: `"comm_open"`, `"comm_close"`, or `"regular"`

2. **Detection Rules**:
   - **Opening Comment**: `symbol == "<"` AND `chars_5_after[0:3] == "!--"`
   - **Closing Comment**: `symbol == ">"` AND `chars_5_before[-2:] == "--"`
   - **Regular Tag**: All other cases

3. **Updated Data Structure**:
```json
{
  "symbols_collected_withdata": [
    {
      "id": 1,
      "order": 1,
      "symbol": "<",
      "pos_in_file": 0,
      "chars_5_before": "",
      "chars_5_after": "!-- <",
      "type_tech_tag": "comm_open",
      "full_context": "<!-- <"
    },
    {
      "id": 6,
      "order": 6,
      "symbol": ">",
      "pos_in_file": 103,
      "chars_5_before": "4> --",
      "chars_5_after": "",
      "type_tech_tag": "comm_close",
      "full_context": "4> -->"
    }
  ]
}
```

### Processing Logic

1. For each symbol in `symbols_collected_withdata`:
   - Check opening comment pattern: `symbol == "<"` AND `chars_5_after[0:3] == "!--"`
   - Check closing comment pattern: `symbol == ">"` AND `chars_5_before[-2:] == "--"`
   - Set `type_tech_tag` accordingly
   - Add the field to the symbol data

2. Save enhanced data with comment type classification


implement this functional in enhance_symbols_with_context

<!-- PRESERVE end id_part2 -->


<!-- PRESERVE begin id_part3 -->

## Comment Type Consistency Validation (id_part3)

### Overview
Validate that comment opening symbols (`type_tech_tag: "comm_open"`) are properly followed by comment closing symbols (`type_tech_tag: "comm_close"`) in the correct sequence and pairing using stack-based validation, analogous to Symbol Consistency Validation but for comment types.

### Implementation Status
- ✅ **Stack-based Validation**: Implement with LIFO approach for comment pairs
- ✅ **Consistency Scoring**: 0.0 to 1.0 scale for comment validation
- ✅ **Orphaned Comment Detection**: Identifies unpaired comment symbols
- ✅ **Validation Status**: PASSED/FAILED determination for comment structure
- ✅ **Error Reporting**: Detailed orphaned comment symbol lists

### Validation Rules

#### **Basic Comment Consistency Check:**
- **Comment opening (`type_tech_tag: "comm_open"`)** must be followed by **comment closing (`type_tech_tag: "comm_close"`)**  
- **Sequential order**: Comment opening at position N, comment closing at position N+1 or later
- **No orphaned comments**: Every `"comm_open"` must have corresponding `"comm_close"`
- **Stack-based pairing**: Use LIFO (Last In, First Out) for proper comment nesting
- **Perfect balance**: Equal number of comment opening and closing symbols

#### **Advanced Comment Validation Algorithm:**
```python
def validate_comment_consistency(self, symbols_with_data: List[Dict]) -> Dict[str, Any]:
    """Validate comment type consistency and pairing using stack-based approach."""
    validation_results = {
        "total_comment_symbols": 0,
        "comment_opening_symbols": 0,
        "comment_closing_symbols": 0,
        "valid_comment_pairs": 0,
        "orphaned_comment_openings": [],
        "orphaned_comment_closings": [],
        "comment_consistency_score": 0.0,
        "comment_validation_status": "PASSED"
    }
    
    comment_opening_stack = []
    
    for i, symbol in enumerate(symbols_with_data):
        if symbol["type_tech_tag"] == "comm_open":
            validation_results["comment_opening_symbols"] += 1
            validation_results["total_comment_symbols"] += 1
            comment_opening_stack.append({
                "id": symbol["id"],
                "pos": symbol["pos_in_file"],
                "index": i
            })
        elif symbol["type_tech_tag"] == "comm_close":
            validation_results["comment_closing_symbols"] += 1
            validation_results["total_comment_symbols"] += 1
            
            if comment_opening_stack:
                # Valid comment pair found - pop the matching opening symbol
                opening = comment_opening_stack.pop()
                validation_results["valid_comment_pairs"] += 1
            else:
                # Orphaned comment closing symbol
                validation_results["orphaned_comment_closings"].append(symbol["id"])
    
    # Check for orphaned comment opening symbols
    for opening in comment_opening_stack:
        validation_results["orphaned_comment_openings"].append(opening["id"])
    
    # Calculate comment consistency score (0.0 to 1.0)
    total_comment_symbols = validation_results["comment_opening_symbols"] + validation_results["comment_closing_symbols"]
    if total_comment_symbols > 0:
        validation_results["comment_consistency_score"] = (validation_results["valid_comment_pairs"] * 2) / total_comment_symbols
    
    # Determine comment validation status
    if (len(validation_results["orphaned_comment_openings"]) == 0 and 
        len(validation_results["orphaned_comment_closings"]) == 0 and
        validation_results["comment_consistency_score"] == 1.0):
        validation_results["comment_validation_status"] = "PASSED"
    else:
        validation_results["comment_validation_status"] = "FAILED"
    
    return validation_results
```

#### **Output Database Structure:**
```json
{
  "inputhtmlfilename": "test1.html",
  "comment_validation": {
    "total_comment_symbols": 2,
    "comment_opening_symbols": 1,
    "comment_closing_symbols": 1,
    "valid_comment_pairs": 1,
    "orphaned_comment_openings": [],
    "orphaned_comment_closings": [],
    "comment_consistency_score": 1.0,
    "comment_validation_status": "PASSED"
  },
  "symbols_collected_withdata": [...]
}
```

#### **Configuration Setup:**
```json
{
  "output_database_comment_validation": "json/comment_validation.json",
  "enable_comment_validation": true
}
```

### Implementation Requirements

1. **Enhanced Validation Method**:
   - Create `validate_comment_consistency()` method
   - Use `type_tech_tag` field instead of `symbol` field
   - Focus on `"comm_open"` and `"comm_close"` types only
   - Ignore `"regular"` type symbols

2. **Comment-Specific Processing**:
   - Filter symbols by `type_tech_tag` for comment validation
   - Maintain separate validation from regular symbol validation
   - Generate comment-specific validation reports

3. **Integration with Existing System**:
   - Add comment validation to `enhance_symbols_with_context()` method
   - Save comment validation results to separate JSON file
   - Maintain backward compatibility with existing symbol validation

### Processing Logic

1. For each symbol in `symbols_collected_withdata`:
   - Check if `type_tech_tag == "comm_open"` → add to opening stack
   - Check if `type_tech_tag == "comm_close"` → try to pair with opening
   - Track orphaned comment symbols
   - Calculate comment consistency score

2. Generate comment validation report with:
   - Comment opening/closing counts
   - Valid comment pairs
   - Orphaned comment symbols
   - Comment consistency score
   - Comment validation status

3. Save comment validation results to dedicated output file

<!-- PRESERVE end id_part3 -->


<!-- PRESERVE begin id_part4 -->

## Inner Comment Content Classification (id_part4)

### Overview
Mark each element in `symbols_collected_withdata` that falls between a `comm_open` and its corresponding `comm_close` as `"type_tech_tag": "inner_comm_content"` to identify all symbols that are part of HTML comment content.

### Comment Content Detection Logic

#### **Basic Rule:**
- Any symbol between `"type_tech_tag": "comm_open"` and its matching `"type_tech_tag": "comm_close"` should be marked as `"type_tech_tag": "inner_comm_content"`
- This includes all symbols that are part of the comment content, not just the opening/closing comment markers

#### **Detection Algorithm:**
```python
def mark_inner_comment_content(self, symbols_with_data: List[Dict]) -> List[Dict]:
    """Mark symbols between comment opening and closing as inner comment content."""
    enhanced_symbols = symbols_with_data.copy()
    comment_stack = []
    
    for i, symbol in enumerate(enhanced_symbols):
        if symbol["type_tech_tag"] == "comm_open":
            # Push comment opening to stack
            comment_stack.append({
                "id": symbol["id"],
                "pos": symbol["pos_in_file"],
                "index": i
            })
        elif symbol["type_tech_tag"] == "comm_close":
            if comment_stack:
                # Found matching comment closing - mark all symbols in between
                opening = comment_stack.pop()
                start_index = opening["index"] + 1
                end_index = i
                
                # Mark all symbols between opening and closing as inner_comm_content
                for j in range(start_index, end_index):
                    if enhanced_symbols[j]["type_tech_tag"] == "regular":
                        enhanced_symbols[j]["type_tech_tag"] = "inner_comm_content"
    
    return enhanced_symbols
```

### Example Data Transformation

#### **Before Processing:**
```json
[
  {
    "id": 1,
    "type_tech_tag": "comm_open",
    "pos_in_file": 0
  },
  {
    "id": 2,
    "type_tech_tag": "regular",
    "pos_in_file": 5
  },
  {
    "id": 3,
    "type_tech_tag": "regular",
    "pos_in_file": 67
  },
  {
    "id": 6,
    "type_tech_tag": "comm_close",
    "pos_in_file": 103
  }
]
```

#### **After Processing:**
```json
[
  {
    "id": 1,
    "type_tech_tag": "comm_open",
    "pos_in_file": 0
  },
  {
    "id": 2,
    "type_tech_tag": "inner_comm_content",
    "pos_in_file": 5
  },
  {
    "id": 3,
    "type_tech_tag": "inner_comm_content",
    "pos_in_file": 67
  },
  {
    "id": 6,
    "type_tech_tag": "comm_close",
    "pos_in_file": 103
  }
]
```

### Implementation Requirements

1. **Enhanced Symbol Processing**:
   - Add `mark_inner_comment_content()` method
   - Process symbols after comment detection but before validation
   - Preserve original `comm_open` and `comm_close` types
   - Convert `regular` symbols to `inner_comm_content` when between comments

2. **Stack-Based Processing**:
   - Use stack to track comment opening positions
   - Mark all symbols between opening and closing comments
   - Handle nested comments correctly (LIFO approach)

3. **Type Classification Hierarchy**:
   - `"comm_open"`: Comment opening symbol
   - `"comm_close"`: Comment closing symbol  
   - `"inner_comm_content"`: Symbols inside comment content
   - `"regular"`: Regular HTML tag symbols (outside comments)

### Processing Logic

1. **Initial Classification**: First classify symbols as `comm_open`, `comm_close`, or `regular`
2. **Content Marking**: Process symbols sequentially:
   - When `comm_open` found → push to stack
   - When `comm_close` found → pop from stack and mark intermediate symbols
   - Mark all `regular` symbols between `comm_open` and `comm_close` as `inner_comm_content`
3. **Final Output**: Enhanced symbols with complete comment content classification

### Integration with Existing System

- Add to `enhance_symbols_with_context()` method after comment detection
- Maintain backward compatibility with existing validation
- Update comment validation to account for `inner_comm_content` symbols
- Preserve all existing fields and functionality

<!-- PRESERVE end id_part4 -->


<!-- PRESERVE beagin id_part5 -->

## Comment Element Processing (id_part5)

### Overview
Create a new method `create_tech_tag_html_elements_comms()` that processes comment elements separately from regular HTML elements, using the same logic as `create_tech_tag_html_elements()` but focused on comment detection and classification.

### Comment Element Detection Strategy

#### **Three-Stage Processing Approach:**

1. **Stage 1: Comment Element Processing**
   - Loop through symbols to find `comm_open` and `comm_close` pairs
   - Create comment elements with `"name_tech_tag_html": "comment"`
   - Track opening and closing positions for proper ordering
   - Extract body content of comment between opening and closing positions

2. **Stage 2: Regular HTML Element Processing**
   - Skip all symbols with `type_tech_tag`: `"comm_open"`, `"inner_comm_content"`, `"comm_close"`
   - Process only `"regular"` type symbols for HTML elements
   - Maintain existing HTML element processing logic

3. **Stage 3: Element Ordering**
   - Consider order in the end using logic or sort after by consistent order
   - Sort by `"pos_open_ttag"` and `"pos_close_ttag"` for proper sequence
   - Maintain chronological order of elements in the document

### Comment Body Extraction

#### **Comment Body Extraction Logic:**
```python
def extract_comment_body(self, content: str, pos_open_ttag: int, pos_close_ttag: int) -> str:
    """Extract comment body content between opening and closing positions."""
    # Extract content between comment opening and closing
    # Skip the opening <!-- and closing --> markers
    start_pos = pos_open_ttag + 4  # Skip "<!--"
    end_pos = pos_close_ttag - 3   # Skip "-->"
    
    if start_pos < end_pos:
        comment_body = content[start_pos:end_pos].strip()
        return comment_body
    else:
        return ""
```

#### **Comment Body Examples:**
```html
<!-- This is a comment -->
<!-- 
  Multi-line comment
  with formatting 
-->
<!-- Comment with special chars: <div>test</div> -->
```

**Extracted Comment Bodies:**
- `"This is a comment"`
- `"Multi-line comment with formatting"`
- `"Comment with special chars: <div>test</div>"`

### New Method Implementation

#### **Comment Element Processing Method:**
```python
def create_tech_tag_html_elements_comms(self, symbols: List[Dict[str, Any]], content: str) -> List[Dict[str, Any]]:
    """Create comment elements from symbols using TECH_HTML terminology."""
    comment_elements = []
    element_counter = 1
    
    # Stage 1: Process comment elements
    comment_stack = []
    
    for i, symbol in enumerate(symbols):
        if symbol["type_tech_tag"] == "comm_open":
            # Push comment opening to stack
            comment_stack.append({
                "id": symbol["id"],
                "pos": symbol["pos_in_file"],
                "index": i
            })
        elif symbol["type_tech_tag"] == "comm_close":
            if comment_stack:
                # Found matching comment closing - create comment element
                opening = comment_stack.pop()
                pos_open_ttag = opening["pos"]
                pos_close_ttag = symbol["pos_in_file"]
                
                # Extract comment body
                comment_body = self.extract_comment_body(content, pos_open_ttag, pos_close_ttag)
                
                # Create comment element
                comment_element = {
                    "id": element_counter,
                    "pos_open_ttag": pos_open_ttag,
                    "pos_close_ttag": pos_close_ttag,
                    "type_ttag": "unnamed",
                    "name_tech_tag_html": "comment",
                    "body_tech_tag_html": comment_body
                }
                
                comment_elements.append(comment_element)
                element_counter += 1
    
    # Stage 2: Process regular HTML elements (skip comment-related symbols)
    regular_symbols = [s for s in symbols if s["type_tech_tag"] == "regular"]
    html_elements = self.create_tech_tag_html_elements(regular_symbols, content)
    
    # Stage 3: Combine and sort all elements by position
    all_elements = comment_elements + html_elements
    
    # Sort elements by pos_open_ttag for consistent chronological order
    all_elements.sort(key=lambda x: x.get("pos_open_ttag", 0))
    
    return all_elements
```

### Comment Element Structure

#### **Comment Element Example with Body:**
```json
{
  "id": 1,
  "pos_open_ttag": 0,
  "pos_close_ttag": 103,
  "type_ttag": "unnamed",
  "name_tech_tag_html": "comment",
  "body_tech_tag_html": "This is a comment with content"
}
```

### Implementation Requirements

1. **New Method Creation**:
   - Create `create_tech_tag_html_elements_comms()` method
   - Add `extract_comment_body()` method for comment content extraction
   - Use same logic as `create_tech_tag_html_elements()` but for comments
   - Preserve existing `create_tech_tag_html_elements()` method unchanged

2. **Three-Stage Processing**:
   - **Stage 1**: Process comment opening/closing pairs with body extraction
   - **Stage 2**: Process regular HTML elements (skip comment symbols)
   - **Stage 3**: Combine and sort elements by position

3. **Comment Element Features**:
   - `"name_tech_tag_html": "comment"` for all comment elements
   - `"type_ttag": "unnamed"` for comment classification
   - `"body_tech_tag_html"` containing extracted comment content
   - Track opening and closing positions for proper ordering
   - Maintain position tracking for opening and closing symbols

4. **Comment Body Extraction**:
   - Extract content between `<!--` and `-->` markers
   - Skip opening and closing comment markers
   - Handle multi-line comments with proper formatting
   - Preserve special characters and HTML within comments
   - Return empty string for malformed comments

5. **Symbol Filtering**:
   - Skip `"type_tech_tag": "comm_open"` symbols in HTML processing
   - Skip `"type_tech_tag": "inner_comm_content"` symbols in HTML processing
   - Skip `"type_tech_tag": "comm_close"` symbols in HTML processing
   - Process only `"type_tech_tag": "regular"` symbols for HTML elements

6. **Element Ordering**:
   - Sort all elements by `"pos_open_ttag"` for chronological order
   - Maintain consistent ordering across different element types
   - Ensure proper sequence in final output

### Processing Logic

1. **Comment Detection Stage**:
   - Loop through all symbols sequentially
   - Track comment opening symbols in stack
   - When comment closing found, create comment element
   - Extract comment body content between positions
   - Record opening and closing positions

2. **HTML Element Stage**:
   - Filter symbols to include only `"regular"` type
   - Use existing `create_tech_tag_html_elements()` method
   - Skip all comment-related symbols

3. **Combination and Ordering Stage**:
   - Combine comment elements with HTML elements
   - Sort all elements by `pos_open_ttag` for chronological order
   - Return properly ordered list of all elements

### Integration with Existing System

- Add new method alongside existing `create_tech_tag_html_elements()`
- Add `extract_comment_body()` method for comment content extraction
- Preserve existing HTML element processing logic
- Maintain backward compatibility
- Use existing helper methods where appropriate
- Ensure proper element ordering in final output

<!-- PRESERVE end id_part5 -->



<!-- PRESERVE begin id_part6 -->

## Element Sequence Validation (id_part6)

### Overview
Validate that HTML elements in `tech_tag_html_collected` (abbreviated as `list_tech_tech`) are properly sequenced without gaps or overlaps in their position ranges. This ensures that elements are correctly ordered and positioned in the document structure.

### Sequential Element Validation Logic

#### **Validation Rule:**
For each consecutive pair of elements in `list_tech_tech`, the closing position of the current element must be immediately followed by the opening position of the next element.


**Mathematical Formula:**
```
current_elem_tech_tag["id_open_ttag"] + 1 = next_elem_tech_tag["id_close_ttag"]
```

#### **Validation Algorithm:**
```python
def validate_element_sequence(self, list_tech_tech: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate that elements are properly sequenced without gaps or overlaps."""
    validation_results = {
        "total_elements": len(list_tech_tech),
        "validated_pairs": 0,
        "sequence_errors": [],
        "sequence_validation_status": "PASSED",
        "sequence_consistency_score": 0.0
    }
    
    for i in range(len(list_tech_tech) - 1):
        current_elem = list_tech_tech[i]
        next_elem = list_tech_tech[i + 1]
        
        # Check if current element closes exactly before next element opens
        expected_next_open = current_elem["id_close_ttag"] + 1
        actual_next_open = next_elem["id_open_ttag"]
        
        if expected_next_open != actual_next_open:
            error_info = {
                "pair_index": i,
                "current_element_id": current_elem["id"],
                "next_element_id": next_elem["id"],
                "current_id_close": current_elem["id_close_ttag"],
                "expected_next_id_open": expected_next_open,
                "actual_next_id_open": actual_next_open,
                "gap_or_overlap": actual_next_open - expected_next_open
            }
            validation_results["sequence_errors"].append(error_info)
        else:
            validation_results["validated_pairs"] += 1
    
    # Calculate consistency score
    total_pairs = len(list_tech_tech) - 1
    if total_pairs > 0:
        validation_results["sequence_consistency_score"] = validation_results["validated_pairs"] / total_pairs
    
    # Determine validation status
    if len(validation_results["sequence_errors"]) == 0:
        validation_results["sequence_validation_status"] = "PASSED"
    else:
        validation_results["sequence_validation_status"] = "FAILED"
    
    return validation_results
```

### Validation Examples

#### **Example 1: Valid Sequence**
```json
[
  {
    "id": 1,
    "id_open_ttag": 1,
    "id_close_ttag": 2,
    "name_tech_tag_html": "html"
  },
  {
    "id": 2,
    "id_open_ttag": 3,
    "id_close_ttag": 4,
    "name_tech_tag_html": "head"
  },
  {
    "id": 3,
    "id_open_ttag": 5,
    "id_close_ttag": 6,
    "name_tech_tag_html": "body"
  }
]
```

**Validation Results:**
- Pair 0-1: 2 + 1 = 3 ✓ (PASSED)
- Pair 1-2: 4 + 1 = 5 ✓ (PASSED)
- **Overall Status: PASSED**

#### **Example 2: Invalid Sequence with Gap**
```json
[
  {
    "id": 1,
    "id_open_ttag": 1,
    "id_close_ttag": 2,
    "name_tech_tag_html": "html"
  },
  {
    "id": 2,
    "id_open_ttag": 5,
    "id_close_ttag": 6,
    "name_tech_tag_html": "head"
  }
]
```

**Validation Results:**
- Pair 0-1: 2 + 1 = 3 ≠ 5 ✗ (FAILED - Gap of 2 ID positions)
- **Overall Status: FAILED**

#### **Example 3: Invalid Sequence with Overlap**
```json
[
  {
    "id": 1,
    "id_open_ttag": 1,
    "id_close_ttag": 4,
    "name_tech_tag_html": "html"
  },
  {
    "id": 2,
    "id_open_ttag": 3,
    "id_close_ttag": 6,
    "name_tech_tag_html": "head"
  }
]
```

**Validation Results:**
- Pair 0-1: 4 + 1 = 5 ≠ 3 ✗ (FAILED - Overlap of 2 ID positions)
- **Overall Status: FAILED**

### Error Reporting Structure

#### **Sequence Error Details:**
```json
{
  "sequence_errors": [
    {
      "pair_index": 0,
      "current_element_id": 1,
      "next_element_id": 2,
      "current_id_close": 2,
      "expected_next_id_open": 3,
      "actual_next_id_open": 5,
      "gap_or_overlap": 2
    }
  ]
}
```

#### **Validation Output Structure:**
```json
{
  "element_sequence_validation": {
    "total_elements": 3,
    "validated_pairs": 1,
    "sequence_errors": [...],
    "sequence_validation_status": "FAILED",
    "sequence_consistency_score": 0.5
  }
}
```

### Implementation Requirements

1. **Validation Method Creation**:
   - Create `validate_element_sequence()` method
   - Process consecutive element pairs in `list_tech_tech`
   - Check position continuity between elements
   - Generate detailed error reports for gaps/overlaps

2. **ID Validation Logic**:
   - Verify `current_elem["id_close_ttag"] + 1 = next_elem["id_open_ttag"]`
   - Handle edge cases (single element, empty list)
   - Calculate gap/overlap values for error reporting
   - Track validation statistics

3. **Error Classification**:
   - **Gap**: When `actual_next_pos_open > expected_next_pos_open`
   - **Overlap**: When `actual_next_pos_open < expected_next_pos_open`
   - **Perfect Sequence**: When `actual_next_pos_open = expected_next_pos_open`

4. **Integration Requirements**:
   - Add to existing validation pipeline
   - Save results to dedicated JSON file
   - Maintain consistency with other validation methods
   - Provide detailed error reporting for debugging

### Processing Logic

1. **Element Pair Processing**:
   - Loop through `list_tech_tech` with index `i`
   - Compare element `i` with element `i + 1`
   - Calculate expected vs actual positions
   - Record validation results

2. **Error Detection**:
   - Identify gaps (missing content between elements)
   - Identify overlaps (elements sharing positions)
   - Calculate exact gap/overlap values
   - Generate detailed error information

3. **Score Calculation**:
   - Count valid pairs vs total pairs
   - Calculate consistency score (0.0 to 1.0)
   - Determine overall validation status

### Configuration Setup

#### **Configuration Options:**
```json
{
  "enable_element_sequence_validation": true,
  "output_database_element_sequence_validation": "json/element_sequence_validation.json",
  "sequence_validation_tolerance": 0
}
```

### Use Cases

1. **Document Structure Validation**: Ensure HTML elements are properly ordered
2. **Parser Accuracy Verification**: Validate that element extraction is complete
3. **Content Integrity Check**: Detect missing or overlapping content sections
4. **Debugging Aid**: Identify specific position mismatches in element extraction

## Unified Validation System Integration

### Overview
Refactor all validation processes into a unified JSON validation system that consolidates results from multiple validation types into a single comprehensive validation report.

### Validation Sources Consolidation

#### **Current Validation Sources:**
- `ptb_parser/json/comment_validation.json` - Comment type consistency validation
- `ptb_parser/json/symbol_validation.json` - Symbol consistency validation  
- `ptb_parser/json/element_sequence_validation.json` - Element sequence validation

#### **Unified Validation Structure:**
```json
{
  "inputhtmlfilename": "test1.html",
  "validation_timestamp": "2025-01-30T10:30:00Z",
  "overall_validation_status": "PASSED",
  "overall_validation_score": 0.95,
  "validation_summary": {
    "total_validation_types": 3,
    "passed_validations": 3,
    "failed_validations": 0,
    "validation_coverage": 1.0
  },
  "validation_details": {
    "comment_validation": {
      "total_comment_symbols": 2,
      "comment_opening_symbols": 1,
      "comment_closing_symbols": 1,
      "valid_comment_pairs": 1,
      "orphaned_comment_openings": [],
      "orphaned_comment_closings": [],
      "comment_consistency_score": 1.0,
      "comment_validation_status": "PASSED"
    },
    "symbol_validation": {
      "total_symbols": 15,
      "opening_symbols": 8,
      "closing_symbols": 7,
      "valid_pairs": 7,
      "orphaned_openings": [],
      "orphaned_closings": [],
      "symbol_consistency_score": 0.93,
      "symbol_validation_status": "PASSED"
    },
    "element_sequence_validation": {
      "total_elements": 10,
      "validated_pairs": 9,
      "sequence_errors": [],
      "sequence_validation_status": "PASSED",
      "sequence_consistency_score": 1.0
    }
  },
  "cross_validation_analysis": {
    "symbol_comment_correlation": 0.98,
    "element_symbol_alignment": 0.95,
    "overall_structure_integrity": 0.96
  }
}
```

### Unified Validation Method

#### **Consolidation Algorithm:**
```python
def create_unified_validation_report(self, 
                                   comment_validation: Dict[str, Any],
                                   symbol_validation: Dict[str, Any], 
                                   element_sequence_validation: Dict[str, Any]) -> Dict[str, Any]:
    """Create unified validation report combining all validation types."""
    
    # Collect all validation results
    validation_details = {
        "comment_validation": comment_validation,
        "symbol_validation": symbol_validation,
        "element_sequence_validation": element_sequence_validation
    }
    
    # Calculate overall validation status
    validation_statuses = [
        comment_validation.get("comment_validation_status", "UNKNOWN"),
        symbol_validation.get("symbol_validation_status", "UNKNOWN"),
        element_sequence_validation.get("sequence_validation_status", "UNKNOWN")
    ]
    
    overall_status = "PASSED" if all(status == "PASSED" for status in validation_statuses) else "FAILED"
    
    # Calculate overall validation score
    scores = [
        comment_validation.get("comment_consistency_score", 0.0),
        symbol_validation.get("symbol_consistency_score", 0.0),
        element_sequence_validation.get("sequence_consistency_score", 0.0)
    ]
    overall_score = sum(scores) / len(scores) if scores else 0.0
    
    # Generate validation summary
    passed_count = sum(1 for status in validation_statuses if status == "PASSED")
    total_count = len(validation_statuses)
    
    # Cross-validation analysis
    cross_analysis = self.perform_cross_validation_analysis(validation_details)
    
    unified_report = {
        "inputhtmlfilename": self.current_filename,
        "validation_timestamp": datetime.now().isoformat(),
        "overall_validation_status": overall_status,
        "overall_validation_score": overall_score,
        "validation_summary": {
            "total_validation_types": total_count,
            "passed_validations": passed_count,
            "failed_validations": total_count - passed_count,
            "validation_coverage": passed_count / total_count if total_count > 0 else 0.0
        },
        "validation_details": validation_details,
        "cross_validation_analysis": cross_analysis
    }
    
    return unified_report
```

### Cross-Validation Analysis

#### **Correlation Analysis Method:**
```python
def perform_cross_validation_analysis(self, validation_details: Dict[str, Any]) -> Dict[str, float]:
    """Perform cross-validation analysis between different validation types."""
    
    comment_val = validation_details["comment_validation"]
    symbol_val = validation_details["symbol_validation"]
    element_val = validation_details["element_sequence_validation"]
    
    # Calculate symbol-comment correlation
    comment_symbols = comment_val.get("total_comment_symbols", 0)
    total_symbols = symbol_val.get("total_symbols", 0)
    symbol_comment_correlation = comment_symbols / total_symbols if total_symbols > 0 else 0.0
    
    # Calculate element-symbol alignment
    element_count = element_val.get("total_elements", 0)
    symbol_pairs = symbol_val.get("valid_pairs", 0)
    element_symbol_alignment = symbol_pairs / element_count if element_count > 0 else 0.0
    
    # Calculate overall structure integrity
    structure_scores = [
        comment_val.get("comment_consistency_score", 0.0),
        symbol_val.get("symbol_consistency_score", 0.0),
        element_val.get("sequence_consistency_score", 0.0)
    ]
    overall_structure_integrity = sum(structure_scores) / len(structure_scores)
    
    return {
        "symbol_comment_correlation": symbol_comment_correlation,
        "element_symbol_alignment": element_symbol_alignment,
        "overall_structure_integrity": overall_structure_integrity
    }
```

### Implementation Requirements

#### **1. Unified Validation Pipeline:**
```python
def run_comprehensive_validation(self, file_path: str) -> Dict[str, Any]:
    """Run all validation types and create unified report."""
    
    # Run individual validations
    comment_validation = self.validate_comment_consistency(symbols_with_data)
    symbol_validation = self.validate_symbol_consistency(symbols)
    element_sequence_validation = self.validate_element_sequence(list_tech_tech)
    
    # Create unified report
    unified_report = self.create_unified_validation_report(
        comment_validation, symbol_validation, element_sequence_validation
    )
    
    # Save unified validation report
    output_path = "ptb_parser/json/unified_validation.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unified_report, f, indent=2, ensure_ascii=False)
    
    return unified_report
```

#### **2. Configuration Updates:**
```json
{
  "unified_validation": {
    "enabled": true,
    "output_file": "ptb_parser/json/unified_validation.json",
    "include_cross_validation": true,
    "validation_types": [
      "comment_validation",
      "symbol_validation", 
      "element_sequence_validation"
    ]
  }
}
```

#### **3. Validation Type Integration:**
- **Comment Validation**: Comment type consistency and pairing
- **Symbol Validation**: Symbol opening/closing consistency
- **Element Sequence Validation**: Element position continuity
- **Cross-Validation**: Correlation analysis between validation types

### Benefits of Unified System

1. **Comprehensive Overview**: Single report with all validation results
2. **Cross-Validation Insights**: Correlation analysis between validation types
3. **Simplified Management**: One output file instead of multiple
4. **Better Debugging**: Centralized validation information
5. **Performance Tracking**: Overall validation scores and trends
6. **Consistency Assurance**: Coordinated validation across all types

### Migration Strategy

#### **Phase 1: Maintain Individual Files**
- Keep existing individual validation files for backward compatibility
- Add unified validation alongside existing system

#### **Phase 2: Gradual Migration**
- Update existing code to use unified validation
- Deprecate individual validation files
- Maintain migration path for existing integrations

#### **Phase 3: Full Integration**
- Remove individual validation file generation
- Use unified validation as primary output
- Update all dependent systems to use unified format

<!-- PRESERVE end id_part6 -->