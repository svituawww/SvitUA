# Database Design: Python + SQLite for HTML Parser

## Overview

This document outlines a comprehensive database design using Python and SQLite for the HTML parser project, eliminating the need for traditional RDBMS while maintaining full SQL capabilities.

## 🎯 **Recommended Technology Stack**

### **Core Technologies:**
- **Python 3.11+** - Primary language
- **SQLite 3** - Embedded database
- **sqlite3** - Python's built-in SQLite module
- **pandas** - Data manipulation (optional)
- **sqlalchemy** - ORM (optional, for complex queries)

### **Why This Stack:**
- ✅ **Zero Dependencies** - No external database server
- ✅ **Portable** - Single `.db` file
- ✅ **Version Control Friendly** - Database file can be tracked
- ✅ **Full SQL Support** - All standard SQL operations
- ✅ **ACID Compliant** - Reliable transactions
- ✅ **Python Native** - Built-in `sqlite3` module

## 📊 **Database Schema Design**

### **1. Files Table**
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    encoding VARCHAR(50) DEFAULT 'utf-8',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processed',
    UNIQUE(filename, file_path)
);
```

### **2. Symbols Table**
```sql
CREATE TABLE symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    symbol_order INTEGER NOT NULL,
    symbol_type VARCHAR(10) NOT NULL, -- '<' or '>'
    position INTEGER NOT NULL,
    chars_before TEXT,
    chars_after TEXT,
    full_context TEXT,
    type_tech_tag VARCHAR(50) DEFAULT 'regular', -- 'comm_open', 'comm_close', 'inner_comm_content', 'regular'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id),
    UNIQUE(file_id, symbol_order)
);
```

### **3. HTML Elements Table**
```sql
CREATE TABLE html_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    element_order INTEGER NOT NULL,
    pos_open_ttag INTEGER NOT NULL,
    pos_close_ttag INTEGER NOT NULL,
    type_ttag VARCHAR(50) DEFAULT 'unnamed', -- 'standard_named', 'custom', 'unnamed'
    name_tech_tag_html VARCHAR(100),
    body_tech_tag_html TEXT,
    is_comment BOOLEAN DEFAULT FALSE,
    comment_body TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id),
    UNIQUE(file_id, element_order)
);
```

### **4. Validation Results Table**
```sql
CREATE TABLE validation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    validation_type VARCHAR(50) NOT NULL, -- 'comment', 'symbol', 'element_sequence', 'unified'
    validation_status VARCHAR(20) NOT NULL, -- 'PASSED', 'FAILED'
    validation_score DECIMAL(3,2) DEFAULT 0.00,
    total_items INTEGER DEFAULT 0,
    valid_items INTEGER DEFAULT 0,
    invalid_items INTEGER DEFAULT 0,
    error_details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id),
    UNIQUE(file_id, validation_type)
);
```

### **5. Validation Errors Table**
```sql
CREATE TABLE validation_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    validation_result_id INTEGER NOT NULL,
    error_type VARCHAR(50) NOT NULL,
    error_message TEXT,
    error_position INTEGER,
    error_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (validation_result_id) REFERENCES validation_results(id)
);
```

## 🐍 **Python Implementation**

### **1. Database Manager Class**
```python
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class HTMLParserDatabase:
    def __init__(self, db_path: str = "html_parser.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    encoding VARCHAR(50) DEFAULT 'utf-8',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'processed',
                    UNIQUE(filename, file_path)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    symbol_order INTEGER NOT NULL,
                    symbol_type VARCHAR(10) NOT NULL,
                    position INTEGER NOT NULL,
                    chars_before TEXT,
                    chars_after TEXT,
                    full_context TEXT,
                    type_tech_tag VARCHAR(50) DEFAULT 'regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, symbol_order)
                )
            """)
            
            # Add other tables...
            conn.commit()
    
    def add_file(self, filename: str, file_path: str, file_size: int = None) -> int:
        """Add a file to the database and return file_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO files (filename, file_path, file_size)
                VALUES (?, ?, ?)
            """, (filename, file_path, file_size))
            return cursor.lastrowid
    
    def add_symbols(self, file_id: int, symbols: List[Dict[str, Any]]):
        """Add symbols for a file."""
        with sqlite3.connect(self.db_path) as conn:
            for symbol in symbols:
                conn.execute("""
                    INSERT OR REPLACE INTO symbols 
                    (file_id, symbol_order, symbol_type, position, chars_before, 
                     chars_after, full_context, type_tech_tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    symbol.get('order', 0),
                    symbol.get('symbol', ''),
                    symbol.get('pos_in_file', 0),
                    symbol.get('chars_5_before', ''),
                    symbol.get('chars_5_after', ''),
                    symbol.get('full_context', ''),
                    symbol.get('type_tech_tag', 'regular')
                ))
            conn.commit()
    
    def add_html_elements(self, file_id: int, elements: List[Dict[str, Any]]):
        """Add HTML elements for a file."""
        with sqlite3.connect(self.db_path) as conn:
            for element in elements:
                conn.execute("""
                    INSERT OR REPLACE INTO html_elements 
                    (file_id, element_order, pos_open_ttag, pos_close_ttag,
                     type_ttag, name_tech_tag_html, body_tech_tag_html,
                     is_comment, comment_body)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    element.get('id', 0),
                    element.get('pos_open_ttag', 0),
                    element.get('pos_close_ttag', 0),
                    element.get('type_ttag', 'unnamed'),
                    element.get('name_tech_tag_html', ''),
                    element.get('body_tech_tag_html', ''),
                    element.get('name_tech_tag_html') == 'comment',
                    element.get('body_tech_tag_html', '')
                ))
            conn.commit()
    
    def add_validation_result(self, file_id: int, validation_type: str, 
                            validation_data: Dict[str, Any]):
        """Add validation results for a file."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO validation_results 
                (file_id, validation_type, validation_status, validation_score,
                 total_items, valid_items, invalid_items, error_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                validation_type,
                validation_data.get('status', 'UNKNOWN'),
                validation_data.get('score', 0.0),
                validation_data.get('total_items', 0),
                validation_data.get('valid_items', 0),
                validation_data.get('invalid_items', 0),
                json.dumps(validation_data.get('errors', []))
            ))
            conn.commit()
    
    def get_file_statistics(self, file_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a file."""
        with sqlite3.connect(self.db_path) as conn:
            # File info
            file_info = conn.execute("""
                SELECT * FROM files WHERE id = ?
            """, (file_id,)).fetchone()
            
            # Symbol counts
            symbol_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_symbols,
                    SUM(CASE WHEN symbol_type = '<' THEN 1 ELSE 0 END) as opening_symbols,
                    SUM(CASE WHEN symbol_type = '>' THEN 1 ELSE 0 END) as closing_symbols,
                    SUM(CASE WHEN type_tech_tag = 'comm_open' THEN 1 ELSE 0 END) as comment_openings,
                    SUM(CASE WHEN type_tech_tag = 'comm_close' THEN 1 ELSE 0 END) as comment_closings
                FROM symbols WHERE file_id = ?
            """, (file_id,)).fetchone()
            
            # Element counts
            element_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_elements,
                    SUM(CASE WHEN type_ttag = 'standard_named' THEN 1 ELSE 0 END) as standard_elements,
                    SUM(CASE WHEN type_ttag = 'custom' THEN 1 ELSE 0 END) as custom_elements,
                    SUM(CASE WHEN type_ttag = 'unnamed' THEN 1 ELSE 0 END) as unnamed_elements,
                    SUM(CASE WHEN is_comment = 1 THEN 1 ELSE 0 END) as comment_elements
                FROM html_elements WHERE file_id = ?
            """, (file_id,)).fetchone()
            
            # Validation results
            validation_results = conn.execute("""
                SELECT validation_type, validation_status, validation_score
                FROM validation_results WHERE file_id = ?
            """, (file_id,)).fetchall()
            
            return {
                'file_info': dict(zip([col[0] for col in conn.description], file_info)) if file_info else {},
                'symbol_stats': dict(zip([col[0] for col in conn.description], symbol_stats)) if symbol_stats else {},
                'element_stats': dict(zip([col[0] for col in conn.description], element_stats)) if element_stats else {},
                'validation_results': [dict(zip(['validation_type', 'validation_status', 'validation_score'], row)) 
                                     for row in validation_results]
            }
    
    def get_all_files_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all processed files."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("""
                SELECT 
                    f.id, f.filename, f.file_size, f.status, f.created_at,
                    COUNT(s.id) as symbol_count,
                    COUNT(h.id) as element_count,
                    COUNT(v.id) as validation_count
                FROM files f
                LEFT JOIN symbols s ON f.id = s.file_id
                LEFT JOIN html_elements h ON f.id = h.file_id
                LEFT JOIN validation_results v ON f.id = v.file_id
                GROUP BY f.id
                ORDER BY f.created_at DESC
            """).fetchall()
```

### **2. Integration with Existing Parser**
```python
class TechHTMLCollectorWithDB(TechHTMLCollector):
    def __init__(self, config_file: str = "json/tech_tag_config.json", 
                 db_path: str = "html_parser.db"):
        super().__init__(config_file)
        self.db = HTMLParserDatabase(db_path)
    
    def process_file_with_database(self, file_path: str):
        """Process a file and store results in database."""
        # Add file to database
        file_size = Path(file_path).stat().st_size
        file_id = self.db.add_file(Path(file_path).name, file_path, file_size)
        
        # Process symbols
        symbols = self.scan_bytes_for_symbols(file_path)
        enhanced_symbols = self.enhance_symbols_with_context(symbols, self.read_file_content(file_path))
        self.db.add_symbols(file_id, enhanced_symbols)
        
        # Process HTML elements
        html_elements = self.create_tech_tag_html_elements_comms(enhanced_symbols, self.read_file_content(file_path))
        self.db.add_html_elements(file_id, html_elements)
        
        # Run validations
        validation_results = self.run_comprehensive_validation(file_path)
        for validation_type, result in validation_results['validation_details'].items():
            self.db.add_validation_result(file_id, validation_type, result)
        
        return file_id
    
    def read_file_content(self, file_path: str) -> str:
        """Read file content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
```

## 📈 **Advanced Queries**

### **1. Comment Analysis**
```sql
-- Find all comment elements with their content
SELECT 
    f.filename,
    h.element_order,
    h.comment_body,
    h.pos_open_ttag,
    h.pos_close_ttag
FROM html_elements h
JOIN files f ON h.file_id = f.id
WHERE h.is_comment = 1
ORDER BY f.filename, h.element_order;
```

### **2. Validation Statistics**
```sql
-- Get validation success rates across all files
SELECT 
    validation_type,
    COUNT(*) as total_files,
    SUM(CASE WHEN validation_status = 'PASSED' THEN 1 ELSE 0 END) as passed_files,
    AVG(validation_score) as avg_score
FROM validation_results
GROUP BY validation_type;
```

### **3. Symbol Distribution Analysis**
```sql
-- Analyze symbol distribution by file
SELECT 
    f.filename,
    COUNT(*) as total_symbols,
    SUM(CASE WHEN s.type_tech_tag = 'comm_open' THEN 1 ELSE 0 END) as comment_openings,
    SUM(CASE WHEN s.type_tech_tag = 'comm_close' THEN 1 ELSE 0 END) as comment_closings,
    SUM(CASE WHEN s.type_tech_tag = 'regular' THEN 1 ELSE 0 END) as regular_symbols
FROM symbols s
JOIN files f ON s.file_id = f.id
GROUP BY f.id, f.filename
ORDER BY total_symbols DESC;
```

## 🔧 **Performance Optimizations**

### **1. Indexes for Better Performance**
```sql
-- Create indexes for common queries
CREATE INDEX idx_symbols_file_id ON symbols(file_id);
CREATE INDEX idx_symbols_type ON symbols(type_tech_tag);
CREATE INDEX idx_elements_file_id ON html_elements(file_id);
CREATE INDEX idx_elements_type ON html_elements(type_ttag);
CREATE INDEX idx_validation_file_id ON validation_results(file_id);
CREATE INDEX idx_validation_type ON validation_results(validation_type);
```

### **2. Batch Operations**
```python
def batch_insert_symbols(self, file_id: int, symbols: List[Dict[str, Any]]):
    """Batch insert symbols for better performance."""
    with sqlite3.connect(self.db_path) as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO symbols 
            (file_id, symbol_order, symbol_type, position, chars_before, 
             chars_after, full_context, type_tech_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(
            file_id,
            symbol.get('order', 0),
            symbol.get('symbol', ''),
            symbol.get('pos_in_file', 0),
            symbol.get('chars_5_before', ''),
            symbol.get('chars_5_after', ''),
            symbol.get('full_context', ''),
            symbol.get('type_tech_tag', 'regular')
        ) for symbol in symbols])
        conn.commit()
```

## 📊 **Data Export/Import**

### **1. Export to JSON**
```python
def export_file_data(self, file_id: int) -> Dict[str, Any]:
    """Export all data for a file to JSON format."""
    stats = self.get_file_statistics(file_id)
    
    with sqlite3.connect(self.db_path) as conn:
        symbols = conn.execute("""
            SELECT * FROM symbols WHERE file_id = ? ORDER BY symbol_order
        """, (file_id,)).fetchall()
        
        elements = conn.execute("""
            SELECT * FROM html_elements WHERE file_id = ? ORDER BY element_order
        """, (file_id,)).fetchall()
        
        validations = conn.execute("""
            SELECT * FROM validation_results WHERE file_id = ?
        """, (file_id,)).fetchall()
    
    return {
        'file_info': stats['file_info'],
        'statistics': {
            'symbols': stats['symbol_stats'],
            'elements': stats['element_stats'],
            'validations': stats['validation_results']
        },
        'symbols': [dict(zip([col[0] for col in conn.description], row)) for row in symbols],
        'elements': [dict(zip([col[0] for col in conn.description], row)) for row in elements],
        'validations': [dict(zip([col[0] for col in conn.description], row)) for row in validations]
    }
```

### **2. Import from JSON**
```python
def import_file_data(self, data: Dict[str, Any]) -> int:
    """Import file data from JSON format."""
    file_id = self.add_file(
        data['file_info']['filename'],
        data['file_info']['file_path'],
        data['file_info']['file_size']
    )
    
    if 'symbols' in data:
        self.db.add_symbols(file_id, data['symbols'])
    
    if 'elements' in data:
        self.db.add_html_elements(file_id, data['elements'])
    
    if 'validations' in data:
        for validation in data['validations']:
            self.db.add_validation_result(file_id, validation['validation_type'], validation)
    
    return file_id
```

## 🎯 **Benefits of This Approach**

### **✅ Advantages:**
1. **No Server Setup** - Zero configuration required
2. **Portable** - Single `.db` file, easy to backup
3. **Full SQL Support** - All standard SQL operations
4. **ACID Compliant** - Reliable transactions
5. **Python Native** - Built-in support
6. **Version Control Friendly** - Database file can be tracked
7. **Lightweight** - Minimal resource usage
8. **Cross-Platform** - Works on any OS

### **✅ Perfect for Your Use Case:**
- **HTML Parsing Data** - Store symbols, elements, validation results
- **Analysis & Reporting** - Complex SQL queries for insights
- **Data Persistence** - Reliable storage without external dependencies
- **Scalability** - Can handle thousands of files efficiently
- **Integration** - Easy to integrate with existing Python code

## 🚀 **Implementation Steps**

1. **Install Dependencies** (if needed):
   ```bash
   pip install pandas  # Optional, for data analysis
   ```

2. **Create Database Manager**:
   ```python
   db = HTMLParserDatabase("html_parser.db")
   ```

3. **Integrate with Parser**:
   ```python
   collector = TechHTMLCollectorWithDB()
   file_id = collector.process_file_with_database("input/test1.html")
   ```

4. **Query Results**:
   ```python
   stats = db.get_file_statistics(file_id)
   print(f"Processed {stats['symbol_stats']['total_symbols']} symbols")
   ```

This approach gives you the full power of SQL with the simplicity of Python, perfect for your HTML parsing project! 🎯 