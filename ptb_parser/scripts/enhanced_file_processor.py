#!/usr/bin/env python3
"""
Enhanced File Processor - Complete Integration
Integrates enhanced database functionality with existing tech tag collector
Implements complete enhanced file processing strategy from inst_4.md
"""

import json
import hashlib
import zlib
import uuid
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the enhanced database
from enhanced_tech_html_parser import EnhancedTechHTMLParserDatabase

# Import the existing tech tag collector
from tech_tag_collector import TechHTMLCollector

class EnhancedFileProcessor:
    """Enhanced file processor with complete integration of database and collector."""
    
    def __init__(self, config_file: str = "json/tech_tag_config.json", 
                 db_path: str = "sqllite/tech_html_parser.db"):
        self.config_file = config_file
        self.config = self.load_config()
        self.db = EnhancedTechHTMLParserDatabase(db_path)
        self.collector = TechHTMLCollector(config_file)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_file}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for enhanced processing."""
        return {
            "input_files": ["input/test1.html"],
            "enable_enhanced_storage": True,
            "enable_hash_detection": True,
            "enable_uuid_storage": True,
            "enable_reprocessing": True,
            "processing_settings": {
                "max_file_size_mb": 10,
                "encoding": "utf-8",
                "error_handling": "continue",
                "verbose_output": True
            }
        }
    
    def process_file_with_enhanced_storage(self, file_path: str) -> int:
        """Process file with enhanced storage and database integration."""
        
        print(f"\n🚀 Processing file: {Path(file_path).name}")
        
        # 1. Enhanced file processing with UUID storage
        file_id = self.db.process_file_with_enhanced_storage(file_path)
        
        # 2. Get stored file path from database
        stored_file_path = self.get_stored_file_path(file_id)
        
        if not stored_file_path or not Path(stored_file_path).exists():
            print(f"❌ Stored file not found: {stored_file_path}")
            return file_id
        
        # 3. Process file with tech tag collector
        print(f"   🔍 Running TECH HTML analysis...")
        self.process_file_with_collector(stored_file_path, file_id)
        
        # 4. Generate comprehensive statistics
        stats = self.db.get_file_statistics(file_id)
        self.print_processing_summary(stats)
        
        return file_id
    
    def get_stored_file_path(self, file_id: int) -> Optional[str]:
        """Get stored file path from database."""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            result = conn.execute("""
                SELECT stored_file_path FROM files WHERE id = ?
            """, (file_id,)).fetchone()
            return result[0] if result else None
    
    def process_file_with_collector(self, stored_file_path: str, file_id: int):
        """Process file using the tech tag collector and store results in database."""
        
        # Read file content
        try:
            with open(stored_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file {stored_file_path}: {e}")
            return
        
        # Process brackets
        print(f"   📊 Scanning brackets...")
        brackets = self.collector.scan_bytes_for_brackets(stored_file_path)
        enhanced_brackets = self.collector.enhance_brackets_with_context(brackets, content)
        
        # Store brackets in database
        if enhanced_brackets:
            self.db.add_brackets_with_file_specific_id(file_id, enhanced_brackets)
            print(f"   ✅ Stored {len(enhanced_brackets)} brackets")
        
        # Process TECH HTML elements
        print(f"   🏷️  Processing TECH HTML elements...")
        tech_elements = self.collector.create_tech_tag_html_elements(enhanced_brackets, content)
        
        # Store TECH HTML elements in database
        if tech_elements:
            self.db.add_tech_html_elements_with_file_specific_id(file_id, tech_elements)
            print(f"   ✅ Stored {len(tech_elements)} TECH HTML elements")
        
        # Run validation
        print(f"   ✅ Running validation...")
        validation_results = self.collector.run_comprehensive_validation(stored_file_path)
        
        # Store validation results
        if validation_results:
            # Store individual validation components
            validation_components = {
                'validation_summary': validation_results.get('validation_summary', {}),
                'validation_details': validation_results.get('validation_details', {}),
                'cross_validation_analysis': validation_results.get('cross_validation_analysis', {})
            }
            
            for validation_type, validation_data in validation_components.items():
                if validation_data:
                    self.db.add_validation_result_with_file_specific_id(file_id, validation_type, validation_data)
                    print(f"   ✅ Stored {validation_type} validation")
    
    def print_processing_summary(self, stats: Dict[str, Any]):
        """Print comprehensive processing summary."""
        if not stats or 'file_info' not in stats:
            print("   ❌ No statistics available")
            return
        
        file_info = stats['file_info']
        print(f"\n📊 Processing Summary:")
        print(f"   📁 File: {file_info['input_filename']}")
        print(f"   🔑 UUID: {file_info['uuid']}")
        print(f"   🆔 Database ID: {file_info['id']}")
        print(f"   🔄 Processing Count: {file_info['processing_count']}")
        print(f"   📏 File Size: {file_info['file_size']:,} bytes")
        
        if 'bracket_stats' in stats:
            bracket_stats = stats['bracket_stats']
            print(f"   📊 Brackets: {bracket_stats['total_brackets']} total")
            print(f"      ├─ Opening: {bracket_stats['opening_brackets']}")
            print(f"      ├─ Closing: {bracket_stats['closing_brackets']}")
            print(f"      ├─ Comment Opens: {bracket_stats['comment_openings']}")
            print(f"      └─ Comment Closes: {bracket_stats['comment_closings']}")
        
        if 'element_stats' in stats:
            element_stats = stats['element_stats']
            print(f"   🏷️  Elements: {element_stats['total_elements']} total")
            print(f"      ├─ Tags: {element_stats['tag_elements']}")
            print(f"      ├─ Comments: {element_stats['comment_elements']}")
            print(f"      └─ Unique Types: {element_stats['unique_tag_types']}")
        
        if 'validation_stats' in stats:
            print(f"   ✅ Validations: {len(stats['validation_stats'])} types")
            for validation in stats['validation_stats']:
                print(f"      ├─ {validation['validation_type']}: {validation['validation_status']}")
                print(f"      │  Score: {validation['validation_score']:.2f}")
                print(f"      │  Items: {validation['valid_items']}/{validation['total_items']} valid")
    
    def process_all_files(self):
        """Process all files specified in configuration."""
        input_files = self.config.get("input_files", [])
        
        print(f"📁 Processing {len(input_files)} files...")
        
        processed_files = []
        errors = []
        
        for file_path in input_files:
            if Path(file_path).exists():
                try:
                    file_id = self.process_file_with_enhanced_storage(file_path)
                    processed_files.append({
                        'file_path': file_path,
                        'file_id': file_id,
                        'status': 'success'
                    })
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")
                    errors.append({
                        'file_path': file_path,
                        'error': str(e)
                    })
            else:
                print(f"❌ File not found: {file_path}")
                errors.append({
                    'file_path': file_path,
                    'error': 'File not found'
                })
        
        # Print final summary
        self.print_final_summary(processed_files, errors)
    
    def print_final_summary(self, processed_files: List[Dict], errors: List[Dict]):
        """Print final processing summary."""
        print(f"\n🎯 Processing Complete!")
        print("=" * 50)
        print(f"✅ Successfully processed: {len(processed_files)} files")
        
        # Only show errors section if there are actual errors
        if errors:
            print(f"❌ Errors: {len(errors)} files")
        
        if processed_files:
            print(f"\n📋 Processed Files:")
            for file_info in processed_files:
                print(f"   ✅ {Path(file_info['file_path']).name} (ID: {file_info['file_id']})")
        
        if errors:
            print(f"\n❌ Errors:")
            for error_info in errors:
                print(f"   ❌ {Path(error_info['file_path']).name}: {error_info['error']}")
        
        # Show database summary
        print(f"\n📊 Database Summary:")
        files_summary = self.db.get_all_files_summary()
        print(f"   Total files in database: {len(files_summary)}")
        
        if files_summary:
            total_processing = sum(f['processing_count'] for f in files_summary)
            print(f"   Total processing events: {total_processing}")
            print(f"   Average processing per file: {total_processing/len(files_summary):.1f}")
    
def main():
    """Main function to run enhanced file processor."""
    processor = EnhancedFileProcessor()
    
    # Process all files
    processor.process_all_files()

if __name__ == "__main__":
    main() 