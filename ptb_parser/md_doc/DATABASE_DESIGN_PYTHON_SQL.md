# Database Design: Python + SQLite for HTML Parser

## 📋 **Overview**

This document outlines a comprehensive database design using Python and SQLite for the HTML parser project, eliminating the need for traditional RDBMS while maintaining full SQL capabilities.

## 🎯 **Technology Stack**

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

### **2. Brackets Table**
```sql
CREATE TABLE brackets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    bracket_order INTEGER NOT NULL,
    bracket_type VARCHAR(10) NOT NULL, -- '<' or '>'
    position INTEGER NOT NULL,
    chars_before TEXT,
    chars_after TEXT,
    full_context TEXT,
    type_tech_tag VARCHAR(50) DEFAULT 'regular', -- 'comm_open', 'comm_close', 'inner_comm_content', 'regular'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id),
    UNIQUE(file_id, bracket_order)
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
    validation_type VARCHAR(50) NOT NULL, -- 'comment', 'bracket', 'element_sequence', 'unified'
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
            # Files table
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
            
            # Brackets table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brackets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    bracket_order INTEGER NOT NULL,
                    bracket_type VARCHAR(10) NOT NULL,
                    position INTEGER NOT NULL,
                    chars_before TEXT,
                    chars_after TEXT,
                    full_context TEXT,
                    type_tech_tag VARCHAR(50) DEFAULT 'regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, bracket_order)
                )
            """)
            
            # HTML Elements table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS html_elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    element_order INTEGER NOT NULL,
                    pos_open_ttag INTEGER NOT NULL,
                    pos_close_ttag INTEGER NOT NULL,
                    type_ttag VARCHAR(50) DEFAULT 'unnamed',
                    name_tech_tag_html VARCHAR(100),
                    body_tech_tag_html TEXT,
                    is_comment BOOLEAN DEFAULT FALSE,
                    comment_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, element_order)
                )
            """)
            
            # Validation Results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    validation_type VARCHAR(50) NOT NULL,
                    validation_status VARCHAR(20) NOT NULL,
                    validation_score DECIMAL(3,2) DEFAULT 0.00,
                    total_items INTEGER DEFAULT 0,
                    valid_items INTEGER DEFAULT 0,
                    invalid_items INTEGER DEFAULT 0,
                    error_details JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, validation_type)
                )
            """)
            
            # Validation Errors table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    validation_result_id INTEGER NOT NULL,
                    error_type VARCHAR(50) NOT NULL,
                    error_message TEXT,
                    error_position INTEGER,
                    error_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (validation_result_id) REFERENCES validation_results(id)
                )
            """)
            
            conn.commit()
    
    def add_file(self, filename: str, file_path: str, file_size: int = None) -> int:
        """Add a file to the database and return file_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO files (filename, file_path, file_size)
                VALUES (?, ?, ?)
            """, (filename, file_path, file_size))
            return cursor.lastrowid
    
    def add_brackets(self, file_id: int, brackets: List[Dict[str, Any]]):
        """Add brackets for a file."""
        with sqlite3.connect(self.db_path) as conn:
            for bracket in brackets:
                conn.execute("""
                    INSERT OR REPLACE INTO brackets 
                    (file_id, bracket_order, bracket_type, position, chars_before, 
                     chars_after, full_context, type_tech_tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_id,
                    bracket.get('order', 0),
                    bracket.get('bracket', ''),
                    bracket.get('pos_in_file', 0),
                    bracket.get('chars_5_before', ''),
                    bracket.get('chars_5_after', ''),
                    bracket.get('full_context', ''),
                    bracket.get('type_tech_tag', 'regular')
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
            
            # Bracket counts
            bracket_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_brackets,
                    SUM(CASE WHEN bracket_type = '<' THEN 1 ELSE 0 END) as opening_brackets,
                    SUM(CASE WHEN bracket_type = '>' THEN 1 ELSE 0 END) as closing_brackets,
                    SUM(CASE WHEN type_tech_tag = 'comm_open' THEN 1 ELSE 0 END) as comment_openings,
                    SUM(CASE WHEN type_tech_tag = 'comm_close' THEN 1 ELSE 0 END) as comment_closings
                FROM brackets WHERE file_id = ?
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
                'bracket_stats': dict(zip([col[0] for col in conn.description], bracket_stats)) if bracket_stats else {},
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
                    COUNT(b.id) as bracket_count,
                    COUNT(h.id) as element_count,
                    COUNT(v.id) as validation_count
                FROM files f
                LEFT JOIN brackets b ON f.id = b.file_id
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
        
        # Process brackets
        brackets = self.scan_bytes_for_brackets(file_path)
        enhanced_brackets = self.enhance_brackets_with_context(brackets, self.read_file_content(file_path))
        self.db.add_brackets(file_id, enhanced_brackets)
        
        # Process HTML elements
        html_elements = self.create_tech_tag_html_elements_comms(enhanced_brackets, self.read_file_content(file_path))
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

### **3. Bracket Distribution Analysis**
```sql
-- Analyze bracket distribution by file
SELECT 
    f.filename,
    COUNT(*) as total_brackets,
    SUM(CASE WHEN b.type_tech_tag = 'comm_open' THEN 1 ELSE 0 END) as comment_openings,
    SUM(CASE WHEN b.type_tech_tag = 'comm_close' THEN 1 ELSE 0 END) as comment_closings,
    SUM(CASE WHEN b.type_tech_tag = 'regular' THEN 1 ELSE 0 END) as regular_brackets
FROM brackets b
JOIN files f ON b.file_id = f.id
GROUP BY f.id, f.filename
ORDER BY total_brackets DESC;
```

### **4. Element Type Analysis**
```sql
-- Analyze HTML element types across all files
SELECT 
    type_ttag,
    COUNT(*) as element_count,
    COUNT(DISTINCT file_id) as file_count,
    AVG(pos_close_ttag - pos_open_ttag) as avg_element_length
FROM html_elements
GROUP BY type_ttag
ORDER BY element_count DESC;
```

### **5. Cross-Validation Analysis**
```sql
-- Compare validation results across different types
SELECT 
    f.filename,
    vr1.validation_score as bracket_score,
    vr2.validation_score as comment_score,
    vr3.validation_score as element_score,
    (vr1.validation_score + vr2.validation_score + vr3.validation_score) / 3 as overall_score
FROM files f
LEFT JOIN validation_results vr1 ON f.id = vr1.file_id AND vr1.validation_type = 'bracket_validation'
LEFT JOIN validation_results vr2 ON f.id = vr2.file_id AND vr2.validation_type = 'comment_validation'
LEFT JOIN validation_results vr3 ON f.id = vr3.file_id AND vr3.validation_type = 'element_sequence_validation'
ORDER BY overall_score DESC;
```

## 🔧 **Performance Optimizations**

### **1. Indexes for Better Performance**
```sql
-- Create indexes for common queries
CREATE INDEX idx_brackets_file_id ON brackets(file_id);
CREATE INDEX idx_brackets_type ON brackets(type_tech_tag);
CREATE INDEX idx_brackets_position ON brackets(position);
CREATE INDEX idx_elements_file_id ON html_elements(file_id);
CREATE INDEX idx_elements_type ON html_elements(type_ttag);
CREATE INDEX idx_validation_file_id ON validation_results(file_id);
CREATE INDEX idx_validation_type ON validation_results(validation_type);
CREATE INDEX idx_files_filename ON files(filename);
```

### **2. Batch Operations**
```python
def batch_insert_brackets(self, file_id: int, brackets: List[Dict[str, Any]]):
    """Batch insert brackets for better performance."""
    with sqlite3.connect(self.db_path) as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO brackets 
            (file_id, bracket_order, bracket_type, position, chars_before, 
             chars_after, full_context, type_tech_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(
            file_id,
            bracket.get('order', 0),
            bracket.get('bracket', ''),
            bracket.get('pos_in_file', 0),
            bracket.get('chars_5_before', ''),
            bracket.get('chars_5_after', ''),
            bracket.get('full_context', ''),
            bracket.get('type_tech_tag', 'regular')
        ) for bracket in brackets])
        conn.commit()
```

### **3. Connection Pooling**
```python
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
```

## 📊 **Data Export/Import**

### **1. Export to JSON**
```python
def export_file_data(self, file_id: int) -> Dict[str, Any]:
    """Export all data for a file to JSON format."""
    stats = self.get_file_statistics(file_id)
    
    with self.get_connection() as conn:
        brackets = conn.execute("""
            SELECT * FROM brackets WHERE file_id = ? ORDER BY bracket_order
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
            'brackets': stats['bracket_stats'],
            'elements': stats['element_stats'],
            'validations': stats['validation_results']
        },
        'brackets': [dict(row) for row in brackets],
        'elements': [dict(row) for row in elements],
        'validations': [dict(row) for row in validations]
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
    
    if 'brackets' in data:
        self.add_brackets(file_id, data['brackets'])
    
    if 'elements' in data:
        self.add_html_elements(file_id, data['elements'])
    
    if 'validations' in data:
        for validation in data['validations']:
            self.add_validation_result(file_id, validation['validation_type'], validation)
    
    return file_id
```

### **3. Backup and Restore**
```python
def backup_database(self, backup_path: str):
    """Create a backup of the database."""
    import shutil
    shutil.copy2(self.db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")

def restore_database(self, backup_path: str):
    """Restore database from backup."""
    import shutil
    shutil.copy2(backup_path, self.db_path)
    print(f"✅ Database restored from: {backup_path}")
```

## 📈 **Analytics and Reporting**

### **1. Processing Statistics**
```python
def get_processing_statistics(self) -> Dict[str, Any]:
    """Get overall processing statistics."""
    with self.get_connection() as conn:
        stats = conn.execute("""
            SELECT 
                COUNT(DISTINCT f.id) as total_files,
                SUM(f.file_size) as total_size,
                COUNT(b.id) as total_brackets,
                COUNT(h.id) as total_elements,
                COUNT(v.id) as total_validations,
                AVG(v.validation_score) as avg_validation_score
            FROM files f
            LEFT JOIN brackets b ON f.id = b.file_id
            LEFT JOIN html_elements h ON f.id = h.file_id
            LEFT JOIN validation_results v ON f.id = v.file_id
        """).fetchone()
        
        return dict(stats)
```

### **2. Performance Metrics**
```python
def get_performance_metrics(self) -> Dict[str, Any]:
    """Get performance metrics for the parser."""
    with self.get_connection() as conn:
        metrics = conn.execute("""
            SELECT 
                f.filename,
                COUNT(b.id) as bracket_count,
                COUNT(h.id) as element_count,
                AVG(h.pos_close_ttag - h.pos_open_ttag) as avg_element_size,
                AVG(v.validation_score) as avg_validation_score
            FROM files f
            LEFT JOIN brackets b ON f.id = b.file_id
            LEFT JOIN html_elements h ON f.id = h.file_id
            LEFT JOIN validation_results v ON f.id = v.file_id
            GROUP BY f.id, f.filename
            ORDER BY bracket_count DESC
        """).fetchall()
        
        return [dict(row) for row in metrics]
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
- **HTML Bracket Parsing** - Store brackets, elements, validation results
- **Analysis & Reporting** - Complex SQL queries for insights
- **Data Persistence** - Reliable storage without external dependencies
- **Scalability** - Can handle thousands of files efficiently
- **Integration** - Easy to integrate with existing Python code

## 🚀 **Implementation Steps**

### **1. Install Dependencies** (if needed):
```bash
pip install pandas  # Optional, for data analysis
```

### **2. Create Database Manager**:
```python
db = HTMLParserDatabase("html_parser.db")
```

### **3. Integrate with Parser**:
```python
collector = TechHTMLCollectorWithDB()
file_id = collector.process_file_with_database("input/test1.html")
```

### **4. Query Results**:
```python
stats = db.get_file_statistics(file_id)
print(f"Processed {stats['bracket_stats']['total_brackets']} brackets")
```

### **5. Generate Reports**:
```python
# Get all files summary
summary = db.get_all_files_summary()
for file in summary:
    print(f"File: {file['filename']}, Brackets: {file['bracket_count']}, Elements: {file['element_count']}")

# Get processing statistics
stats = db.get_processing_statistics()
print(f"Total files: {stats['total_files']}, Total brackets: {stats['total_brackets']}")
```

## 📋 **Usage Examples**

### **Basic Usage:**
```python
# Initialize database
db = HTMLParserDatabase("html_parser.db")

# Process a file
collector = TechHTMLCollectorWithDB()
file_id = collector.process_file_with_database("input/test1.html")

# Get statistics
stats = db.get_file_statistics(file_id)
print(f"File: {stats['file_info']['filename']}")
print(f"Brackets: {stats['bracket_stats']['total_brackets']}")
print(f"Elements: {stats['element_stats']['total_elements']}")
```

### **Advanced Analytics:**
```python
# Get bracket distribution
with db.get_connection() as conn:
    distribution = conn.execute("""
        SELECT bracket_type, COUNT(*) as count
        FROM brackets
        GROUP BY bracket_type
    """).fetchall()
    
    for row in distribution:
        print(f"{row['bracket_type']}: {row['count']}")

# Get validation success rates
with db.get_connection() as conn:
    success_rates = conn.execute("""
        SELECT validation_type, 
               AVG(validation_score) as avg_score,
               COUNT(*) as total_files
        FROM validation_results
        GROUP BY validation_type
    """).fetchall()
    
    for row in success_rates:
        print(f"{row['validation_type']}: {row['avg_score']:.2f} ({row['total_files']} files)")
```

This approach gives you the full power of SQL with the simplicity of Python, perfect for your HTML bracket parsing project! 🎯 