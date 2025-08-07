#!/usr/bin/env python3
"""
Test script for id_part1 inline content extraction implementation

This script tests the InlineContentExtractor class with various HTML content scenarios
to ensure it correctly extracts inline JavaScript and CSS content.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from inline_content_extractor import InlineContentExtractor


class InlineContentExtractorTests:
    """Test suite for inline content extraction functionality."""
    
    def __init__(self):
        """Initialize test environment."""
        self.test_dir = None
        self.config_file = None
        self.extractor = None
    
    def setup_test_environment(self):
        """Set up test environment with temporary files."""
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp(prefix="inline_extraction_test_")
        
        # Create test configuration
        self.config_file = os.path.join(self.test_dir, "tech_tag_config.json")
        config = {
            "input_dir": os.path.join(self.test_dir, "input"),
            "output_dir": os.path.join(self.test_dir, "output")
        }
        
        with open(self.config_file, 'w') as f:
            import json
            json.dump(config, f, indent=2)
        
        # Create input directory
        os.makedirs(config["input_dir"], exist_ok=True)
        
        # Initialize extractor
        self.extractor = InlineContentExtractor(self.config_file)
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_analyze_inline_content_basic(self):
        """Test basic inline content analysis."""
        print("🧪 Testing basic inline content analysis...")
        
        html_content = '''
        <html>
            <head>
                <script>console.log('inline script 1');</script>
                <style>body { color: red; }</style>
                <script>console.log('inline script 2');</script>
                <style>p { margin: 10px; }</style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        analysis = self.extractor.analyze_inline_content(html_content)
        
        # Validate results
        assert len(analysis['inline_scripts']) == 2, f"Expected 2 inline scripts, got {len(analysis['inline_scripts'])}"
        assert len(analysis['inline_styles']) == 2, f"Expected 2 inline styles, got {len(analysis['inline_styles'])}"
        assert analysis['total_scripts'] == 2, f"Expected 2 total scripts, got {analysis['total_scripts']}"
        assert analysis['total_styles'] == 2, f"Expected 2 total styles, got {analysis['total_styles']}"
        
        print("✅ Basic inline content analysis test passed")
        return True
    
    def test_analyze_inline_content_with_external(self):
        """Test inline content analysis with external resources."""
        print("🧪 Testing inline content analysis with external resources...")
        
        html_content = '''
        <html>
            <head>
                <script src="external.js"></script>
                <script>console.log('inline script');</script>
                <link rel="stylesheet" href="external.css">
                <style>body { color: red; }</style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        analysis = self.extractor.analyze_inline_content(html_content)
        
        # Validate results
        assert len(analysis['inline_scripts']) == 1, f"Expected 1 inline script, got {len(analysis['inline_scripts'])}"
        assert len(analysis['inline_styles']) == 1, f"Expected 1 inline style, got {len(analysis['inline_styles'])}"
        assert len(analysis['external_scripts']) == 1, f"Expected 1 external script, got {len(analysis['external_scripts'])}"
        assert len(analysis['external_styles']) == 1, f"Expected 1 external style, got {len(analysis['external_styles'])}"
        
        print("✅ Inline content analysis with external resources test passed")
        return True
    
    def test_extract_inline_content(self):
        """Test complete inline content extraction."""
        print("🧪 Testing complete inline content extraction...")
        
        # Create test HTML file
        test_html = '''
        <html>
            <head>
                <script>console.log('inline script 1');</script>
                <style>body { color: red; }</style>
                <script>console.log('inline script 2');</script>
                <style>p { margin: 10px; }</style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        test_html_file = os.path.join(self.test_dir, "test_page.html")
        with open(test_html_file, 'w') as f:
            f.write(test_html)
        
        # Get initial file count
        initial_script_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.js')])
        initial_style_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.css')])
        
        # Extract content
        extraction_results = self.extractor.extract_inline_content(test_html_file)
        
        # Validate results
        assert extraction_results['summary']['successful_extractions'] == 4, f"Expected 4 successful extractions, got {extraction_results['summary']['successful_extractions']}"
        assert len(extraction_results['extracted_scripts']) == 2, f"Expected 2 extracted scripts, got {len(extraction_results['extracted_scripts'])}"
        assert len(extraction_results['extracted_styles']) == 2, f"Expected 2 extracted styles, got {len(extraction_results['extracted_styles'])}"
        
        # Check file naming (only count new files created by this test)
        final_script_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.js')])
        final_style_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.css')])
        
        new_script_files = final_script_files - initial_script_files
        new_style_files = final_style_files - initial_style_files
        
        assert new_script_files == 2, f"Expected 2 new JS files, got {new_script_files}"
        assert new_style_files == 2, f"Expected 2 new CSS files, got {new_style_files}"
        
        # Check file naming format
        script_files = [f for f in os.listdir(self.extractor.input_dir) if f.endswith('.js')][-2:]  # Get last 2 files
        style_files = [f for f in os.listdir(self.extractor.input_dir) if f.endswith('.css')][-2:]  # Get last 2 files
        
        for script_file in script_files:
            assert script_file.startswith('test_page_js_'), f"Script file {script_file} doesn't match naming pattern"
            assert script_file.endswith('.js'), f"Script file {script_file} doesn't have .js extension"
        
        for style_file in style_files:
            assert style_file.startswith('test_page_css_'), f"Style file {style_file} doesn't match naming pattern"
            assert style_file.endswith('.css'), f"Style file {style_file} doesn't have .css extension"
        
        print("✅ Complete inline content extraction test passed")
        return True
    
    def test_update_html_with_extractions(self):
        """Test HTML file update with extractions."""
        print("🧪 Testing HTML file update with extractions...")
        
        # Create test HTML file
        test_html = '''
        <html>
            <head>
                <script>console.log('inline script');</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        test_html_file = os.path.join(self.test_dir, "test_update.html")
        with open(test_html_file, 'w') as f:
            f.write(test_html)
        
        # Create replacements
        replacements = [
            {
                'original': r'<script>console\.log\(\'inline script\'\);</script>',
                'replacement': '<!-- EXTRACTED_INLINE_SCRIPT: test_update_js_20241204_1.js | Size: 35 bytes -->',
                'type': 'inline_script',
                'index': 0
            },
            {
                'original': r'<style>body \{ color: red; \}</style>',
                'replacement': '<!-- EXTRACTED_INLINE_STYLE: test_update_css_20241204_1.css | Size: 22 bytes -->',
                'type': 'inline_style',
                'index': 0
            }
        ]
        
        # Update HTML file
        update_results = self.extractor.update_html_with_extractions(test_html_file, replacements)
        
        # Validate results
        assert update_results['replacements_applied'] == 2, f"Expected 2 replacements applied, got {update_results['replacements_applied']}"
        assert update_results['backup_file'] is not None, "Backup file should be created"
        assert os.path.exists(update_results['backup_file']), "Backup file should exist"
        
        # Check updated content
        with open(test_html_file, 'r') as f:
            updated_content = f.read()
        
        assert '<!-- EXTRACTED_INLINE_SCRIPT:' in updated_content, "Script replacement not found"
        assert '<!-- EXTRACTED_INLINE_STYLE:' in updated_content, "Style replacement not found"
        assert '<script>console.log' not in updated_content, "Original script should be replaced"
        assert '<style>body {' not in updated_content, "Original style should be replaced"
        
        print("✅ HTML file update with extractions test passed")
        return True
    
    def test_process_inline_extraction_complete(self):
        """Test complete inline extraction workflow."""
        print("🧪 Testing complete inline extraction workflow...")
        
        # Create test HTML file
        test_html = '''
        <html>
            <head>
                <script>console.log('inline script 1');</script>
                <style>body { color: red; }</style>
                <script>console.log('inline script 2');</script>
                <style>p { margin: 10px; }</style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        test_html_file = os.path.join(self.test_dir, "test_complete.html")
        with open(test_html_file, 'w') as f:
            f.write(test_html)
        
        # Get initial file count
        initial_script_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.js')])
        initial_style_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.css')])
        
        # Process complete extraction
        results = self.extractor.process_inline_extraction(test_html_file)
        
        # Validate results
        assert results['summary']['successful_extractions'] == 4, f"Expected 4 successful extractions, got {results['summary']['successful_extractions']}"
        assert results['summary']['replacements_applied'] == 4, f"Expected 4 replacements applied, got {results['summary']['replacements_applied']}"
        assert results['summary']['inline_scripts_found'] == 2, f"Expected 2 inline scripts found, got {results['summary']['inline_scripts_found']}"
        assert results['summary']['inline_styles_found'] == 2, f"Expected 2 inline styles found, got {results['summary']['inline_styles_found']}"
        
        # Check extracted files (only count new files created by this test)
        final_script_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.js')])
        final_style_files = len([f for f in os.listdir(self.extractor.input_dir) if f.endswith('.css')])
        
        new_script_files = final_script_files - initial_script_files
        new_style_files = final_style_files - initial_style_files
        
        assert new_script_files == 2, f"Expected 2 new JS files, got {new_script_files}"
        assert new_style_files == 2, f"Expected 2 new CSS files, got {new_style_files}"
        
        print("✅ Complete inline extraction workflow test passed")
        return True
    
    def test_empty_inline_content(self):
        """Test handling of empty inline content."""
        print("🧪 Testing empty inline content handling...")
        
        html_content = '''
        <html>
            <head>
                <script></script>
                <style></style>
                <script>   </script>
                <style>   </style>
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        analysis = self.extractor.analyze_inline_content(html_content)
        
        # Empty content should be filtered out
        assert len(analysis['inline_scripts']) == 0, f"Expected 0 inline scripts, got {len(analysis['inline_scripts'])}"
        assert len(analysis['inline_styles']) == 0, f"Expected 0 inline styles, got {len(analysis['inline_styles'])}"
        
        print("✅ Empty inline content handling test passed")
        return True
    
    def test_external_only_content(self):
        """Test handling of HTML with only external resources."""
        print("🧪 Testing external-only content handling...")
        
        html_content = '''
        <html>
            <head>
                <script src="external.js"></script>
                <link rel="stylesheet" href="external.css">
            </head>
            <body>
                <h1>Test Page</h1>
            </body>
        </html>
        '''
        
        analysis = self.extractor.analyze_inline_content(html_content)
        
        # Should only find external resources
        assert len(analysis['inline_scripts']) == 0, f"Expected 0 inline scripts, got {len(analysis['inline_scripts'])}"
        assert len(analysis['inline_styles']) == 0, f"Expected 0 inline styles, got {len(analysis['inline_styles'])}"
        assert len(analysis['external_scripts']) == 1, f"Expected 1 external script, got {len(analysis['external_scripts'])}"
        assert len(analysis['external_styles']) == 1, f"Expected 1 external style, got {len(analysis['external_styles'])}"
        
        print("✅ External-only content handling test passed")
        return True
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("🚀 Starting id_part1 Inline Content Extraction Tests")
        print("=" * 60)
        
        try:
            self.setup_test_environment()
            
            test_results = []
            test_results.append(self.test_analyze_inline_content_basic())
            test_results.append(self.test_analyze_inline_content_with_external())
            test_results.append(self.test_extract_inline_content())
            test_results.append(self.test_update_html_with_extractions())
            test_results.append(self.test_process_inline_extraction_complete())
            test_results.append(self.test_empty_inline_content())
            test_results.append(self.test_external_only_content())
            
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            print("\n" + "=" * 60)
            print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                print("🎉 All tests passed! id_part1 implementation is working correctly.")
                return True
            else:
                print("⚠️  Some tests failed. Please review the implementation.")
                return False
                
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
        finally:
            self.cleanup_test_environment()


def main():
    """Main function to run the test suite."""
    tests = InlineContentExtractorTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 