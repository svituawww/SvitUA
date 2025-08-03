#!/usr/bin/env python3
"""
Selenium-Based Selective HTML Content Filtering Test - id_part6 Fixed Implementation
Demonstrates precise text content replacement within HTML elements
"""

import sys
import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Set

# Add parent directory to path to import from scripts
sys.path.append(str(Path(__file__).parent.parent))

class SeleniumSelectiveFilterFixed:
    """Use Selenium to selectively filter and replace specific HTML content with precise text replacement."""
    
    def __init__(self):
        self.content_mapping = {}
        self.generated_uuids = set()
        self.filtered_elements = set()
        self.driver = None
    
    def setup_selenium_driver(self):
        """Setup Selenium WebDriver with Chrome options."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except ImportError:
            print("❌ Selenium not installed. Install with: pip install selenium")
            return None
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            return None
    
    def generate_unique_uuid(self) -> str:
        """Generate unique UUID with prefix."""
        while True:
            unique_id = f"uuid_{uuid.uuid4()}"
            if unique_id not in self.generated_uuids:
                self.generated_uuids.add(unique_id)
                return unique_id
    
    def define_filtering_rules(self) -> Dict[str, List[str]]:
        """Define specific filtering rules for content selection."""
        return {
            'sensitive_text': [
                '//title',                    # Page titles
                '//h1',                      # Main headings
                '//h2',                      # Sub headings
                '//h3',                      # Sub-sub headings
                '//p',                       # ALL paragraph elements
                '//meta[@name="description"]', # Meta descriptions
                '//div[@class="faq-answer"]',  # FAQ answers
                '//p[contains(@class, "sensitive")]',  # Sensitive paragraphs
                '//div[contains(@class, "private")]',  # Private content
                '//span[contains(@class, "personal")]' # Personal information
            ],
            'sensitive_attributes': [
                '//*[@data-sensitive="true"]',  # Elements with sensitive data
                '//*[@class="private"]',        # Private class elements
                '//*[@id="personal"]'           # Personal ID elements
            ],
            'content_selectors': [
                '//div[@class="container"]//text()',  # Container text content
                '//section[@class="private"]//text()', # Private section content
                '//article[@class="sensitive"]//text()' # Sensitive article content
            ]
        }
    
    def extract_specific_content_with_selenium(self, html_file_path: str) -> Dict[str, Any]:
        """Extract specific content using Selenium selectors."""
        
        if not self.driver:
            self.driver = self.setup_selenium_driver()
        if not self.driver:
            return None
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Load HTML file
            file_url = f"file://{Path(html_file_path).absolute()}"
            print(f"📁 Loading HTML file: {file_url}")
            
            self.driver.get(file_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("✅ HTML loaded successfully with Selenium")
            
            # Define filtering rules
            filtering_rules = self.define_filtering_rules()
            
            # Extract specific content based on rules
            extracted_content = {
                'sensitive_text': [],
                'sensitive_attributes': [],
                'content_selectors': []
            }
            
            # Extract sensitive text elements
            for xpath in filtering_rules['sensitive_text']:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        # Handle different element types
                        if element.tag_name == 'title':
                            # For title elements, get the innerHTML content
                            title_content = self.driver.execute_script("return arguments[0].innerHTML;", element)
                            if title_content.strip():
                                element_html = self.driver.execute_script("return arguments[0].outerHTML;", element)
                                
                                extracted_content['sensitive_text'].append({
                                    'element': element,
                                    'text': title_content.strip(),
                                    'tag_name': element.tag_name,
                                    'xpath': xpath,
                                    'element_html': element_html,
                                    'original_text': title_content.strip()
                                })
                        elif element.text.strip():
                            # For other elements, use text content
                            element_html = self.driver.execute_script("return arguments[0].outerHTML;", element)
                            
                            extracted_content['sensitive_text'].append({
                                'element': element,
                                'text': element.text.strip(),
                                'tag_name': element.tag_name,
                                'xpath': xpath,
                                'element_html': element_html,
                                'original_text': element.text.strip()
                            })
                except Exception as e:
                    print(f"⚠️  Error extracting from {xpath}: {e}")
            
            # Extract sensitive attributes
            for xpath in filtering_rules['sensitive_attributes']:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        attributes = self.driver.execute_script("""
                            var items = {};
                            for (index = 0; index < arguments[0].attributes.length; ++index) {
                                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value;
                            }
                            return items;
                        """, element)
                        
                        for attr_name, attr_value in attributes.items():
                            if attr_value.strip():
                                extracted_content['sensitive_attributes'].append({
                                    'element': element,
                                    'attribute_name': attr_name,
                                    'attribute_value': attr_value,
                                    'tag_name': element.tag_name
                                })
                except Exception as e:
                    print(f"⚠️  Error extracting attributes from {xpath}: {e}")
            
            # Extract content selectors
            for xpath in filtering_rules['content_selectors']:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.text.strip():
                            extracted_content['content_selectors'].append({
                                'element': element,
                                'text': element.text.strip(),
                                'tag_name': element.tag_name
                            })
                except Exception as e:
                    print(f"⚠️  Error extracting content from {xpath}: {e}")
            
            return extracted_content
            
        except Exception as e:
            print(f"❌ Error in Selenium extraction: {e}")
            return None
    
    def transform_specific_content(self, html_file_path: str) -> Dict[str, Any]:
        """Transform only specific content using Selenium filtering with precise text replacement."""
        
        # Import Selenium components
        from selenium.webdriver.common.by import By
        
        # Extract specific content with Selenium
        extracted_content = self.extract_specific_content_with_selenium(html_file_path)
        
        if not extracted_content:
            return None
        
        # Read original HTML
        with open(html_file_path, 'r', encoding='utf-8') as f:
            original_html = f.read()
        
        print(f"📄 Processing HTML file: {html_file_path}")
        print(f"📊 Original content length: {len(original_html)} characters")
        
        # Count extracted content
        total_sensitive_text = len(extracted_content['sensitive_text'])
        total_sensitive_attributes = len(extracted_content['sensitive_attributes'])
        total_content_selectors = len(extracted_content['content_selectors'])
        
        print(f"🔍 Found {total_sensitive_text} sensitive text elements")
        print(f"🎯 Found {total_sensitive_attributes} sensitive attributes")
        print(f"📋 Found {total_content_selectors} content selector elements")
        
        # Transform sensitive text with PRECISE replacement
        transformed_html = original_html
        text_mappings = {}
        
        # Sort items by position (descending) to avoid index shifting issues
        sorted_items = sorted(extracted_content['sensitive_text'], 
                            key=lambda x: len(x.get('element_html', '')), reverse=True)
        
        for item in sorted_items:
            original_text = item['original_text']
            element_html = item['element_html']
            tag_name = item['tag_name']
            
            if original_text.strip():
                uuid_text = self.generate_unique_uuid()
                text_mappings[uuid_text] = {
                    'type': 'sensitive_text',
                    'original': original_text,
                    'tag_name': tag_name,
                    'xpath': item.get('xpath', '')
                }
                
                # PRECISE REPLACEMENT: Replace only the text content within the element
                try:
                    # Create new element HTML with replaced text content
                    new_element_html = element_html.replace(original_text, uuid_text)
                    
                    # Replace the entire element HTML in the document
                    transformed_html = transformed_html.replace(element_html, new_element_html)
                    
                    print(f"✅ Replaced text in {tag_name}: '{original_text[:50]}...' → {uuid_text}")
                    
                except Exception as e:
                    print(f"⚠️  Error replacing text in {tag_name}: {e}")
                    # Fallback to simple replacement
                    transformed_html = transformed_html.replace(original_text, uuid_text, 1)
        
        # Transform sensitive attributes
        attr_mappings = {}
        
        for item in extracted_content['sensitive_attributes']:
            attr_value = item['attribute_value']
            if attr_value.strip():
                uuid_attr = self.generate_unique_uuid()
                attr_mappings[uuid_attr] = {
                    'type': 'sensitive_attribute',
                    'original': attr_value,
                    'attribute_name': item['attribute_name'],
                    'tag_name': item['tag_name']
                }
                
                # Replace attribute value in HTML
                transformed_html = transformed_html.replace(f'="{attr_value}"', f'="{uuid_attr}"')
        
        # Transform content selectors
        selector_mappings = {}
        
        for item in extracted_content['content_selectors']:
            text = item['text']
            if text.strip():
                uuid_selector = self.generate_unique_uuid()
                selector_mappings[uuid_selector] = {
                    'type': 'content_selector',
                    'original': text,
                    'tag_name': item['tag_name']
                }
                
                # Replace in HTML
                transformed_html = transformed_html.replace(text, uuid_selector, 1)
        
        # Combine all mappings
        self.content_mapping = {**text_mappings, **attr_mappings, **selector_mappings}
        
        return {
            'transformed_html': transformed_html,
            'content_mapping': self.content_mapping,
            'sensitive_text_count': total_sensitive_text,
            'sensitive_attributes_count': total_sensitive_attributes,
            'content_selectors_count': total_content_selectors,
            'total_replacements': len(self.content_mapping)
        }
    
    def save_selective_files(self, original_path: Path, result: Dict[str, Any]) -> Dict[str, str]:
        """Save selectively transformed HTML and mapping files."""
        
        # Generate unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(original_path.read_bytes()).hexdigest()[:8]
        
        # Save transformed HTML to test output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create filenames
        base_name = original_path.stem
        transformed_html_file = output_dir / f"selenium_fixed_{base_name}_{content_hash}_{timestamp}.html"
        mapping_json_file = output_dir / f"selenium_fixed_mapping_{base_name}_{content_hash}_{timestamp}.json"
        
        # Save transformed HTML
        with open(transformed_html_file, 'w', encoding='utf-8') as f:
            f.write(result['transformed_html'])
        
        # Save mapping JSON
        with open(mapping_json_file, 'w', encoding='utf-8') as f:
            json.dump(result['content_mapping'], f, ensure_ascii=False, indent=2)
        
        return {
            'transformed_html': str(transformed_html_file),
            'mapping_json': str(mapping_json_file)
        }
    
    def cleanup(self):
        """Clean up Selenium driver."""
        if self.driver:
            self.driver.quit()

def test_selenium_selective_filtering_fixed():
    """Test the fixed Selenium selective filtering implementation."""
    
    print("🧪 Selenium-Based Selective Filtering Test Suite - id_part6 Fixed")
    print("=" * 70)
    
    # Test filtering rules
    test_filtering_rules()
    
    # Test UUID generation
    test_uuid_generation()
    
    # Initialize filter
    selective_filter = SeleniumSelectiveFilterFixed()
    
    # Find HTML file to process
    input_dir = Path(__file__).parent.parent / "input"
    html_files = list(input_dir.glob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found in input directory")
        return None
    
    html_file_path = html_files[0]  # Use first HTML file
    print(f"🧪 Selenium Selective Content Filtering Test - id_part6 Fixed")
    print("=" * 60)
    
    # Transform content
    result = selective_filter.transform_specific_content(str(html_file_path))
    
    if not result:
        print("❌ Failed to transform content")
        return None
    
    # Print results
    print(f"\n📊 Selective Filtering Results:")
    print("-" * 50)
    print(f"Sensitive text elements: {result['sensitive_text_count']}")
    print(f"Sensitive attributes: {result['sensitive_attributes_count']}")
    print(f"Content selectors: {result['content_selectors_count']}")
    print(f"Total replacements: {result['total_replacements']}")
    
    # Show sample mappings
    print(f"\n🔍 Sample Content Mappings:")
    print("-" * 50)
    sample_count = 0
    for uuid_key, mapping_data in result['content_mapping'].items():
        if sample_count < 5:
            print(f"   {uuid_key} → '{mapping_data['original']}' ({mapping_data['type']})")
            sample_count += 1
        else:
            break
    
    # Save transformed files
    saved_files = selective_filter.save_selective_files(html_file_path, result)
    
    print(f"\n💾 Files saved:")
    print(f"   Transformed HTML: {saved_files['transformed_html']}")
    print(f"   Mapping JSON: {saved_files['mapping_json']}")
    
    # Cleanup
    selective_filter.cleanup()
    
    return {
        'result': result,
        'saved_files': saved_files
    }

def test_filtering_rules():
    """Test the filtering rules definition."""
    print("🔍 Testing Filtering Rules:")
    print("-" * 40)
    
    filter_instance = SeleniumSelectiveFilterFixed()
    rules = filter_instance.define_filtering_rules()
    
    print("Sensitive Text XPath Rules:")
    for i, rule in enumerate(rules['sensitive_text'], 1):
        print(f"   {i}. {rule}")
    
    print("\nSensitive Attributes XPath Rules:")
    for i, rule in enumerate(rules['sensitive_attributes'], 1):
        print(f"   {i}. {rule}")
    
    print("\nContent Selectors XPath Rules:")
    for i, rule in enumerate(rules['content_selectors'], 1):
        print(f"   {i}. {rule}")

def test_uuid_generation():
    """Test UUID generation functionality."""
    print("\n🔐 Testing UUID Generation:")
    print("-" * 40)
    
    filter_instance = SeleniumSelectiveFilterFixed()
    
    # Generate 10 UUIDs
    uuids = []
    for i in range(10):
        uuid_text = filter_instance.generate_unique_uuid()
        uuids.append(uuid_text)
        print(f"   {i+1}. {uuid_text}")
    
    # Check uniqueness
    unique_count = len(set(uuids))
    if unique_count == 10:
        print("✅ Generated 10 unique UUIDs")
    else:
        print(f"❌ Only {unique_count} unique UUIDs generated")

def main():
    """Main test function."""
    results = test_selenium_selective_filtering_fixed()
    
    if results:
        print(f"\n✅ Selenium selective filtering (fixed) completed successfully!")
        print(f"📄 Transformed HTML: {results['saved_files']['transformed_html']}")
        print(f"📋 Mapping file: {results['saved_files']['mapping_json']}")
    else:
        print(f"\n❌ Selenium selective filtering (fixed) failed!")

if __name__ == "__main__":
    main() 