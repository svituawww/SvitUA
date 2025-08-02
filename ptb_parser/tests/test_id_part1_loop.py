#!/usr/bin/env python3
"""
Test script to demonstrate the loop from id_part1
Shows the loop that processes each record from tech_html_elements
"""

import sqlite3
from enhanced_tech_html_parser import EnhancedTechHTMLParserDatabase

def test_id_part1_loop():
    """Test the loop from id_part1 specification."""
    print("🔄 Testing Loop from id_part1")
    print("=" * 50)
    
    db = EnhancedTechHTMLParserDatabase()
    
    # Get available file_ids
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT file_id FROM tech_html_elements ORDER BY file_id")
        file_ids = [row[0] for row in cursor.fetchall()]
    
    if not file_ids:
        print("❌ No files found in tech_html_elements table")
        return
    
    print(f"📁 Available file_ids: {file_ids}")
    
    # Test the loop for first file
    first_file_id = file_ids[0]
    print(f"\n🔄 Testing loop for file_id: {first_file_id}")
    
    # This is the loop from id_part1 - it processes each record from the SQL query
    elements = db.get_tech_html_elements_by_file(first_file_id, limit=5)
    
    if not elements:
        print(f"❌ No tech HTML elements found for file_id: {first_file_id}")
        return
    
    print(f"📊 Found {len(elements)} elements to process")
    print("\n🔄 Starting loop from id_part1:")
    print("=" * 50)
    
    # This is the actual loop from id_part1
    for i, element in enumerate(elements):
        techhtml_id, pos_open, pos_close, file_id, type_ttag, name_tech_tag = element
        
        print(f"\n📝 Element {i+1}:")
        print(f"   techhtml_id: {techhtml_id}")
        print(f"   pos_open: {pos_open} -> pos_close: {pos_close}")
        print(f"   type: {type_ttag}")
        print(f"   name: {name_tech_tag}")
        
        # Create content record (this is what the loop does)
        content_body = f"Content between positions {pos_open} and {pos_close} - {name_tech_tag}"
        content_id = db.add_content_tech_html(
            file_id=file_id,
            techhtml_id_start=techhtml_id,
            techhtml_id_end=techhtml_id,
            pos_start=pos_open,
            pos_end=pos_close,
            content_body=content_body
        )
        
        print(f"   ✅ Created content_id: {content_id}")
    
    print(f"\n🎉 Loop from id_part1 complete!")
    print("=" * 50)
    
    # Show the results
    db.show_content_tech_html_records(first_file_id, limit=10)

if __name__ == "__main__":
    test_id_part1_loop() 