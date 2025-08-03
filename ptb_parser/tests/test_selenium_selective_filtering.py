#!/usr/bin/env python3
"""
Selenium-Based Selective HTML Content Filtering Test - id_part5 Implementation
Demonstrates efficient Selenium identification and selective content filtering
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

class SeleniumSelectiveFilter:
    """Use Selenium to selectively filter and replace specific HTML content."""
    
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
            
            driver = webdriver.Chrome(options=chrome_options)
            return driver
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
        
        driver = self.setup_selenium_driver()
        if not driver:
            return None
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Load HTML file
            file_url = f"file://{Path(html_file_path).absolute()}"
            print(f"📁 Loading HTML file: {file_url}")
            
            driver.get(file_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
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
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.text.strip():
                            extracted_content['sensitive_text'].append({
                                'element': element,
                                'text': element.text.strip(),
                                'tag_name': element.tag_name,
                                'xpath': driver.execute_script("""
                                    function getXPath(element) {
                                        if (element.id !== '') {
                                            return '//' + element.tagName.toLowerCase() + '[@id="' + element.id + '"]';
                                        }
                                        if (element === document.body) {
                                            return '/html/body';
                                        }
                                        var ix = 0;
                                        var siblings = element.parentNode.childNodes;
                                        for (var i = 0; i < siblings.length; i++) {
                                            var sibling = siblings[i];
                                            if (sibling === element) {
                                                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                            }
                                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                                ix++;
                                            }
                                        }
                                    }
                                    return getXPath(arguments[0]);
                                """, element)
                            })
                except Exception as e:
                    print(f"⚠️  Error extracting from {xpath}: {e}")
            
            # Extract sensitive attributes
            for xpath in filtering_rules['sensitive_attributes']:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        attributes = driver.execute_script("""
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
                    elements = driver.find_elements(By.XPATH, xpath)
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
        
        finally:
            # Don't quit the driver here - we need it for transformation
            pass
    
    def transform_specific_content(self, html_file_path: str) -> Dict[str, Any]:
        """Transform only specific content using Selenium filtering."""
        
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
        
        # Transform sensitive text
        transformed_html = original_html
        text_mappings = {}
        
        # Sort items by position (descending) to avoid index shifting issues
        sorted_items = sorted(extracted_content['sensitive_text'], 
                            key=lambda x: x.get('xpath', ''), reverse=True)
        
        for item in sorted_items:
            text = item['text']
            if text.strip():
                uuid_text = self.generate_unique_uuid()
                text_mappings[uuid_text] = {
                    'type': 'sensitive_text',
                    'original': text,
                    'tag_name': item['tag_name'],
                    'xpath': item.get('xpath', '')
                }
                
                # Use Selenium to get the exact element HTML and replace only its text content
                try:
                    # Find the element using the stored xpath
                    xpath = item.get('xpath', '')
                    if xpath:
                        # Get the element's current outerHTML
                        element = self.driver.find_element(By.XPATH, xpath)
                        original_element_html = self.driver.execute_script("return arguments[0].outerHTML;", element)
                        
                        # Replace only the text content within the element
                        new_element_html = original_element_html.replace(text, uuid_text)
                        
                        # Replace the entire element HTML in the document
                        transformed_html = transformed_html.replace(original_element_html, new_element_html)
                    else:
                        # Fallback to simple replacement if no xpath
                        transformed_html = transformed_html.replace(text, uuid_text, 1)
                        
                except Exception as e:
                    print(f"⚠️  Error replacing text in {item['tag_name']}: {e}")
                    # Fallback to simple replacement
                    transformed_html = transformed_html.replace(text, uuid_text, 1)
        
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
        
        transformed_filename = f"selenium_selective_{original_path.stem}_{content_hash}_{timestamp}.html"
        transformed_path = output_dir / transformed_filename
        
        with open(transformed_path, 'w', encoding='utf-8') as f:
            f.write(result['transformed_html'])
        
        # Save mapping JSON to output directory
        mapping_filename = f"selenium_mapping_{original_path.stem}_{content_hash}_{timestamp}.json"
        mapping_path = output_dir / mapping_filename
        
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(result['content_mapping'], f, indent=2, ensure_ascii=False)
        
        return {
            'transformed_html': str(transformed_path),
            'mapping_json': str(mapping_path)
        }

def test_selenium_selective_filtering():
    """Test Selenium-based selective filtering on real HTML file."""
    
    print("🧪 Selenium Selective Content Filtering Test - id_part5")
    print("=" * 60)
    
    # Path to HTML file
    html_file_path = Path(__file__).parent.parent / "input" / "index_html_.html"
    
    if not html_file_path.exists():
        print(f"❌ File not found: {html_file_path}")
        return None
    
    # Initialize selective filter
    selective_filter = SeleniumSelectiveFilter()
    
    # Transform specific content
    result = selective_filter.transform_specific_content(str(html_file_path))
    
    if not result:
        print("❌ Failed to extract content with Selenium")
        return None
    
    # Display results
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
    
    return {
        'result': result,
        'saved_files': saved_files
    }

def test_filtering_rules():
    """Test the filtering rules definition."""
    
    print("\n🔍 Testing Filtering Rules:")
    print("-" * 40)
    
    selective_filter = SeleniumSelectiveFilter()
    rules = selective_filter.define_filtering_rules()
    
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
    """Test UUID generation for selective filtering."""
    
    print("\n🔐 Testing UUID Generation:")
    print("-" * 40)
    
    selective_filter = SeleniumSelectiveFilter()
    generated_uuids = set()
    
    # Generate multiple UUIDs
    for i in range(10):
        uuid_val = selective_filter.generate_unique_uuid()
        if uuid_val in generated_uuids:
            print(f"❌ Duplicate UUID found: {uuid_val}")
            return False
        generated_uuids.add(uuid_val)
        print(f"   {i+1}. {uuid_val}")
    
    print(f"✅ Generated {len(generated_uuids)} unique UUIDs")
    return True

def main():
    """Run all Selenium selective filtering tests."""
    print("🧪 Selenium-Based Selective Filtering Test Suite - id_part5")
    print("=" * 70)
    
    # Test filtering rules
    test_filtering_rules()
    
    # Test UUID generation
    uuid_result = test_uuid_generation()
    
    # Test selective filtering
    results = test_selenium_selective_filtering()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print("-" * 30)
    print(f"UUID Generation Test: {'✅ Passed' if uuid_result else '❌ Failed'}")
    print(f"Selective Filtering Test: {'✅ Passed' if results else '❌ Failed'}")
    
    if results:
        print(f"\n✅ Selenium selective filtering completed successfully!")
        print(f"📄 Transformed HTML: {results['saved_files']['transformed_html']}")
        print(f"📋 Mapping file: {results['saved_files']['mapping_json']}")
    else:
        print(f"\n❌ Selenium selective filtering failed!")

if __name__ == "__main__":
    main() 