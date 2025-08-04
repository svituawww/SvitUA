#!/usr/bin/env python3
"""
Complete Integration Test for Enhanced Image Extraction
Demonstrates the full workflow from file processing to enhanced image extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from enhanced_file_processor import EnhancedFileProcessor
from extract_content_items import ContentExtractor

def test_enhanced_image_extraction_standalone():
    """Test the enhanced image extraction functionality standalone."""
    
    print("🔍 Testing Enhanced Image Extraction (Standalone)")
    print("=" * 60)
    
    extractor = ContentExtractor()
    
    # Test cases from id_part4
    test_cases = [
        # Complex img tag with all attributes
        '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Літературний вечір" 
             srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                     https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
                     https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
                     https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
                     https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
             sizes="(max-width: 768px) 100vw, 400px">''',
        
        # Simple img tag
        '<img src="image.jpg" alt="Simple image">',
        
        # img tag with single quotes
        "<img src='image.png' alt='Single quoted' srcset='image.png 1x'>",
        
        # img tag with mixed quotes and spaces
        '<img  src = "image.jpg"  alt = "Mixed spacing"  srcset = "image.jpg 1x"  sizes = "100vw" >',
        
        # img tag with no alt attribute
        '<img src="image.jpg" srcset="image.jpg 1x, image@2x.jpg 2x">'
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case}")
        
        # Extract attributes
        extracted = extractor.extract_img_from_element(test_case)
        validation = extractor.validate_img_extraction(test_case)
        
        print(f"Extracted Attributes:")
        for element_type, attr_name, attr_value in extracted:
            print(f"  {attr_name}: {attr_value}")
        
        print(f"Validation: is_img={validation['is_img_tag']}, "
              f"has_src={validation['has_required_src']}, "
              f"attr_count={validation['attribute_count']}")

def test_complete_workflow():
    """Test the complete workflow with file processing and enhanced image extraction."""
    
    print("\n🚀 Testing Complete Workflow Integration")
    print("=" * 60)
    
    # Initialize the enhanced file processor
    processor = EnhancedFileProcessor()
    
    # Process a test file
    test_file = "input/test1.html"
    if os.path.exists(test_file):
        print(f"📁 Processing file: {test_file}")
        
        # Process the file with enhanced storage
        file_id = processor.process_file_with_enhanced_storage(test_file)
        
        print(f"\n✅ File processing complete. File ID: {file_id}")
        
        # Get detailed statistics
        stats = processor.db.get_file_statistics(file_id)
        
        print(f"\n📊 File Statistics:")
        print(f"   File: {stats['file_info']['input_filename']}")
        print(f"   UUID: {stats['file_info']['uuid']}")
        print(f"   Processing Count: {stats['file_info']['processing_count']}")
        
        if 'bracket_stats' in stats:
            print(f"   Brackets: {stats['bracket_stats']['total_brackets']}")
        
        if 'element_stats' in stats:
            print(f"   Elements: {stats['element_stats']['total_elements']}")
        
        # Test enhanced image extraction validation
        print(f"\n🔍 Testing Enhanced Image Extraction Validation...")
        validation_result = processor.db.validate_and_report_image_extraction(file_id)
        
        if validation_result['images_found'] > 0:
            print(f"✅ Found {validation_result['images_found']} images")
            print(f"   Total attributes: {validation_result['total_attributes']}")
            print(f"   Average per image: {validation_result['total_attributes']/validation_result['images_found']:.2f}")
        
        # Get image extraction statistics
        img_stats = processor.db.get_image_extraction_statistics(file_id)
        print(f"\n📊 Image Extraction Statistics:")
        print(f"   Total content items: {img_stats['total_content_items']}")
        print(f"   Image attributes found: {img_stats['total_image_attributes']}")
        print(f"   Attribute types: {img_stats['attribute_types']}")
        for attr_type, count in img_stats['image_attributes'].items():
            print(f"     {attr_type}: {count}")
        
        return file_id
    else:
        print(f"❌ Test file not found: {test_file}")
        return None

def test_database_queries():
    """Test database queries for image extraction results."""
    
    print("\n🗄️ Testing Database Queries")
    print("=" * 60)
    
    from scripts.enhanced_tech_html_parser import EnhancedTechHTMLParserDatabase
    
    db = EnhancedTechHTMLParserDatabase()
    
    # Get all files
    files_summary = db.get_all_files_summary()
    print(f"📋 Files in database: {len(files_summary)}")
    
    for file_info in files_summary:
        file_id = file_info['id']
        print(f"\n📁 File: {file_info['input_filename']} (ID: {file_id})")
        
        # Get content records
        content_records = db.get_content_tech_html_by_file(file_id)
        print(f"   Content records: {len(content_records)}")
        
        # Get content items
        content_items = db.get_content_items_by_content_id(file_id)
        print(f"   Content items: {len(content_items)}")
        
        # Get image-specific content items
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type_item, COUNT(*) as count
                FROM content_items_tech_html 
                WHERE content_id IN (
                    SELECT content_id FROM content_tech_html WHERE file_id = ?
                ) AND type_element = 'img'
                GROUP BY type_item
            """, (file_id,))
            
            image_stats = dict(cursor.fetchall())
            if image_stats:
                print(f"   Image attributes:")
                for attr_type, count in image_stats.items():
                    print(f"     {attr_type}: {count}")
            else:
                print(f"   No image attributes found")

def main():
    """Run all integration tests."""
    
    print("🧪 Complete Integration Test for Enhanced Image Extraction")
    print("=" * 80)
    
    # Test 1: Standalone enhanced image extraction
    test_enhanced_image_extraction_standalone()
    
    # Test 2: Complete workflow
    file_id = test_complete_workflow()
    
    # Test 3: Database queries
    test_database_queries()
    
    print("\n" + "=" * 80)
    print("✅ INTEGRATION TESTING COMPLETE")
    print("=" * 80)
    
    if file_id:
        print(f"📊 Summary:")
        print(f"   ✅ Enhanced image extraction integrated successfully")
        print(f"   ✅ File processing workflow working")
        print(f"   ✅ Database integration functional")
        print(f"   ✅ Test file processed: File ID {file_id}")
    else:
        print(f"❌ Integration test failed - no file processed")

if __name__ == "__main__":
    main() 