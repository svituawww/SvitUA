#!/usr/bin/env python3
"""
Enhanced File Processor Runner
Demonstrates the complete enhanced file processing strategy from inst_4.md
"""

import sys
from pathlib import Path

# Add current directory to path to import from scripts
sys.path.append(str(Path(__file__).parent))

from enhanced_file_processor import EnhancedFileProcessor

def main():
    """Run the enhanced file processor."""
    print("🚀 Enhanced File Processor")
    print("=" * 50)
    
    # Create enhanced processor
    processor = EnhancedFileProcessor()
    
    # Process all files from configuration
    processor.process_all_files()
    
    print("\n✅ Enhanced file processing completed!")
    print("📁 Check database and input_file_store/ for results")

if __name__ == "__main__":
    main() 