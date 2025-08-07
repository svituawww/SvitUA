#!/usr/bin/env python3
"""
Test Implementation for id_part1 - Pre-Parsing Content Extraction Phase

This script implements the complete workflow for extracting external JavaScript and CSS files
from HTML files before the main parsing process begins.

Features:
- HTML file analysis for external scripts and styles
- Content download and extraction with error handling
- File naming with content hash for deduplication
- HTML file updates with backup creation
- Comprehensive testing framework
- Progress reporting and logging
"""

import re
import os
import sys
import hashlib
import shutil
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from pathlib import Path


class HTMLContentExtractor:
    """Main class for extracting external content from HTML files."""
    
    def __init__(self, input_dir: str, base_url: str = None):
        """
        Initialize the HTML content extractor.
        
        Args:
            input_dir (str): Directory for extracted files
            base_url (str): Base URL for relative resource paths
        """
        self.input_dir = input_dir
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; HTML-Parser/1.0)',
            'Accept': '*/*'
        })
        
        # Ensure input directory exists
        os.makedirs(input_dir, exist_ok=True)
    
    def analyze_html_file(self, file_path: str) -> Dict[str, any]:
        """
        Analyze HTML file for external scripts and styles with validation.
        
        Args:
            file_path (str): Path to HTML file
            
        Returns:
            dict: Analysis results with scripts, styles, and validation info
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"HTML file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Enhanced patterns for better matching
        script_pattern = r'<script[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        scripts = re.findall(script_pattern, content, re.IGNORECASE)
        
        # Multiple style patterns for different link formats
        style_patterns = [
            r'<link[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*rel\s*=\s*["\']stylesheet["\'][^>]*>',
            r'<style[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        ]
        
        styles = []
        for pattern in style_patterns:
            styles.extend(re.findall(pattern, content, re.IGNORECASE))
        
        # Remove duplicates while preserving order
        styles = list(dict.fromkeys(styles))
        
        return {
            'scripts': scripts,
            'styles': styles,
            'original_content': content,
            'file_size': len(content),
            'script_count': len(scripts),
            'style_count': len(styles)
        }
    
    def download_or_copy_content(self, url: str, timeout: int = 30) -> str:
        """
        Download content from URL or copy from local file.
        
        Args:
            url (str): URL or file path
            timeout (int): Request timeout in seconds
            
        Returns:
            str: Downloaded/copied content
        """
        # Handle relative URLs
        if self.base_url and not url.startswith(('http://', 'https://', 'file://')):
            url = urljoin(self.base_url, url)
        
        # Local file handling
        if url.startswith('file://') or not url.startswith(('http://', 'https://')):
            local_path = url.replace('file://', '') if url.startswith('file://') else url
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise FileNotFoundError(f"Local file not found: {local_path}")
        
        # HTTP/HTTPS download
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to download {url}: {str(e)}")
    
    def extract_external_content(self, html_file: str) -> Dict[str, any]:
        """
        Extract external JavaScript and CSS files with enhanced error handling.
        
        Args:
            html_file (str): Path to HTML file
            
        Returns:
            dict: Extraction results with file paths and replacements
        """
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(html_file))[0]
        current_date = datetime.now().strftime('%Y%m%d')
        
        analysis = self.analyze_html_file(html_file)
        results = {
            'extracted_scripts': [],
            'extracted_styles': [],
            'replacements': [],
            'errors': [],
            'warnings': [],
            'summary': {
                'total_resources': analysis['script_count'] + analysis['style_count'],
                'successful_extractions': 0,
                'failed_extractions': 0
            }
        }
        
        # Extract scripts with enhanced error handling
        for i, script_url in enumerate(analysis['scripts']):
            try:
                # Generate unique filename with content hash
                script_content = self.download_or_copy_content(script_url)
                content_hash = hashlib.md5(script_content.encode()).hexdigest()[:8]
                script_filename = f"{base_name}_js_{current_date}_{i+1}_{content_hash}.js"
                script_path = os.path.join(self.input_dir, script_filename)
                
                # Write script content
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                
                results['extracted_scripts'].append({
                    'original_url': script_url,
                    'local_path': script_path,
                    'filename': script_filename,
                    'size': len(script_content),
                    'hash': content_hash
                })
                
                # Create replacement comment with metadata
                replacement = f'<!-- EXTRACTED_SCRIPT: {script_filename} | Original: {script_url} | Size: {len(script_content)} bytes -->'
                results['replacements'].append({
                    'original': f'<script[^>]*src\s*=\s*["\']{re.escape(script_url)}["\'][^>]*>',
                    'replacement': replacement,
                    'type': 'script'
                })
                
                results['summary']['successful_extractions'] += 1
                
            except Exception as e:
                error_msg = f"Failed to extract script {script_url}: {str(e)}"
                results['errors'].append(error_msg)
                results['summary']['failed_extractions'] += 1
                
                # Add warning replacement
                replacement = f'<!-- EXTRACTION_FAILED: {script_url} | Error: {str(e)} -->'
                results['replacements'].append({
                    'original': f'<script[^>]*src\s*=\s*["\']{re.escape(script_url)}["\'][^>]*>',
                    'replacement': replacement,
                    'type': 'script_failed'
                })
        
        # Extract styles with enhanced error handling
        for i, style_url in enumerate(analysis['styles']):
            try:
                # Generate unique filename with content hash
                style_content = self.download_or_copy_content(style_url)
                content_hash = hashlib.md5(style_content.encode()).hexdigest()[:8]
                style_filename = f"{base_name}_css_{current_date}_{i+1}_{content_hash}.css"
                style_path = os.path.join(self.input_dir, style_filename)
                
                # Write style content
                with open(style_path, 'w', encoding='utf-8') as f:
                    f.write(style_content)
                
                results['extracted_styles'].append({
                    'original_url': style_url,
                    'local_path': style_path,
                    'filename': style_filename,
                    'size': len(style_content),
                    'hash': content_hash
                })
                
                # Create replacement comment with metadata
                replacement = f'<!-- EXTRACTED_STYLE: {style_filename} | Original: {style_url} | Size: {len(style_content)} bytes -->'
                results['replacements'].append({
                    'original': f'<link[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*href\s*=\s*["\']{re.escape(style_url)}["\'][^>]*>',
                    'replacement': replacement,
                    'type': 'style'
                })
                
                results['summary']['successful_extractions'] += 1
                
            except Exception as e:
                error_msg = f"Failed to extract style {style_url}: {str(e)}"
                results['errors'].append(error_msg)
                results['summary']['failed_extractions'] += 1
                
                # Add warning replacement
                replacement = f'<!-- EXTRACTION_FAILED: {style_url} | Error: {str(e)} -->'
                results['replacements'].append({
                    'original': f'<link[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*href\s*=\s*["\']{re.escape(style_url)}["\'][^>]*>',
                    'replacement': replacement,
                    'type': 'style_failed'
                })
        
        return results
    
    def update_html_file(self, html_file: str, replacements: List[Dict], create_backup: bool = True) -> Dict[str, any]:
        """
        Update HTML file with extracted content replacements and create backup.
        
        Args:
            html_file (str): Path to HTML file
            replacements (list): List of replacement rules
            create_backup (bool): Whether to create backup before modification
            
        Returns:
            dict: Update results with statistics
        """
        results = {
            'original_file': html_file,
            'backup_file': None,
            'replacements_applied': 0,
            'errors': [],
            'warnings': []
        }
        
        # Create backup if requested
        if create_backup:
            backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{html_file}.backup_{backup_suffix}"
            try:
                shutil.copy2(html_file, backup_file)
                results['backup_file'] = backup_file
            except Exception as e:
                results['warnings'].append(f"Failed to create backup: {str(e)}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements with validation
            for replacement in replacements:
                try:
                    new_content = re.sub(
                        replacement['original'],
                        replacement['replacement'],
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    if new_content != content:
                        content = new_content
                        results['replacements_applied'] += 1
                    else:
                        results['warnings'].append(f"No match found for pattern: {replacement['original']}")
                        
                except Exception as e:
                    results['errors'].append(f"Replacement failed: {str(e)}")
            
            # Write updated content back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            results['content_changed'] = content != original_content
            results['final_size'] = len(content)
            
        except Exception as e:
            results['errors'].append(f"File update failed: {str(e)}")
        
        return results
    
    def process_html_extraction(self, html_file: str) -> Dict[str, any]:
        """
        Complete workflow for HTML external content extraction.
        
        Args:
            html_file (str): Path to HTML file
            
        Returns:
            dict: Complete processing results
        """
        print(f"🔄 Starting extraction for: {html_file}")
        
        # Step 1: Analyze file
        print("📊 Analyzing HTML file...")
        analysis = self.analyze_html_file(html_file)
        print(f"   Found {analysis['script_count']} scripts and {analysis['style_count']} styles")
        
        # Step 2: Extract content
        print("📥 Extracting external content...")
        extraction_results = self.extract_external_content(html_file)
        
        # Step 3: Update HTML file
        print("✏️  Updating HTML file...")
        update_results = self.update_html_file(html_file, extraction_results['replacements'])
        
        # Combine results
        final_results = {
            'analysis': analysis,
            'extraction': extraction_results,
            'update': update_results,
            'summary': {
                'total_resources': analysis['script_count'] + analysis['style_count'],
                'successful_extractions': extraction_results['summary']['successful_extractions'],
                'failed_extractions': extraction_results['summary']['failed_extractions'],
                'replacements_applied': update_results['replacements_applied']
            }
        }
        
        # Print summary
        print(f"✅ Extraction complete!")
        print(f"   📁 Extracted: {final_results['summary']['successful_extractions']} files")
        print(f"   ❌ Failed: {final_results['summary']['failed_extractions']} files")
        print(f"   🔄 Applied: {final_results['summary']['replacements_applied']} replacements")
        
        if extraction_results['errors']:
            print(f"   ⚠️  Errors: {len(extraction_results['errors'])}")
            for error in extraction_results['errors'][:3]:  # Show first 3 errors
                print(f"      - {error}")
        
        return final_results


class HTMLContentExtractorTests:
    """Test suite for HTML content extraction functionality."""
    
    @staticmethod
    def test_analyze_html_file():
        """Test HTML file analysis functionality."""
        print("\n🧪 Testing HTML file analysis...")
        
        # Test with sample HTML content
        test_html = '''
        <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
                <style src="local-style.css"></style>
            </head>
            <body>
                <script src="app.js"></script>
            </body>
        </html>
        '''
        
        # Create temporary test file
        with open('test_file.html', 'w') as f:
            f.write(test_html)
        
        try:
            extractor = HTMLContentExtractor('test_output')
            analysis = extractor.analyze_html_file('test_file.html')
            
            # Validate results
            assert analysis['script_count'] == 2, f"Expected 2 scripts, got {analysis['script_count']}"
            assert analysis['style_count'] == 2, f"Expected 2 styles, got {analysis['style_count']}"
            assert 'jquery.min.js' in analysis['scripts'][0], "jQuery script not found"
            assert 'bootstrap.min.css' in analysis['styles'][0], "Bootstrap style not found"
            
            print("✅ HTML analysis test passed")
            return True
            
        except Exception as e:
            print(f"❌ HTML analysis test failed: {e}")
            return False
        finally:
            if os.path.exists('test_file.html'):
                os.remove('test_file.html')
    
    @staticmethod
    def test_download_content():
        """Test content download functionality."""
        print("\n🧪 Testing content download...")
        
        # Test local file handling
        test_content = "console.log('test');"
        with open('test_script.js', 'w') as f:
            f.write(test_content)
        
        try:
            extractor = HTMLContentExtractor('test_output')
            downloaded = extractor.download_or_copy_content('test_script.js')
            assert downloaded == test_content, "Downloaded content doesn't match"
            print("✅ Content download test passed")
            return True
        except Exception as e:
            print(f"❌ Content download test failed: {e}")
            return False
        finally:
            if os.path.exists('test_script.js'):
                os.remove('test_script.js')
    
    @staticmethod
    def test_extraction_workflow():
        """Test complete extraction workflow."""
        print("\n🧪 Testing extraction workflow...")
        
        # Create test HTML with external resources
        test_html = '''
        <html>
            <head>
                <script src="https://example.com/script.js"></script>
                <link rel="stylesheet" href="https://example.com/style.css">
            </head>
        </html>
        '''
        
        with open('test_workflow.html', 'w') as f:
            f.write(test_html)
        
        try:
            # Mock the download function for testing
            def mock_download(url):
                if 'script.js' in url:
                    return "console.log('test script');"
                elif 'style.css' in url:
                    return "body { color: red; }"
                else:
                    raise Exception("Unknown URL")
            
            # Create extractor and replace download method
            extractor = HTMLContentExtractor('test_output')
            original_download = extractor.download_or_copy_content
            extractor.download_or_copy_content = mock_download
            
            try:
                results = extractor.process_html_extraction('test_workflow.html')
                
                # Validate results
                assert results['summary']['successful_extractions'] == 2, "Expected 2 successful extractions"
                assert results['summary']['replacements_applied'] == 2, "Expected 2 replacements applied"
                assert len(results['extraction']['extracted_scripts']) == 1, "Expected 1 extracted script"
                assert len(results['extraction']['extracted_styles']) == 1, "Expected 1 extracted style"
                
                print("✅ Extraction workflow test passed")
                return True
                
            finally:
                # Restore original function
                extractor.download_or_copy_content = original_download
                
        except Exception as e:
            print(f"❌ Extraction workflow test failed: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists('test_workflow.html'):
                os.remove('test_workflow.html')
            if os.path.exists('test_output'):
                shutil.rmtree('test_output')
    
    @staticmethod
    def run_integration_tests():
        """Run comprehensive integration tests."""
        print("\n🧪 Running integration tests...")
        
        test_cases = [
            {
                'name': 'Basic HTML with external resources',
                'html': '''
                    <html>
                        <head>
                            <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
                            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
                        </head>
                        <body>
                            <h1>Test Page</h1>
                        </body>
                    </html>
                ''',
                'expected_scripts': 1,
                'expected_styles': 1
            },
            {
                'name': 'HTML with inline and external resources',
                'html': '''
                    <html>
                        <head>
                            <script>console.log('inline');</script>
                            <script src="external.js"></script>
                            <style>body { margin: 0; }</style>
                            <link rel="stylesheet" href="external.css">
                        </head>
                    </html>
                ''',
                'expected_scripts': 1,
                'expected_styles': 1
            },
            {
                'name': 'HTML with relative URLs',
                'html': '''
                    <html>
                        <head>
                            <script src="./js/app.js"></script>
                            <link rel="stylesheet" href="./css/style.css">
                        </head>
                    </html>
                ''',
                'expected_scripts': 1,
                'expected_styles': 1
            }
        ]
        
        extractor = HTMLContentExtractor('test_output')
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            try:
                # Create test file
                test_file = f"test_{test_case['name'].replace(' ', '_').lower()}.html"
                with open(test_file, 'w') as f:
                    f.write(test_case['html'])
                
                # Run analysis
                analysis = extractor.analyze_html_file(test_file)
                
                # Validate results
                if (analysis['script_count'] == test_case['expected_scripts'] and 
                    analysis['style_count'] == test_case['expected_styles']):
                    print(f"✅ {test_case['name']} - PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_case['name']} - FAILED")
                    print(f"   Expected: {test_case['expected_scripts']} scripts, {test_case['expected_styles']} styles")
                    print(f"   Got: {analysis['script_count']} scripts, {analysis['style_count']} styles")
                
                # Cleanup
                os.remove(test_file)
                
            except Exception as e:
                print(f"❌ {test_case['name']} - ERROR: {e}")
        
        print(f"\n📊 Integration Test Results: {passed}/{total} passed")
        return passed == total


def main():
    """Main function to run the test implementation."""
    print("🚀 Starting id_part1 Test Implementation")
    print("=" * 50)
    
    # Run all tests
    tests = HTMLContentExtractorTests()
    
    # Unit tests
    test_results = []
    test_results.append(tests.test_analyze_html_file())
    test_results.append(tests.test_download_content())
    test_results.append(tests.test_extraction_workflow())
    
    # Integration tests
    integration_passed = tests.run_integration_tests()
    test_results.append(integration_passed)
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print("\n" + "=" * 50)
    print(f"📊 Final Test Results: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Implementation is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 