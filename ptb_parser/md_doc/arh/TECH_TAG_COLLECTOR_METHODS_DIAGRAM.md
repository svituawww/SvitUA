# TECH Tag Collector - Methods Diagram

## 📋 **Overview**
This document provides a comprehensive diagram of all methods in `ptb_parser/scripts/tech_tag_collector.py`, organized by functionality and showing the relationships between methods.

## 🏗️ **Class Structure**
```
TechHTMLCollector
├── Configuration Methods
├── Bracket Collection Methods
├── Context Enhancement Methods
├── Comment Detection Methods
├── Validation Methods
├── TECH HTML Element Methods
├── File Processing Methods
├── Output Methods
└── Main Execution Methods
```

## 🔧 **Configuration Methods**

### **1. Initialization & Configuration**
```
┌─────────────────────────────────────┐
│ TechHTMLCollector.__init__()       │
│ • Loads config file                │
│ • Initializes collector            │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ load_config()                      │
│ • Reads JSON config file           │
│ • Returns Dict[str, Any]           │
│ • Falls back to default config     │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ get_default_config()               │
│ • Provides default settings        │
│ • Includes all required fields     │
│ • Used as fallback                │
└─────────────────────────────────────┘
```

## 🔍 **Bracket Collection Methods**

### **2. Core Bracket Scanning**
```
┌─────────────────────────────────────┐
│ scan_bytes_for_brackets()          │
│ Input: file_path: str              │
│ Output: List[Dict[str, Any]]      │
│ • Scans file byte-by-byte          │
│ • Collects < and > brackets        │
│ • Returns bracket data with inner_id│
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ enhance_brackets_with_context()    │
│ Input: brackets, content: str      │
│ Output: List[Dict[str, Any]]      │
│ • Adds context data                 │
│ • Detects comment types            │
│ • Marks inner comment content      │
└─────────────────────────────────────┘
```

## 🏷️ **Comment Detection Methods**

### **3. Comment Type Classification**
```
┌─────────────────────────────────────┐
│ detect_comment_type()              │
│ Input: bracket, chars_before,      │
│        chars_after: str            │
│ Output: str                        │
│ • Detects "comm_open"              │
│ • Detects "comm_close"             │
│ • Returns "regular" for others     │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ mark_inner_comment_content()       │
│ Input: brackets_with_data          │
│ Output: List[Dict[str, Any]]      │
│ • Marks brackets between comments  │
│ • Sets type_tech_tag="inner_comm" │
│ • Uses stack-based approach        │
└─────────────────────────────────────┘
```

## ✅ **Validation Methods**

### **4. Comment Validation**
```
┌─────────────────────────────────────┐
│ validate_comment_consistency()     │
│ Input: brackets_with_data          │
│ Output: Dict[str, Any]            │
│ • Validates comment pairing        │
│ • Uses stack-based validation      │
│ • Calculates consistency score     │
└─────────────────────────────────────┘
```

### **5. Bracket Validation**
```
┌─────────────────────────────────────┐
│ validate_bracket_consistency()     │
│ Input: brackets: List[Dict]        │
│ Output: Dict[str, Any]            │
│ • Validates < and > pairing        │
│ • Tracks orphaned brackets         │
│ • Calculates bracket score         │
└─────────────────────────────────────┘
```

### **6. Element Sequence Validation**
```
┌─────────────────────────────────────┐
│ validate_element_sequence()        │
│ Input: list_tech_tech: List[Dict]  │
│ Output: Dict[str, Any]            │
│ • Validates element ordering       │
│ • Checks for gaps/overlaps         │
│ • Uses inner_id fields             │
└─────────────────────────────────────┘
```

### **7. Cross-Validation Analysis**
```
┌─────────────────────────────────────┐
│ perform_cross_validation_analysis()│
│ Input: validation_details: Dict    │
│ Output: Dict[str, float]          │
│ • Calculates correlations          │
│ • Analyzes structure integrity     │
│ • Provides cross-validation metrics│
└─────────────────────────────────────┘
```

### **8. Unified Validation Report**
```
┌─────────────────────────────────────┐
│ create_unified_validation_report() │
│ Input: comment_validation,         │
│        bracket_validation,         │
│        element_sequence_validation │
│ Output: Dict[str, Any]            │
│ • Combines all validation results  │
│ • Calculates overall status        │
│ • Generates comprehensive report   │
└─────────────────────────────────────┘
```

## 🏗️ **TECH HTML Element Methods**

### **9. Element Creation**
```
┌─────────────────────────────────────┐
│ create_tech_tag_html_elements()    │
│ Input: brackets, content: str      │
│ Output: List[Dict[str, Any]]      │
│ • Creates HTML elements            │
│ • Extracts body content            │
│ • Determines element types         │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ create_tech_tag_html_elements_comms()│
│ Input: brackets, content: str      │
│ Output: List[Dict[str, Any]]      │
│ • Creates comment elements          │
│ • Processes regular HTML elements   │
│ • Combines and sorts all elements  │
└─────────────────────────────────────┘
```

### **10. Element Content Extraction**
```
┌─────────────────────────────────────┐
│ extract_body_tech_tag_html()       │
│ Input: content, pos_open, pos_close│
│ Output: str                        │
│ • Extracts content between brackets│
│ • Handles edge cases               │
│ • Returns body content             │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ extract_name_tech_tag_html()       │
│ Input: body_content: str           │
│ Output: str                        │
│ • Extracts element name            │
│ • Handles special cases            │
│ • Returns element name             │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ determine_type_ttag()              │
│ Input: name_tech_tag_html,         │
│        body_content: str           │
│ Output: str                        │
│ • Classifies element types         │
│ • Checks standard tags list        │
│ • Returns type classification      │
└─────────────────────────────────────┘
```

### **11. Comment Body Extraction**
```
┌─────────────────────────────────────┐
│ extract_comment_body()             │
│ Input: content, pos_open, pos_close│
│ Output: str                        │
│ • Extracts comment content         │
│ • Skips <!-- and --> markers      │
│ • Returns comment body text        │
└─────────────────────────────────────┘
```

## 📁 **File Processing Methods**

### **12. Main Processing Pipeline**
```
┌─────────────────────────────────────┐
│ process_all_files_for_brackets()   │
│ Input: None                        │
│ Output: List[Dict[str, Any]]      │
│ • Processes all input files        │
│ • Collects bracket data            │
│ • Saves results to JSON            │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ process_tech_html_elements()       │
│ Input: None                        │
│ Output: List[Dict[str, Any]]      │
│ • Processes TECH HTML elements     │
│ • Creates element data             │
│ • Saves results to JSON            │
└─────────────────────────────────────┘
```

### **13. Comprehensive Validation**
```
┌─────────────────────────────────────┐
│ run_comprehensive_validation()     │
│ Input: file_path: str              │
│ Output: Dict[str, Any]            │
│ • Runs all validation types        │
│ • Creates unified report           │
│ • Saves validation results         │
└─────────────────────────────────────┘
```

## 💾 **Output Methods**

### **14. Data Saving**
```
┌─────────────────────────────────────┐
│ save_bracket_results()             │
│ Input: results: List[Dict]         │
│ Output: None                       │
│ • Saves bracket data to JSON       │
│ • Uses output_database_byte path   │
│ • Handles file writing             │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ save_tech_html_results()           │
│ Input: results: List[Dict]         │
│ Output: None                       │
│ • Saves TECH HTML data to JSON     │
│ • Uses output_database_tech_elements│
│ • Handles file writing             │
└─────────────────────────────────────┘
```

## 🚀 **Main Execution Methods**

### **15. Collection Runners**
```
┌─────────────────────────────────────┐
│ run_bracket_collection()           │
│ • Runs bracket collection          │
│ • Processes all files              │
│ • Saves bracket results            │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ run_tech_html_collection()         │
│ • Runs TECH HTML collection        │
│ • Processes all files              │
│ • Saves element results            │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ run_unified_validation()           │
│ • Runs unified validation          │
│ • Processes all files              │
│ • Saves validation results         │
└─────────────────────────────────────┘
```

### **16. Main Execution**
```
┌─────────────────────────────────────┐
│ run()                              │
│ • Main execution method            │
│ • Orchestrates all processes       │
│ • Runs collection and validation   │
└─────────────────────────────────────┘
```

### **17. Element Processing**
```
┌─────────────────────────────────────┐
│ loop_tech_html_elements()          │
│ • Loops through TECH HTML elements │
│ • Processes each element           │
│ • Generates output files           │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ process_single_tech_html_element() │
│ Input: element, filename, index    │
│ Output: None                       │
│ • Processes single element          │
│ • Generates output content         │
│ • Handles element reconstruction   │
└─────────────────────────────────────┘
```

## 🛠️ **Utility Methods**

### **18. Helper Methods**
```
┌─────────────────────────────────────┐
│ get_current_timestamp()            │
│ Output: str                        │
│ • Returns current timestamp        │
│ • Used for validation reports      │
└─────────────────────────────────────┘
```

## 🔄 **Method Flow Diagram**

### **Complete Processing Flow:**
```
1. __init__() 
   ↓
2. load_config()
   ↓
3. run()
   ├── run_bracket_collection()
   │   ├── process_all_files_for_brackets()
   │   │   ├── scan_bytes_for_brackets()
   │   │   ├── enhance_brackets_with_context()
   │   │   │   ├── detect_comment_type()
   │   │   │   └── mark_inner_comment_content()
   │   │   └── save_bracket_results()
   │   └── run_tech_html_collection()
   │       ├── process_tech_html_elements()
   │       │   ├── create_tech_tag_html_elements_comms()
   │       │   │   ├── extract_comment_body()
   │       │   │   └── create_tech_tag_html_elements()
   │       │   │       ├── extract_body_tech_tag_html()
   │       │   │       ├── extract_name_tech_tag_html()
   │       │   │       └── determine_type_ttag()
   │       │   └── save_tech_html_results()
   │       └── run_unified_validation()
   │           ├── run_comprehensive_validation()
   │           │   ├── validate_comment_consistency()
   │           │   ├── validate_bracket_consistency()
   │           │   ├── validate_element_sequence()
   │           │   ├── create_unified_validation_report()
   │           │   │   └── perform_cross_validation_analysis()
   │           │   └── get_current_timestamp()
   │           └── loop_tech_html_elements()
   │               └── process_single_tech_html_element()
   └── Complete!
```

## 📊 **Method Statistics**

### **Total Methods: 18**
- **Configuration Methods**: 3
- **Bracket Collection Methods**: 2
- **Comment Detection Methods**: 2
- **Validation Methods**: 5
- **TECH HTML Element Methods**: 4
- **File Processing Methods**: 2
- **Output Methods**: 2
- **Main Execution Methods**: 4
- **Utility Methods**: 1

### **Key Features:**
- ✅ **Modular Design**: Methods organized by functionality
- ✅ **Data Flow**: Clear progression from input to output
- ✅ **Validation Pipeline**: Comprehensive validation system
- ✅ **Error Handling**: Robust error handling throughout
- ✅ **Extensibility**: Easy to add new features

## 🎯 **Usage Examples**

### **Basic Usage:**
```python
collector = TechHTMLCollector()
collector.run()  # Runs complete pipeline
```

### **Individual Methods:**
```python
# Bracket collection
brackets = collector.scan_bytes_for_brackets("input/test1.html")
enhanced_brackets = collector.enhance_brackets_with_context(brackets, content)

# TECH HTML element creation
elements = collector.create_tech_tag_html_elements_comms(enhanced_brackets, content)

# Validation
validation = collector.run_comprehensive_validation("input/test1.html")
```

This diagram provides a complete overview of the `TechHTMLCollector` class structure and method relationships! 🚀 