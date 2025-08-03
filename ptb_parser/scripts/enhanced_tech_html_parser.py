#!/usr/bin/env python3
"""
Enhanced TECH HTML Parser Database - Complete Implementation
Enhanced database implementation with hash-based file identification, UUID storage,
file-specific auto-increment IDs, and complete reprocessing logic
Based on inst_4.md specification
"""

import sqlite3
import json
import hashlib
import zlib
import uuid
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import content extraction module
from extract_content_items import ContentExtractor

class EnhancedTechHTMLParserDatabase:
    def __init__(self, db_path: str = "sqllite/tech_html_parser.db"):
        self.db_path = db_path
        self.content_extractor = ContentExtractor()
        self.init_enhanced_database()
    
    def init_enhanced_database(self):
        """Initialize database with enhanced schema including hash-based identification."""
        with sqlite3.connect(self.db_path) as conn:
            # Enhanced files table with hash-based identification
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid VARCHAR(36) NOT NULL,
                    input_filename VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    stored_file_path TEXT,        -- Path in input_file_store
                    file_size INTEGER,
                    sha256_hash VARCHAR(64) NOT NULL,
                    md5_hash VARCHAR(32),
                    crc32_hash VARCHAR(8),
                    file_modified_time INTEGER,
                    processing_count INTEGER DEFAULT 1,
                    first_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sha256_hash),
                    UNIQUE(uuid)
                )
            """)
            
            # Brackets table with file-specific auto-increment
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brackets (
                    brack_id INTEGER,              -- Auto-incremental per file_id
                    file_id INTEGER NOT NULL,
                    inner_id INTEGER NOT NULL,
                    bracket_order INTEGER NOT NULL,
                    bracket_type VARCHAR(10) NOT NULL,
                    position INTEGER NOT NULL,
                    chars_before TEXT,
                    chars_after TEXT,
                    full_context TEXT,
                    type_tech_tag VARCHAR(50) DEFAULT 'regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (brack_id, file_id),  -- Composite primary key
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, bracket_order)
                )
            """)
            
            # Enhanced tech_html_elements table with file-specific auto-increment
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tech_html_elements (
                    techhtml_id INTEGER,           -- Auto-incremental per file_id
                    file_id INTEGER NOT NULL,
                    element_order INTEGER NOT NULL,
                    inner_id_open_ttag INTEGER NOT NULL,
                    inner_id_close_ttag INTEGER NOT NULL,
                    pos_open_ttag INTEGER NOT NULL,
                    pos_close_ttag INTEGER NOT NULL,
                    type_ttag VARCHAR(50) DEFAULT 'unnamed',
                    name_tech_tag_html VARCHAR(100),
                    body_tech_tag_html TEXT,
                    is_comment BOOLEAN DEFAULT FALSE,
                    comment_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (techhtml_id, file_id),  -- Composite primary key
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    UNIQUE(file_id, element_order)
                )
            """)
            
            # Validation results table with file-specific auto-increment
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    valid_id INTEGER,              -- Auto-incremental per file_id
                    file_id INTEGER NOT NULL,
                    validation_type VARCHAR(50) NOT NULL,
                    validation_status VARCHAR(20) NOT NULL,
                    validation_score DECIMAL(3,2) DEFAULT 0.00,
                    total_items INTEGER DEFAULT 0,
                    valid_items INTEGER DEFAULT 0,
                    invalid_items INTEGER DEFAULT 0,
                    error_details JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (valid_id, file_id),  -- Composite primary key
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
                    FOREIGN KEY (validation_result_id) REFERENCES validation_results(valid_id)
                )
            """)
            
            # Content Tech HTML table (inst_4.md specification)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_tech_html (
                    content_id INTEGER,           -- Auto-incremental per file_id
                    techhtml_id_start INTEGER,          
                    techhtml_id_end INTEGER,
                    file_id INTEGER NOT NULL,
                    pos_start INTEGER NOT NULL,
                    pos_end INTEGER NOT NULL,
                    content_body TEXT,
                    type_content VARCHAR(10) DEFAULT 'element',  -- Content type classification
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Last update timestamp
                    PRIMARY KEY (file_id, content_id),  -- Composite primary key
                    FOREIGN KEY (file_id) REFERENCES files(id),
                    FOREIGN KEY (techhtml_id_start) REFERENCES tech_html_elements(techhtml_id),
                    FOREIGN KEY (techhtml_id_end) REFERENCES tech_html_elements(techhtml_id)    
                )
            """)
            
            # Add new columns to existing table if they don't exist (for backward compatibility)
            try:
                conn.execute("ALTER TABLE content_tech_html ADD COLUMN type_content VARCHAR(10) DEFAULT 'element'")
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                conn.execute("ALTER TABLE content_tech_html ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Content Items Tech HTML table (id_part2 specification)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_items_tech_html (
                    item_id INTEGER,    -- Auto-incremental per content_id
                    content_id INTEGER,
                    type_content VARCHAR(15) DEFAULT 'img_src',  -- Content item type classification
                    item_body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Last update timestamp
                    PRIMARY KEY (item_id, content_id),  -- Composite primary key
                    FOREIGN KEY (content_id) REFERENCES content_tech_html(content_id)    
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_uuid ON files(uuid)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_md5 ON files(md5_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_brackets_file_id ON brackets(file_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_brackets_type ON brackets(type_tech_tag)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_brackets_position ON brackets(position)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tech_html_elements_file_id ON tech_html_elements(file_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tech_html_elements_type ON tech_html_elements(type_ttag)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_validation_file_id ON validation_results(file_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_validation_type ON validation_results(validation_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_tech_html_file_id ON content_tech_html(file_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_tech_html_positions ON content_tech_html(pos_start, pos_end)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_items_tech_html_content_id ON content_items_tech_html(content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_items_tech_html_type ON content_items_tech_html(type_content)")
            
            conn.commit()
    
    def calculate_file_hashes(self, file_path: str) -> Dict[str, Any]:
        """Calculate SHA-256, MD5, and CRC32 hashes for a file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            return {
                'sha256': hashlib.sha256(content).hexdigest(),
                'md5': hashlib.md5(content).hexdigest(),
                'crc32': f"{zlib.crc32(content):08x}",
                'file_size': len(content),
                'modified_time': int(os.path.getmtime(file_path))
            }
        except Exception as e:
            print(f"❌ Error calculating hashes for {file_path}: {e}")
            return {}
    
    def check_file_exists(self, sha256_hash: str) -> Optional[Dict[str, Any]]:
        """Check if file exists in database by SHA-256 hash."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT * FROM files WHERE sha256_hash = ?
            """, (sha256_hash,)).fetchone()
            
            if result:
                columns = [description[0] for description in conn.execute("SELECT * FROM files LIMIT 1").description]
                return dict(zip(columns, result))
            return None
    
    def store_input_file_with_uuid(self, file_path: str, file_uuid: str) -> str:
        """Store input file with UUID-based naming in input_file_store directory."""
        # Create input_file_store directory
        store_dir = Path("input_file_store")
        store_dir.mkdir(exist_ok=True)
        
        # Get file extension
        file_extension = Path(file_path).suffix
        
        # Create new filename: uuid + original extension
        new_filename = f"{file_uuid}{file_extension}"
        new_file_path = store_dir / new_filename
        
        # Copy file to storage
        shutil.copy2(file_path, new_file_path)
        
        return str(new_file_path)
    
    def delete_all_file_data(self, file_id: int):
        """Delete all related data for a specific file_id (but keep the file record)."""
        with sqlite3.connect(self.db_path) as conn:
            # Delete validation errors first (they reference validation_results)
            conn.execute("""
                DELETE FROM validation_errors 
                WHERE validation_result_id IN (
                    SELECT valid_id FROM validation_results WHERE file_id = ?
                )
            """, (file_id,))
            
            # Delete from tables with direct file_id reference
            tables_with_file_id = [
                'brackets',
                'tech_html_elements', 
                'validation_results',
                'content_tech_html'
            ]
            
            # Delete content_items_tech_html records that reference content_tech_html records for this file
            conn.execute("""
                DELETE FROM content_items_tech_html 
                WHERE content_id IN (
                    SELECT content_id FROM content_tech_html WHERE file_id = ?
                )
            """, (file_id,))
            
            for table in tables_with_file_id:
                conn.execute(f"DELETE FROM {table} WHERE file_id = ?", (file_id,))
            
            # ❌ DON'T delete from files table - keep the file record!
            # conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()
    
    def update_file_with_new_uuid(self, file_id: int, new_uuid: str, stored_file_path: str) -> int:
        """Update existing file record with new UUID for reprocessing."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE files 
                SET uuid = ?, stored_file_path = ?, processing_count = processing_count + 1,
                    last_processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_uuid, stored_file_path, file_id))
            conn.commit()
            return file_id
    
    def add_new_file_record(self, file_uuid: str, file_path: str, stored_file_path: str, 
                           hashes: Dict[str, Any]) -> int:
        """Add new file record to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO files 
                (uuid, input_filename, file_path, stored_file_path, file_size, 
                 sha256_hash, md5_hash, crc32_hash, file_modified_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_uuid,
                Path(file_path).name,
                file_path,
                stored_file_path,
                hashes.get('file_size'),
                hashes.get('sha256'),
                hashes.get('md5'),
                hashes.get('crc32'),
                hashes.get('modified_time')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_next_brack_id(self, file_id: int) -> int:
        """Get next brack_id for specific file_id."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT COALESCE(MAX(brack_id), 0) + 1
                FROM brackets 
                WHERE file_id = ?
            """, (file_id,)).fetchone()
            return result[0]
    
    def get_next_techhtml_id(self, file_id: int) -> int:
        """Get next techhtml_id for specific file_id."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT COALESCE(MAX(techhtml_id), 0) + 1
                FROM tech_html_elements 
                WHERE file_id = ?
            """, (file_id,)).fetchone()
            return result[0]
    
    def get_next_valid_id(self, file_id: int) -> int:
        """Get next valid_id for specific file_id."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT COALESCE(MAX(valid_id), 0) + 1
                FROM validation_results 
                WHERE file_id = ?
            """, (file_id,)).fetchone()
            return result[0]
    
    def add_brackets_with_file_specific_id(self, file_id: int, brackets: List[Dict[str, Any]]):
        """Add brackets with file-specific auto-increment."""
        with sqlite3.connect(self.db_path) as conn:
            # Get the starting brack_id for this batch
            start_brack_id = self.get_next_brack_id(file_id)
            
            for i, bracket in enumerate(brackets):
                # Calculate brack_id for this bracket
                brack_id = start_brack_id + i
                
                conn.execute("""
                    INSERT INTO brackets 
                    (brack_id, file_id, inner_id, bracket_order, bracket_type, 
                     position, chars_before, chars_after, full_context, type_tech_tag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    brack_id,
                    file_id,
                    bracket.get('inner_id', 0),
                    bracket.get('order', 0),
                    bracket.get('bracket', ''),
                    bracket.get('pos_in_file', 0),
                    bracket.get('chars_5_before', ''),
                    bracket.get('chars_5_after', ''),
                    bracket.get('full_context', ''),
                    bracket.get('type_tech_tag', 'regular')
                ))
            conn.commit()
    
    def add_tech_html_elements_with_file_specific_id(self, file_id: int, elements: List[Dict[str, Any]]):
        """Add TECH HTML elements with file-specific auto-increment."""
        with sqlite3.connect(self.db_path) as conn:
            # Get the starting techhtml_id for this batch
            start_techhtml_id = self.get_next_techhtml_id(file_id)
            
            for i, element in enumerate(elements):
                # Calculate techhtml_id for this element
                techhtml_id = start_techhtml_id + i
                
                # Use sequential element_order to avoid unique constraint violations
                element_order = i + 1
                
                conn.execute("""
                    INSERT INTO tech_html_elements 
                    (techhtml_id, file_id, element_order, inner_id_open_ttag, 
                     inner_id_close_ttag, pos_open_ttag, pos_close_ttag, 
                     type_ttag, name_tech_tag_html, body_tech_tag_html, 
                     is_comment, comment_body)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    techhtml_id,
                    file_id,
                    element_order,  # Use sequential order instead of element.get('id', 0)
                    element.get('inner_id_open_ttag', 0),
                    element.get('inner_id_close_ttag', 0),
                    element.get('pos_open_ttag', 0),
                    element.get('pos_close_ttag', 0),
                    element.get('type_ttag', 'unnamed'),
                    element.get('name_tech_tag_html', ''),
                    element.get('body_tech_tag_html', ''),
                    element.get('name_tech_tag_html') == 'comment',
                    element.get('body_tech_tag_html', '')
                ))
            conn.commit()
    
    def add_validation_result_with_file_specific_id(self, file_id: int, validation_type: str, 
                                                  validation_data: Dict[str, Any]):
        """Add validation result with file-specific auto-increment."""
        with sqlite3.connect(self.db_path) as conn:
            # Get next valid_id for this file
            valid_id = self.get_next_valid_id(file_id)
            
            conn.execute("""
                INSERT INTO validation_results 
                (valid_id, file_id, validation_type, validation_status, validation_score,
                 total_items, valid_items, invalid_items, error_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                valid_id,
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
    
    def process_file_with_enhanced_storage(self, file_path: str) -> int:
        """Enhanced file processing with UUID storage and reprocessing logic."""
        
        # 1. Calculate file hashes
        hashes = self.calculate_file_hashes(file_path)
        if not hashes:
            raise ValueError(f"Failed to calculate hashes for {file_path}")
        
        # 2. Check if file already exists
        existing_file = self.check_file_exists(hashes['sha256'])
        
        if existing_file:
            print(f"🔄 Reprocessing file: {existing_file['input_filename']}")
            print(f"   Previous processing count: {existing_file['processing_count']}")
            print(f"   Existing file_id: {existing_file['id']}")
            print(f"   Existing UUID: {existing_file['uuid']}")
            
            # 3. Delete all existing parsing data for this file (keep the file record unchanged)
            self.delete_all_file_data(existing_file['id'])
            print(f"   ✅ Deleted all previous parsing data for file_id: {existing_file['id']}")
            
            # 4. Use existing UUID and stored_file_path (don't change files table)
            new_uuid = existing_file['uuid']
            stored_file_path = existing_file['stored_file_path']
            file_id = existing_file['id']
            print(f"   🔄 Keeping existing file_id: {file_id} and UUID: {new_uuid}")
            print(f"   📁 Using existing stored file: {stored_file_path}")
            
        else:
            print(f"✅ Processing new file: {Path(file_path).name}")
            
            # 7. Generate new UUID
            new_uuid = str(uuid.uuid4())
            
            # 8. Store file with UUID
            stored_file_path = self.store_input_file_with_uuid(file_path, new_uuid)
            
            # 9. Add new file record
            file_id = self.add_new_file_record(new_uuid, file_path, stored_file_path, hashes)
            print(f"   🆕 Created new file_id: {file_id}")
        
        print(f"   📁 Stored file: {stored_file_path}")
        print(f"   🔑 File UUID: {new_uuid}")
        print(f"   🆔 Database ID: {file_id}")
        
        return file_id
    
    def get_file_statistics(self, file_id: int) -> Dict[str, Any]:
        """Get comprehensive statistics for a file."""
        with sqlite3.connect(self.db_path) as conn:
            # File info
            file_info = conn.execute("""
                SELECT * FROM files WHERE id = ?
            """, (file_id,)).fetchone()
            
            if not file_info:
                return {}
            
            columns = [description[0] for description in conn.execute("SELECT * FROM files LIMIT 1").description]
            file_data = dict(zip(columns, file_info))
            
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
            
            # TECH HTML Element counts
            element_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_elements,
                    SUM(CASE WHEN is_comment = 1 THEN 1 ELSE 0 END) as comment_elements,
                    SUM(CASE WHEN is_comment = 0 THEN 1 ELSE 0 END) as tag_elements,
                    COUNT(DISTINCT type_ttag) as unique_tag_types
                FROM tech_html_elements WHERE file_id = ?
            """, (file_id,)).fetchone()
            
            # Validation results
            validation_stats = conn.execute("""
                SELECT 
                    validation_type,
                    validation_status,
                    validation_score,
                    total_items,
                    valid_items,
                    invalid_items
                FROM validation_results WHERE file_id = ?
            """, (file_id,)).fetchall()
            
            return {
                'file_info': file_data,
                'bracket_stats': dict(zip(['total_brackets', 'opening_brackets', 'closing_brackets', 
                                         'comment_openings', 'comment_closings'], bracket_stats)),
                'element_stats': dict(zip(['total_elements', 'comment_elements', 'tag_elements', 
                                         'unique_tag_types'], element_stats)),
                'validation_stats': [dict(zip(['validation_type', 'validation_status', 'validation_score',
                                             'total_items', 'valid_items', 'invalid_items'], row)) 
                                   for row in validation_stats]
            }
    
    def get_all_files_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all files in database."""
        with sqlite3.connect(self.db_path) as conn:
            results = conn.execute("""
                SELECT 
                    f.id,
                    f.uuid,
                    f.input_filename,
                    f.file_size,
                    f.processing_count,
                    f.first_processed_at,
                    f.last_processed_at,
                    COUNT(b.brack_id) as bracket_count,
                    COUNT(t.techhtml_id) as element_count,
                    COUNT(v.valid_id) as validation_count
                FROM files f
                LEFT JOIN brackets b ON f.id = b.file_id
                LEFT JOIN tech_html_elements t ON f.id = t.file_id
                LEFT JOIN validation_results v ON f.id = v.file_id
                GROUP BY f.id
                ORDER BY f.last_processed_at DESC
            """).fetchall()
            
            columns = ['id', 'uuid', 'input_filename', 'file_size', 'processing_count',
                      'first_processed_at', 'last_processed_at', 'bracket_count', 
                      'element_count', 'validation_count']
            
            return [dict(zip(columns, row)) for row in results]
    
    # Content Tech HTML Processing Methods (inst_4.md implementation)
    def get_next_content_id(self, file_id: int) -> int:
        """Get the next content_id for a specific file_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(MAX(content_id), 0) + 1 
                FROM content_tech_html 
                WHERE file_id = ?
            """, (file_id,))
            return cursor.fetchone()[0]
    
    def add_content_tech_html(self, file_id: int, techhtml_id_start: int, techhtml_id_end: int, 
                             pos_start: int, pos_end: int, content_body: str, type_content: str = 'element') -> int:
        """Add a new content_tech_html record with new fields from id_part2."""
        content_id = self.get_next_content_id(file_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO content_tech_html 
                (content_id, techhtml_id_start, techhtml_id_end, file_id, 
                 pos_start, pos_end, content_body, type_content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (content_id, techhtml_id_start, techhtml_id_end, file_id,
                  pos_start, pos_end, content_body, type_content, datetime.now(), datetime.now()))
            conn.commit()
            return content_id
    
    def get_file_content(self, file_id: int) -> str:
        """Get the original file content for a specific file_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stored_file_path FROM files WHERE id = ?
            """, (file_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                print(f"❌ No stored file path found for file_id: {file_id}")
                return ""
            
            stored_file_path = result[0]
            
            try:
                with open(stored_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"❌ Error reading file {stored_file_path}: {e}")
                return ""
    
    def get_tech_html_elements_by_file(self, file_id: int, limit: int = None) -> List[tuple]:
        """Get tech HTML elements for a specific file."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT techhtml_id, pos_open_ttag, pos_close_ttag, file_id, 
                       type_ttag, name_tech_tag_html
                FROM tech_html_elements 
                WHERE file_id = ?
                ORDER BY pos_open_ttag
            """
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (file_id,))
            return cursor.fetchall()
    

    def filter_file_elements(self, somecontent, name_tech_tag: str) -> bool:
        """Filter file content elements """        
        if name_tech_tag == 'comment':
            return False
        if name_tech_tag == 'script':
            return False
        if name_tech_tag == 'style':
            return False
       # if some element body contains key word "href", "src", "alt", "rel" then return True            
        if 'href' in somecontent.lower():
            return True
        if 'src' in somecontent.lower():
            return True
        if 'alt' in somecontent.lower():
            return True
        if 'rel' in somecontent.lower():
            return True



    def filter_file_between_elements(self, somecontent: str) -> bool:
        """Filter file content between elements
          if it after trim it is empty then return False
          if it is empty then return False
          if it is not attribute then return False
        """

        content = somecontent
        if len(content.strip()) == 0:
            return False
        if content.startswith('\n'):
            return False
        if content.startswith('\t'):
            return False
        if content.startswith('\r'):
            return False
        return True

    def process_file_content(self, file_id: int, limit: int = 5) -> Dict[str, Any]:
        """Process tech HTML elements for a file and create content records with improved extraction."""
        print(f"🔄 Processing content for file_id: {file_id}")
        
        # Get tech HTML elements
        elements = self.get_tech_html_elements_by_file(file_id, 0)
        
        if not elements:
            print(f"❌ No tech HTML elements found for file_id: {file_id}")
            return {'processed': 0, 'created': 0}
        
        print(f"📊 Found {len(elements)} elements to process")
        
        # Get file content for extraction
        f_content = self.get_file_content(file_id)
        if not f_content:
            print(f"❌ No file content found for file_id: {file_id}")
            return {'processed': 0, 'created': 0}
        
        print(f"📄 File content length: {len(f_content)} characters")
        
        created_records = []
        prev_pos_close = 0
        prev_techhtml_id = 0
        
        # Process each element with improved extraction
        for i, element in enumerate(elements):
            techhtml_id, pos_open, pos_close, file_id, type_ttag, name_tech_tag = element
           
           
            # Extract content between previous element and current element
            if pos_open > prev_pos_close:
                content_body = f_content[prev_pos_close:pos_open]  # +1 to include pos_open

                if self.filter_file_between_elements(content_body):
                    content_id = self.add_content_tech_html(
                        file_id=file_id,
                        techhtml_id_start=prev_techhtml_id,
                        techhtml_id_end=techhtml_id,
                        pos_start=prev_pos_close,
                        pos_end=pos_open,
                        content_body=content_body,
                        type_content='between_elements'
                    )
                    
                    created_records.append({
                        'content_id': content_id,
                        'type': 'between_elements',
                        'pos_start': prev_pos_close,
                        'pos_end': pos_open,
                        'content': content_body
                    })
                    
            
            
            # Extract the element content itself
            element_content = f_content[pos_open:pos_close+1]  # +1 to include pos_close

            if self.filter_file_elements(element_content, name_tech_tag):           
                content_id = self.add_content_tech_html(
                    file_id=file_id,
                    techhtml_id_start=techhtml_id,
                    techhtml_id_end=techhtml_id,
                    pos_start=pos_open,
                    pos_end=pos_close+1,
                    content_body=element_content,
                    type_content='element'
                )
                
                created_records.append({
                    'content_id': content_id,
                    'type': 'element',
                    'pos_start': pos_open,
                    'pos_end': pos_close+1,
                    'content': element_content
                })
            
            
            
            # Update for next iteration
            prev_pos_close = pos_close+1
            prev_techhtml_id = techhtml_id
        
        print(f"\n🎉 Content processing complete for file_id: {file_id}")
        return {'processed': len(elements), 'created': len(created_records), 'records': created_records}
    
    def show_content_tech_html_records(self, file_id: int = None, limit: int = 10) -> None:
        """Display content_tech_html records with new fields from id_part2."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if file_id:
                cursor.execute("""
                    SELECT content_id, techhtml_id_start, techhtml_id_end, 
                           file_id, pos_start, pos_end, content_body, type_content, updated_at
                    FROM content_tech_html 
                    WHERE file_id = ?
                    ORDER BY content_id
                    LIMIT ?
                """, (file_id, limit))
            else:
                cursor.execute("""
                    SELECT content_id, techhtml_id_start, techhtml_id_end, 
                           file_id, pos_start, pos_end, content_body, type_content, updated_at
                    FROM content_tech_html 
                    ORDER BY file_id, content_id
                    LIMIT ?
                """, (limit,))
            
            records = cursor.fetchall()
            
            if not records:
                print("❌ No content_tech_html records found")
                return
            
            print(f"\n📋 Content Tech HTML Records (showing {len(records)} records):")
            print("-" * 100)
            print(f"{'content_id':<10} {'techhtml_start':<15} {'techhtml_end':<15} {'file_id':<8} {'pos_start':<10} {'pos_end':<10} {'type_content':<12} {'content_body':<25}")
            print("-" * 100)
            
            for record in records:
                content_id, techhtml_start, techhtml_end, file_id, pos_start, pos_end, content_body, type_content, updated_at = record
                print(f"{content_id:<10} {techhtml_start:<15} {techhtml_end:<15} {file_id:<8} {pos_start:<10} {pos_end:<10} {type_content:<12} {content_body[:25]:<25}")



    def get_content_tech_html_by_file(self, file_id: int, limit: int = None) -> List[tuple]:
        """Get content_tech_html records for a specific file."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT content_id, content_body, type_content
                FROM content_tech_html 
                WHERE file_id = ?
                ORDER BY content_id
            """
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (file_id,))
            return cursor.fetchall()

    def get_next_item_id(self, content_id: int) -> int:
        """Get next item_id for specific content_id."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("""
                SELECT COALESCE(MAX(item_id), 0) + 1
                FROM content_items_tech_html 
                WHERE content_id = ?
            """, (content_id,)).fetchone()
            return result[0]
    
    def add_content_items_tech_html(self, content_id: int, item_body: str, 
                                   type_content: str = 'img_src') -> int:
        """Add content item to content_items_tech_html table."""
        with sqlite3.connect(self.db_path) as conn:
            # Get next item_id for this content_id
            item_id = self.get_next_item_id(content_id)
            
            conn.execute("""
                INSERT INTO content_items_tech_html 
                (item_id, content_id, type_content, item_body, created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (item_id, content_id, type_content, item_body))
            conn.commit()
            return item_id
    
    def get_content_items_by_content_id(self, content_id: int, limit: int = None) -> List[tuple]:
        """Get content_items_tech_html records for a specific content_id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT item_id, content_id, type_content, item_body, created_at, updated_at
                FROM content_items_tech_html 
                WHERE content_id = ?
                ORDER BY item_id
            """
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (content_id,))
            return cursor.fetchall()


    
    def process_file_content_items(self, file_id: int, limit: int = 5) -> Dict[str, Any]:
        """Process content_tech_html records for a file and create content_items_tech_html records."""    
        
        # Get content_tech_html records
        content_records = self.get_content_tech_html_by_file(file_id, 0)
        
        if not content_records:
            print(f"❌ No content_tech_html records found for file_id: {file_id}")
            return {'processed': 0, 'created': 0}
    
        print(f"📊 Found {len(content_records)} content_tech_html records to process")
        
        created_items = []
        
        # Process each content record
        for i, content_record in enumerate(content_records):
            content_id, content_body, type_content = content_record
            
            if type_content == 'between_elements':
                # Create content_items_tech_html record
                item_id = self.add_content_items_tech_html(
                    content_id=content_id,
                    item_body=content_body,
                    type_content=type_content
                )

            if type_content == 'element':
                # Create content_items_tech_html record using the content extractor
                extracted_content = self.content_extractor.extract_content_from_element(content_body)
                item_id = self.add_content_items_tech_html(
                    content_id=content_id,
                    item_body=content_body,
                    type_content=extracted_content
                )
            created_items.append({
                'item_id': item_id,
                'content_id': content_id,
                'type_content': type_content,
                'item_body': content_body[:100] + '...' if len(content_body) > 100 else content_body
            })
            
            if limit and i >= limit - 1:
                break
        
        print(f"✅ Created {len(created_items)} content items")
        
        return {
            'processed': len(content_records),
            'created': len(created_items),
            'items': created_items
        }
    
    def show_content_items_records(self, content_id: int = None, limit: int = 10) -> None:
        """Show content_items_tech_html records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if content_id:
                query = """
                    SELECT item_id, content_id, type_content, item_body, created_at
                    FROM content_items_tech_html 
                    WHERE content_id = ?
                    ORDER BY item_id
                    LIMIT ?
                """
                cursor.execute(query, (content_id, limit))
            else:
                query = """
                    SELECT item_id, content_id, type_content, item_body, created_at
                    FROM content_items_tech_html 
                    ORDER BY content_id, item_id
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            records = cursor.fetchall()
            
            if not records:
                print("❌ No content_items_tech_html records found")
                return
            
            print(f"\n📋 Content Items Records (showing {len(records)} records):")
            print("-" * 80)
            
            for record in records:
                item_id, content_id, type_content, item_body, created_at = record
                print(f"Item ID: {item_id}")
                print(f"Content ID: {content_id}")
                print(f"Type: {type_content}")
                print(f"Body: {item_body[:100]}{'...' if len(item_body) > 100 else ''}")
                print(f"Created: {created_at}")
                print("-" * 40)


def main():
    """Demonstrate enhanced database functionality."""
    print("🚀 Enhanced TECH HTML Parser Database")
    print("=" * 50)
    
    # Initialize enhanced database
    db = EnhancedTechHTMLParserDatabase()
    
    # Example file processing
    test_file = "input/test1.html"
    if Path(test_file).exists():
        print(f"\n📁 Processing file: {test_file}")
        file_id = db.process_file_with_enhanced_storage(test_file)
        
        # Get statistics
        stats = db.get_file_statistics(file_id)
        print(f"\n📊 File Statistics:")
        print(f"   File: {stats['file_info']['input_filename']}")
        print(f"   UUID: {stats['file_info']['uuid']}")
        print(f"   Processing Count: {stats['file_info']['processing_count']}")
        
        if 'bracket_stats' in stats:
            print(f"   Brackets: {stats['bracket_stats']['total_brackets']}")
        
        if 'element_stats' in stats:
            print(f"   Elements: {stats['element_stats']['total_elements']}")
        
        # Process content for this file (inst_4.md implementation)
        print(f"\n🔄 Processing content for file_id: {file_id}")
        # content_result = db.process_file_content(file_id, limit=5)
        content_result = db.process_file_content(file_id)
        print(f"📊 Content processing result: {content_result}")
        
        # Show content records
        db.show_content_tech_html_records(file_id, limit=5)
    
    # Show all files summary
    print(f"\n📋 All Files Summary:")
    files_summary = db.get_all_files_summary()
    for file_info in files_summary:
        print(f"   {file_info['input_filename']} (ID: {file_info['id']}, "
              f"Processed: {file_info['processing_count']} times)")

if __name__ == "__main__":
    main() 