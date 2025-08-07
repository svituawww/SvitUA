#!/usr/bin/env python3
"""
Simple runner script for the Media Scanner
Execute this script to run the media scanning process.
"""

import sys
import os

# Add the scripts directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from media_scanner import process_media_scanning

def main():
    """Main function to run the media scanner."""
    print("🚀 Starting Media Scanner...")
    print("=" * 50)
    
    try:
        # Run the media scanning process
        results = process_media_scanning()
        
        print("\n" + "=" * 50)
        print("🎉 Media scanning completed successfully!")
        print(f"📊 Results saved to: {results['scan_configuration']['output_dir_json'][0]}")
        
        # Print detailed summary
        summary = results['scan_summary']
        print(f"\n📈 Detailed Summary:")
        print(f"   📁 Directories scanned: {summary['total_directories_scanned']}")
        print(f"   📄 Total files found: {summary['total_files_found']}")
        print(f"   🖼️  Media files processed: {summary['media_files_processed']}")
        print(f"   ⏭️  Files skipped: {summary['files_skipped']}")
        print(f"   ❌ Files with errors: {summary['files_with_errors']}")
        print(f"   💾 Total size: {summary['total_size_mb']} MB")
        print(f"   ⏱️  Processing time: {summary['processing_time_seconds']:.2f} seconds")
        
        # Print format statistics
        if results['scan_statistics']['supported_formats_found']:
            print(f"\n🎨 Image Formats Found:")
            for format_name, count in results['scan_statistics']['supported_formats_found'].items():
                print(f"   - {format_name}: {count} files")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during media scanning: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
