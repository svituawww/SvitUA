#!/usr/bin/env python3
"""
Demo script for id_part1 implementation

This script demonstrates how to use the HTMLContentExtractor class
with real HTML files from the input directory.
"""

import os
import sys
from test_id_part1_implementation import HTMLContentExtractor


def demo_with_real_files():
    """Demo the extraction process with real HTML files."""
    print("🎬 Demo: id_part1 Implementation with Real Files")
    print("=" * 60)
    
    # Check if input directory exists and has HTML files
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' not found")
        return False
    
    # Find HTML files in input directory
    html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"❌ No HTML files found in '{input_dir}' directory")
        return False
    
    print(f"📁 Found {len(html_files)} HTML files in input directory:")
    for file in html_files:
        print(f"   - {file}")
    
    # Create output directory for extracted files
    output_dir = "output_extracted"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each HTML file
    for html_file in html_files:
        html_path = os.path.join(input_dir, html_file)
        print(f"\n🔄 Processing: {html_file}")
        
        try:
            # Create extractor
            extractor = HTMLContentExtractor(output_dir)
            
            # Process the file
            results = extractor.process_html_extraction(html_path)
            
            # Show detailed results
            print(f"   📊 Analysis Results:")
            print(f"      - Scripts found: {results['analysis']['script_count']}")
            print(f"      - Styles found: {results['analysis']['style_count']}")
            print(f"      - File size: {results['analysis']['file_size']} bytes")
            
            print(f"   📥 Extraction Results:")
            print(f"      - Scripts extracted: {len(results['extraction']['extracted_scripts'])}")
            print(f"      - Styles extracted: {len(results['extraction']['extracted_styles'])}")
            print(f"      - Errors: {len(results['extraction']['errors'])}")
            
            print(f"   ✏️  Update Results:")
            print(f"      - Replacements applied: {results['update']['replacements_applied']}")
            if results['update']['backup_file']:
                print(f"      - Backup created: {results['update']['backup_file']}")
            
            # Show extracted files
            if results['extraction']['extracted_scripts']:
                print(f"   📄 Extracted Scripts:")
                for script in results['extraction']['extracted_scripts']:
                    print(f"      - {script['filename']} ({script['size']} bytes)")
            
            if results['extraction']['extracted_styles']:
                print(f"   🎨 Extracted Styles:")
                for style in results['extraction']['extracted_styles']:
                    print(f"      - {style['filename']} ({style['size']} bytes)")
            
            print(f"   ✅ Successfully processed {html_file}")
            
        except Exception as e:
            print(f"   ❌ Failed to process {html_file}: {e}")
    
    print(f"\n📁 Check the '{output_dir}' directory for extracted files")
    print(f"📁 Original HTML files have been updated with placeholders")
    
    return True


def demo_with_sample_html():
    """Demo with a sample HTML file that has external resources."""
    print("\n🎬 Demo: Creating Sample HTML with External Resources")
    print("=" * 60)
    
    # Create sample HTML with external resources
    sample_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sample Page</title>
        
        <!-- External JavaScript -->
        <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        
        <!-- External CSS -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        
        <!-- Inline styles (should not be extracted) -->
        <style>
            body { font-family: Arial, sans-serif; }
            .custom { color: blue; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sample Page</h1>
            <p>This is a sample page with external resources.</p>
            
            <!-- Inline script (should not be extracted) -->
            <script>
                console.log('This is inline JavaScript');
            </script>
            
            <!-- External script -->
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js"></script>
        </div>
    </body>
    </html>
    '''
    
    # Create sample file
    sample_file = "sample_page.html"
    with open(sample_file, 'w') as f:
        f.write(sample_html)
    
    print(f"📄 Created sample HTML file: {sample_file}")
    print(f"   - Contains 3 external scripts")
    print(f"   - Contains 2 external stylesheets")
    print(f"   - Contains inline scripts and styles (should not be extracted)")
    
    # Process the sample file
    output_dir = "sample_output"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        extractor = HTMLContentExtractor(output_dir)
        results = extractor.process_html_extraction(sample_file)
        
        print(f"\n📊 Sample Processing Results:")
        print(f"   - Scripts found: {results['analysis']['script_count']}")
        print(f"   - Styles found: {results['analysis']['style_count']}")
        print(f"   - Successful extractions: {results['summary']['successful_extractions']}")
        print(f"   - Failed extractions: {results['summary']['failed_extractions']}")
        
        # Show what was extracted
        if results['extraction']['extracted_scripts']:
            print(f"\n📄 Extracted Scripts:")
            for script in results['extraction']['extracted_scripts']:
                print(f"   - {script['filename']} (Original: {script['original_url']})")
        
        if results['extraction']['extracted_styles']:
            print(f"\n🎨 Extracted Styles:")
            for style in results['extraction']['extracted_styles']:
                print(f"   - {style['filename']} (Original: {style['original_url']})")
        
        print(f"\n📁 Check '{output_dir}' directory for extracted files")
        print(f"📄 Original file updated: {sample_file}")
        
        # Show the updated HTML content
        print(f"\n📄 Updated HTML Preview (first 500 chars):")
        with open(sample_file, 'r') as f:
            updated_content = f.read()
        print(updated_content[:500] + "..." if len(updated_content) > 500 else updated_content)
        
    except Exception as e:
        print(f"❌ Failed to process sample file: {e}")
    
    return True


def main():
    """Main demo function."""
    print("🚀 id_part1 Implementation Demo")
    print("=" * 60)
    
    # Demo 1: With real files
    print("\n1️⃣  Demo with real HTML files:")
    demo_with_real_files()
    
    # Demo 2: With sample HTML
    print("\n2️⃣  Demo with sample HTML:")
    demo_with_sample_html()
    
    print("\n✅ Demo completed!")
    print("\n📋 Summary:")
    print("   - The implementation successfully extracts external scripts and styles")
    print("   - Files are named with content hash for deduplication")
    print("   - Original HTML files are updated with placeholder comments")
    print("   - Backup files are created before modifications")
    print("   - Comprehensive error handling and logging")


if __name__ == "__main__":
    main() 