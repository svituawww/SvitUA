#!/usr/bin/env python3
"""
Integration Test for Enhanced Image Attribute Extraction
Demonstrates integration with existing parser system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_regex import ImageAttributeExtractor

def test_integration_with_real_content():
    """Test the enhanced extraction with real HTML content."""
    
    # Sample real HTML content that might be found in the database
    real_html_samples = [
        # Sample from the original instruction
        '''<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" 
                alt="Літературний вечір" 
                srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, 
                        https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w, 
                        https://svituawww.github.io/uploads1/2025/06/3-1152x1536.png 1152w, 
                        https://svituawww.github.io/uploads1/2025/06/3-9x12.png 9w, 
                        https://svituawww.github.io/uploads1/2025/06/3.png 1280w" 
                sizes="(max-width: 768px) 100vw, 400px">''',
        
        # Team member image
        '<img src="https://svituawww.github.io/uploads1/2025/06/01-4-824x1024.jpg" alt="Team Member" class="team-photo">',
        
        # Logo image
        '<img src="https://svituawww.github.io/uploads1/2025/03/svitua_100x100.png" alt="SvitUA Logo">',
        
        # Responsive image
        '<img src="https://svituawww.github.io/uploads1/2025/06/03.png" alt="Event Photo" srcset="https://svituawww.github.io/uploads1/2025/06/03-150x150.png 150w, https://svituawww.github.io/uploads1/2025/06/03-300x300.png 300w" sizes="(max-width: 600px) 100vw, 50vw">'
    ]
    
    extractor = ImageAttributeExtractor()
    
    print("Integration Test: Enhanced Image Extraction with Real Content")
    print("=" * 70)
    
    for i, html_content in enumerate(real_html_samples, 1):
        print(f"\n--- Real Content Test {i} ---")
        print(f"HTML: {html_content}")
        
        # Extract attributes
        extracted = extractor.extract_img_from_element(html_content)
        validation = extractor.validate_img_extraction(html_content)
        
        print(f"\nExtracted Attributes:")
        for element_type, attr_name, attr_value in extracted:
            print(f"  {attr_name}: {attr_value}")
        
        print(f"\nValidation Results:")
        print(f"  Is img tag: {validation['is_img_tag']}")
        print(f"  Has required src: {validation['has_required_src']}")
        print(f"  Total attributes: {validation['attribute_count']}")
        
        # Show all attributes found
        print(f"  All attributes: {validation['all_attributes']}")

def test_database_integration_scenario():
    """Simulate how this would work with database content."""
    
    # Simulate content from content_tech_html table
    database_content_samples = [
        {
            'content_id': 1,
            'content_body': '<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Літературний вечір" srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w, https://svituawww.github.io/uploads1/2025/06/3-225x300.png 225w" sizes="(max-width: 768px) 100vw, 400px">',
            'file_id': 101,
            'pos_start': 1500,
            'pos_end': 1800
        },
        {
            'content_id': 2,
            'content_body': '<img src="https://svituawww.github.io/uploads1/2025/06/01-4-824x1024.jpg" alt="Team Member Photo">',
            'file_id': 102,
            'pos_start': 2200,
            'pos_end': 2400
        }
    ]
    
    extractor = ImageAttributeExtractor()
    
    print("\n" + "=" * 70)
    print("Database Integration Scenario Test")
    print("=" * 70)
    
    for record in database_content_samples:
        print(f"\n--- Database Record {record['content_id']} ---")
        print(f"File ID: {record['file_id']}")
        print(f"Position: {record['pos_start']} - {record['pos_end']}")
        print(f"Content: {record['content_body']}")
        
        # Extract attributes
        extracted = extractor.extract_img_from_element(record['content_body'])
        
        print(f"\nExtracted Attributes for Database Storage:")
        for element_type, attr_name, attr_value in extracted:
            print(f"  {element_type} | {attr_name} | {attr_value}")
        
        # Simulate storing in content_items_tech_html table
        print(f"\nSimulated Database Insert:")
        for element_type, attr_name, attr_value in extracted:
            print(f"  INSERT INTO content_items_tech_html (content_id, type_content, item_body) VALUES ({record['content_id']}, '{attr_name}', '{attr_value}');")

def test_performance_with_real_data():
    """Test performance with realistic data volumes."""
    
    extractor = ImageAttributeExtractor()
    
    # Create realistic test data
    base_img = '<img src="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png" alt="Test Image" srcset="https://svituawww.github.io/uploads1/2025/06/3-768x1024.png 768w" sizes="100vw">'
    
    # Simulate processing 1000 content records
    test_data = [base_img] * 1000
    
    print("\n" + "=" * 70)
    print("Performance Test with Realistic Data Volume")
    print("=" * 70)
    
    import time
    start_time = time.time()
    
    total_attributes = 0
    for i, html_content in enumerate(test_data):
        extracted = extractor.extract_img_from_element(html_content)
        total_attributes += len(extracted)
        
        if i % 100 == 0:
            print(f"Processed {i} records...")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\nPerformance Results:")
    print(f"  Total records processed: {len(test_data)}")
    print(f"  Total attributes extracted: {total_attributes}")
    print(f"  Processing time: {processing_time:.4f} seconds")
    print(f"  Average time per record: {processing_time/len(test_data):.6f} seconds")
    print(f"  Records per second: {len(test_data)/processing_time:.2f}")

if __name__ == "__main__":
    # Run all integration tests
    test_integration_with_real_content()
    test_database_integration_scenario()
    test_performance_with_real_data()
    
    print("\n" + "=" * 70)
    print("INTEGRATION TESTING COMPLETE")
    print("=" * 70) 