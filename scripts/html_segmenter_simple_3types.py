#!/usr/bin/env python3
"""
Simple HTML Segmenter - 3 Types Only
Uses regex to extract HTML, CSS, and JavaScript into 3 separate files.
"""

import re
from pathlib import Path


class SimpleHTMLSegmenter:
    def __init__(self):
        self.html_content = ""
        self.css_content = ""
        self.js_content = ""
    
    def segment_html_simple(self, html_content: str):
        """Segment HTML into 3 types: HTML, CSS, JS"""
        
        # Extract CSS blocks
        css_pattern = r'<style[^>]*>.*?</style>'
        css_matches = re.findall(css_pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.css_content = "\n\n".join(css_matches)
        
        # Extract JavaScript blocks
        js_pattern = r'<script[^>]*>.*?</script>'
        js_matches = re.findall(js_pattern, html_content, re.DOTALL | re.IGNORECASE)
        self.js_content = "\n\n".join(js_matches)
        
        # Extract HTML structure (everything else)
        # Remove CSS and JS blocks from HTML content
        html_clean = re.sub(css_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_clean = re.sub(js_pattern, '', html_clean, flags=re.DOTALL | re.IGNORECASE)
        self.html_content = html_clean
    
    def save_to_files(self, output_dir: Path):
        """Save the 3 content types to separate files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        # Save HTML content
        if self.html_content.strip():
            html_file = output_dir / "index_html_.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(self.html_content)
            saved_files.append(html_file)
        
        # Save CSS content
        if self.css_content.strip():
            css_file = output_dir / "index_style_.css"
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(self.css_content)
            saved_files.append(css_file)
        
        # Save JavaScript content
        if self.js_content.strip():
            js_file = output_dir / "index_script_.js"
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(self.js_content)
            saved_files.append(js_file)
        
        return saved_files
    
    def process_file(self, input_file: Path, output_dir: Path):
        """Process HTML file and save to 3 separate files"""
        print(f"Processing with simple 3-type approach: {input_file}")
        
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Segment HTML into 3 types
        self.segment_html_simple(html_content)
        print(f"✅ Simple segmentation completed")
        
        # Save to 3 files
        saved_files = self.save_to_files(output_dir)
        
        print(f"📁 Results saved to:")
        for file in saved_files:
            print(f"   {file}")
        
        return {
            'html_size': len(self.html_content),
            'css_size': len(self.css_content),
            'js_size': len(self.js_content)
        }


def main():
    # File paths
    input_file = Path("svituawww.github.io/index.html")
    output_dir = Path("svituawww.github.io/output")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        return
    
    # Process file with simple approach
    segmenter = SimpleHTMLSegmenter()
    results = segmenter.process_file(input_file, output_dir)
    
    print(f"\n📊 Simple 3-Type Summary:")
    print(f"   Input: {input_file}")
    print(f"   Output directory: {output_dir}")
    print(f"   HTML size: {results['html_size']} chars")
    print(f"   CSS size: {results['css_size']} chars")
    print(f"   JS size: {results['js_size']} chars")


if __name__ == "__main__":
    main() 