#!/usr/bin/env python3
"""
Test Enhanced Database Functionality
Simple test to isolate and fix the database issue
"""

import sys
from pathlib import Path

# Add current directory to path to import from scripts
sys.path.append(str(Path(__file__).parent))

from enhanced_tech_html_parser import EnhancedTechHTMLParserDatabase

def test_enhanced_database():
    """Test enhanced database functionality."""
    print("🧪 Testing Enhanced Database")
    print("=" * 40)
    
    # Initialize database
    db = EnhancedTechHTMLParserDatabase()
    print("✅ Database initialized")
    
    # Test file processing
    test_file = "input/test1.html"
    if Path(test_file).exists():
        print(f"\n📁 Testing file processing: {test_file}")
        
        try:
            # Process file with enhanced storage
            file_id = db.process_file_with_enhanced_storage(test_file)
            print(f"✅ File processed successfully, file_id: {file_id}")
            
            # Get file statistics
            stats = db.get_file_statistics(file_id)
            print(f"✅ File statistics retrieved")
            
            print(f"\n✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Test file not found: {test_file}")

if __name__ == "__main__":
    test_enhanced_database() 