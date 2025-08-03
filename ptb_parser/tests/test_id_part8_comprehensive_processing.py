#!/usr/bin/env python3
"""
Comprehensive HTML Element Processing and UUID Transformation - id_part8 Implementation
Processes ALL HTML elements in any type of HTML file with precise output control
"""

import sys
import json
import uuid
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Set

# Add parent directory to path to import from scripts
sys.path.append(str(Path(__file__).parent.parent))

class ComprehensiveHTMLProcessor:
    """Universal HTML processing system for any type of HTML file with output control."""
    
    def __init__(self):
        self.content_mapping = {}
        self.generated_uuids = set()
        self.driver = None
        self.max_elements = 1000  # Configurable limit
        self.total_elements_processed = 0
    
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
    
    def generate_short_uuid(self) -> str:
        """Generate shortened UUID for element identification."""
        while True:
            # Generate full UUID and take last 12 characters
            full_uuid = str(uuid.uuid4())
            short_uuid = f"uuid_{full_uuid[-12:]}"
            
            # Check for uniqueness
            if short_uuid not in self.generated_uuids:
                self.generated_uuids.add(short_uuid)
                return short_uuid
    
    def analyze_file_type(self, html_content: str) -> Dict[str, Any]:
        """Analyze HTML file type and characteristics."""
        file_type = 'unknown'
        
        # Detect file type based on content patterns
        if 'vue-app' in html_content or 'v-if' in html_content or 'v-for' in html_content:
            file_type = 'vue_application'
        elif 'react' in html_content or 'className' in html_content or 'onClick' in html_content:
            file_type = 'react_application'
        elif 'angular' in html_content or 'ng-' in html_content:
            file_type = 'angular_application'
        elif 'product' in html_content and 'price' in html_content:
            file_type = 'ecommerce_page'
        elif 'blog' in html_content or 'post' in html_content:
            file_type = 'blog_cms'
        elif 'form' in html_content and 'input' in html_content:
            file_type = 'form_application'
        else:
            file_type = 'static_corporate'
        
        return {
            'type': file_type,
            'encoding': self.detect_encoding(html_content),
            'language': self.detect_primary_language(html_content)
        }
    
    def detect_encoding(self, html_content: str) -> str:
        """Detect HTML encoding."""
        # Look for charset in meta tags
        charset_match = re.search(r'charset=["\']?([^"\'>]+)', html_content, re.IGNORECASE)
        if charset_match:
            return charset_match.group(1)
        return 'UTF-8'
    
    def detect_primary_language(self, html_content: str) -> str:
        """Detect primary language of content."""
        # Simple language detection based on character patterns
        ukrainian_chars = len(re.findall(r'[а-яА-ЯіїєІЇЄ]', html_content))
        english_chars = len(re.findall(r'[a-zA-Z]', html_content))
        
        if ukrainian_chars > english_chars:
            return 'uk'
        elif english_chars > 0:
            return 'en'
        else:
            return 'unknown'
    
    def detect_language(self, text: str) -> str:
        """Detect language of specific text."""
        ukrainian_chars = len(re.findall(r'[а-яА-ЯіїєІЇЄ]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if ukrainian_chars > english_chars:
            return 'uk'
        elif english_chars > 0:
            return 'en'
        else:
            return 'unknown'
    
    def is_processable_attribute(self, attr_name: str, tag_name: str) -> bool:
        """Determine if attribute should be processed."""
        # Skip structural attributes that should be preserved
        structural_attrs = ['class', 'id', 'style']
        
        # Skip framework-specific attributes that should be preserved
        framework_attrs = ['v-if', 'v-for', 'v-bind', 'v-model', 'className', 'onClick']
        
        return attr_name not in structural_attrs and attr_name not in framework_attrs
    
    def is_dynamic_element(self, element_data: Dict) -> bool:
        """Check if element contains dynamic content."""
        dynamic_patterns = [
            '{{', '}}',  # Vue.js template syntax
            'v-if', 'v-for', 'v-bind',  # Vue.js directives
            'className', 'onClick',  # React patterns
            'ng-',  # Angular patterns
            'data-',  # Custom data attributes
        ]
        
        return any(pattern in str(element_data) for pattern in dynamic_patterns)
    
    def determine_output_status(self, element_data: Dict) -> bool:
        """Determine if element should be included in output based on rules."""
        
        # Define output rules - what should be transformed vs. preserved
        output_rules = {
            'title': True,                    # Transform titles
            'h1': True,                      # Transform h1
            'h2': False,                     # Preserve h2 (structural)
            'h3': True,                      # Transform h3
            'p': True,                       # Transform paragraphs
            'meta': True,                    # Transform meta content
            'img': True,                     # Transform image attributes
            'a': True,                       # Transform link text
            'button': True,                  # Transform button text
            'input': False,                  # Preserve input values (functional)
            'form': False,                   # Preserve form structure
            'div': False,                    # Preserve div structure
            'span': True,                    # Transform span content
            'li': True,                      # Transform list items
            'td': True,                      # Transform table cells
            'th': True,                      # Transform table headers
        }
        
        tag_name = element_data.get('tag_name', '')
        return output_rules.get(tag_name, True)  # Default to True if not specified
    
    def extract_all_attributes(self, element) -> Dict[str, str]:
        """Extract all attributes from an element."""
        try:
            attributes = self.driver.execute_script("""
                var items = {};
                for (index = 0; index < arguments[0].attributes.length; ++index) {
                    items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value;
                }
                return items;
            """, element)
            return attributes
        except Exception as e:
            print(f"⚠️  Error extracting attributes: {e}")
            return {}
    
    def get_element_xpath(self, element) -> str:
        """Get XPath for an element."""
        try:
            return self.driver.execute_script("""
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
        except Exception as e:
            print(f"⚠️  Error getting XPath: {e}")
            return ""
    
    def get_element_position(self, element) -> Dict[str, int]:
        """Get element position in document."""
        try:
            position = self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    start: arguments[0].offsetTop,
                    end: arguments[0].offsetTop + arguments[0].offsetHeight
                };
            """, element)
            return position
        except Exception as e:
            print(f"⚠️  Error getting position: {e}")
            return {"start": 0, "end": 0}
    
    def process_all_html_elements(self, html_file_path: str) -> Dict[str, Any]:
        """Process ALL HTML elements comprehensively for any type of HTML file."""
        
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
            
            # Read original HTML content
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Analyze file type
            file_metadata = self.analyze_file_type(html_content)
            print(f"📊 File type detected: {file_metadata['type']}")
            print(f"🌐 Language: {file_metadata['language']}")
            print(f"🔤 Encoding: {file_metadata['encoding']}")
            
            # Initialize tracking
            element_mappings = {}
            processed_elements = []
            
            # Extract all elements using Selenium
            all_elements = self.driver.find_elements(By.XPATH, "//*")
            print(f"🔍 Found {len(all_elements)} elements to process")
            
            # Validate element count
            if len(all_elements) > self.max_elements:
                raise Exception(f"Too many elements ({len(all_elements)}) found. Maximum allowed: {self.max_elements}")
            
            for i, element in enumerate(all_elements):
                try:
                    element_data = {
                        'tag_name': element.tag_name,
                        'xpath': self.get_element_xpath(element),
                        'outer_html': element.get_attribute('outerHTML'),
                        'inner_html': element.get_attribute('innerHTML'),
                        'text_content': element.text,
                        'attributes': self.extract_all_attributes(element),
                        'file_type': file_metadata['type'],
                        'language': self.detect_language(element.text),
                        'encoding': file_metadata['encoding']
                    }
                    
                    # Process text content (multi-language support)
                    if element_data['text_content'].strip():
                        text_uuid = self.generate_short_uuid()
                        output_status = self.determine_output_status(element_data)
                        
                        element_mappings[text_uuid] = {
                            'type': 'text_content',
                            'element_type': element_data['tag_name'],
                            'original_value': element_data['text_content'],
                            'xpath': element_data['xpath'],
                            'output': output_status,
                            'position': self.get_element_position(element),
                            'processing_timestamp': datetime.now().isoformat() + "Z",
                            'file_type': element_data['file_type'],
                            'language': element_data['language'],
                            'encoding': element_data['encoding']
                        }
                        
                        processed_elements.append({
                            'uuid': text_uuid,
                            'type': 'text_content',
                            'element': element_data,
                            'output': output_status
                        })
                        
                        status_icon = "✅" if output_status else "❌"
                        print(f"{status_icon} Text: '{element_data['text_content'][:50]}...' → {text_uuid}")
                    
                    # Process attributes (comprehensive attribute handling)
                    for attr_name, attr_value in element_data['attributes'].items():
                        if attr_value and self.is_processable_attribute(attr_name, element_data['tag_name']):
                            attr_uuid = self.generate_short_uuid()
                            output_status = self.determine_output_status(element_data)
                            
                            element_mappings[attr_uuid] = {
                                'type': 'attribute_value',
                                'element_type': element_data['tag_name'],
                                'attribute_name': attr_name,
                                'original_value': attr_value,
                                'xpath': f"{element_data['xpath']}/@{attr_name}",
                                'output': output_status,
                                'position': self.get_element_position(element),
                                'processing_timestamp': datetime.now().isoformat() + "Z",
                                'file_type': element_data['file_type'],
                                'language': self.detect_language(attr_value),
                                'encoding': element_data['encoding']
                            }
                            
                            processed_elements.append({
                                'uuid': attr_uuid,
                                'type': 'attribute_value',
                                'element': element_data,
                                'attribute_name': attr_name,
                                'output': output_status
                            })
                            
                            status_icon = "✅" if output_status else "❌"
                            print(f"{status_icon} Attr: {attr_name}='{attr_value[:30]}...' → {attr_uuid}")
                    
                    # Process dynamic content (Vue.js, React, etc.)
                    if self.is_dynamic_element(element_data):
                        dynamic_content = self.extract_dynamic_content(element_data)
                        for dynamic_item in dynamic_content:
                            dynamic_uuid = self.generate_short_uuid()
                            output_status = self.determine_output_status(element_data)
                            
                            element_mappings[dynamic_uuid] = {
                                'type': 'dynamic_content',
                                'element_type': element_data['tag_name'],
                                'original_value': dynamic_item['content'],
                                'xpath': f"{element_data['xpath']}/dynamic",
                                'output': output_status,
                                'position': self.get_element_position(element),
                                'processing_timestamp': datetime.now().isoformat() + "Z",
                                'file_type': element_data['file_type'],
                                'language': self.detect_language(dynamic_item['content']),
                                'encoding': element_data['encoding'],
                                'dynamic_type': dynamic_item['type']
                            }
                            
                            status_icon = "✅" if output_status else "❌"
                            print(f"{status_icon} Dynamic: '{dynamic_item['content'][:30]}...' → {dynamic_uuid}")
                    
                except Exception as e:
                    print(f"⚠️  Error processing element {i}: {e}")
                    continue
            
            self.total_elements_processed = len(all_elements)
            
            return {
                'mappings': element_mappings,
                'processed_elements': processed_elements,
                'total_elements': len(all_elements),
                'total_text_content': len([e for e in processed_elements if e['type'] == 'text_content']),
                'total_attributes': len([e for e in processed_elements if e['type'] == 'attribute_value']),
                'total_dynamic': len([e for e in processed_elements if e['type'] == 'dynamic_content']),
                'file_metadata': file_metadata
            }
            
        except Exception as e:
            print(f"❌ Error in comprehensive processing: {e}")
            return None
    
    def extract_dynamic_content(self, element_data: Dict) -> List[Dict]:
        """Extract dynamic content from element."""
        dynamic_content = []
        
        # Check for Vue.js template syntax
        if '{{' in str(element_data) and '}}' in str(element_data):
            matches = re.findall(r'\{\{([^}]+)\}\}', str(element_data))
            for match in matches:
                dynamic_content.append({
                    'content': match.strip(),
                    'type': 'vue_template'
                })
        
        # Check for Vue.js directives
        vue_directives = ['v-if', 'v-for', 'v-bind', 'v-model']
        for directive in vue_directives:
            if directive in str(element_data):
                dynamic_content.append({
                    'content': directive,
                    'type': 'vue_directive'
                })
        
        # Check for React patterns
        react_patterns = ['className', 'onClick']
        for pattern in react_patterns:
            if pattern in str(element_data):
                dynamic_content.append({
                    'content': pattern,
                    'type': 'react_pattern'
                })
        
        return dynamic_content
    
    def transform_html_with_output_control(self, html_file_path: str, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Transform HTML with precise output control."""
        
        # Read original HTML
        with open(html_file_path, 'r', encoding='utf-8') as f:
            original_html = f.read()
        
        print(f"📄 Processing HTML file: {html_file_path}")
        print(f"📊 Original content length: {len(original_html)} characters")
        
        # Transform HTML with selective output
        transformed_html = original_html
        
        # Process elements with output control
        output_elements = []
        preserved_elements = []
        
        for uuid_key, mapping_data in processing_result['mappings'].items():
            if mapping_data['output']:
                # Add to output list for transformation
                output_elements.append({
                    'uuid': uuid_key,
                    'mapping': mapping_data
                })
            else:
                # Add to preserved list (unchanged)
                preserved_elements.append({
                    'uuid': uuid_key,
                    'mapping': mapping_data
                })
        
        # Transform elements with output=true
        for output_item in output_elements:
            uuid_key = output_item['uuid']
            mapping_data = output_item['mapping']
            original_value = mapping_data['original_value']
            
            if mapping_data['type'] == 'text_content':
                # Replace text content
                transformed_html = transformed_html.replace(original_value, uuid_key, 1)
                print(f"✅ OUTPUT: Replaced text '{original_value[:50]}...' → {uuid_key}")
            
            elif mapping_data['type'] == 'attribute_value':
                # Replace attribute value
                attr_name = mapping_data['attribute_name']
                attr_pattern = f'{attr_name}="{original_value}"'
                attr_replacement = f'{attr_name}="{uuid_key}"'
                transformed_html = transformed_html.replace(attr_pattern, attr_replacement, 1)
                print(f"✅ OUTPUT: Replaced attr {attr_name}='{original_value[:30]}...' → {uuid_key}")
            
            elif mapping_data['type'] == 'dynamic_content':
                # Replace dynamic content
                transformed_html = transformed_html.replace(original_value, uuid_key, 1)
                print(f"✅ OUTPUT: Replaced dynamic '{original_value[:30]}...' → {uuid_key}")
        
        # Log preserved elements (output=false)
        for preserved_item in preserved_elements:
            mapping_data = preserved_item['mapping']
            original_value = mapping_data['original_value']
            print(f"❌ PRESERVED: Kept '{original_value[:50]}...' unchanged")
        
        return {
            'transformed_html': transformed_html,
            'content_mapping': processing_result['mappings'],
            'output_elements': output_elements,
            'preserved_elements': preserved_elements,
            'total_processed': processing_result['total_elements'],
            'total_output': len(output_elements),
            'total_preserved': len(preserved_elements),
            'file_metadata': processing_result['file_metadata']
        }
    
    def save_comprehensive_files(self, original_path: Path, result: Dict[str, Any]) -> Dict[str, str]:
        """Save comprehensive HTML and mapping files."""
        
        # Generate unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(original_path.read_bytes()).hexdigest()[:8]
        
        # Save transformed HTML to test output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create filenames
        base_name = original_path.stem
        transformed_html_file = output_dir / f"id_part8_comprehensive_{base_name}_{content_hash}_{timestamp}.html"
        mapping_json_file = output_dir / f"id_part8_comprehensive_mapping_{base_name}_{content_hash}_{timestamp}.json"
        
        # Save transformed HTML
        with open(transformed_html_file, 'w', encoding='utf-8') as f:
            f.write(result['transformed_html'])
        
        # Save comprehensive mapping JSON
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

def test_id_part8_comprehensive_processing():
    """Test the comprehensive id_part8 HTML processing implementation."""
    
    print("🧪 Comprehensive HTML Element Processing Test - id_part8")
    print("=" * 70)
    
    # Initialize processor
    processor = ComprehensiveHTMLProcessor()
    
    # Find HTML file to process
    input_dir = Path(__file__).parent.parent / "input"
    html_files = list(input_dir.glob("*.html"))
    
    if not html_files:
        print("❌ No HTML files found in input directory")
        return None
    
    html_file_path = html_files[0]  # Use first HTML file
    print(f"🧪 Processing file: {html_file_path.name}")
    
    # Process all HTML elements
    processing_result = processor.process_all_html_elements(str(html_file_path))
    
    if not processing_result:
        print("❌ Failed to process HTML elements")
        return None
    
    # Print processing results
    print(f"\n📊 Comprehensive Processing Results:")
    print("-" * 50)
    print(f"Total elements found: {processing_result['total_elements']}")
    print(f"Text content elements: {processing_result['total_text_content']}")
    print(f"Attribute elements: {processing_result['total_attributes']}")
    print(f"Dynamic content elements: {processing_result['total_dynamic']}")
    print(f"File type: {processing_result['file_metadata']['type']}")
    print(f"Language: {processing_result['file_metadata']['language']}")
    print(f"Encoding: {processing_result['file_metadata']['encoding']}")
    
    # Transform HTML with output control
    transformation_result = processor.transform_html_with_output_control(
        str(html_file_path), processing_result
    )
    
    if not transformation_result:
        print("❌ Failed to transform HTML")
        return None
    
    # Print transformation results
    print(f"\n📊 Transformation Results:")
    print("-" * 50)
    print(f"Elements with output=true: {transformation_result['total_output']}")
    print(f"Elements with output=false: {transformation_result['total_preserved']}")
    print(f"Original HTML size: {len(transformation_result['transformed_html'])} characters")
    
    # Show sample mappings
    print(f"\n🔍 Sample Content Mappings:")
    print("-" * 50)
    sample_count = 0
    for uuid_key, mapping_data in processing_result['mappings'].items():
        if sample_count < 5:
            output_status = "✅ OUTPUT" if mapping_data.get('output', True) else "❌ PRESERVED"
            print(f"   {uuid_key} → '{mapping_data['original_value'][:50]}...' ({mapping_data['type']}) {output_status}")
            sample_count += 1
        else:
            break
    
    # Save comprehensive files
    saved_files = processor.save_comprehensive_files(html_file_path, transformation_result)
    
    print(f"\n💾 Files saved:")
    print(f"   Transformed HTML: {saved_files['transformed_html']}")
    print(f"   Mapping JSON: {saved_files['mapping_json']}")
    
    # Cleanup
    processor.cleanup()
    
    return {
        'processing_result': processing_result,
        'transformation_result': transformation_result,
        'saved_files': saved_files
    }

def main():
    """Main test function."""
    results = test_id_part8_comprehensive_processing()
    
    if results:
        print(f"\n✅ Comprehensive HTML processing (id_part8) completed successfully!")
        print(f"📄 Transformed HTML: {results['saved_files']['transformed_html']}")
        print(f"📋 Mapping file: {results['saved_files']['mapping_json']}")
    else:
        print(f"\n❌ Comprehensive HTML processing (id_part8) failed!")

if __name__ == "__main__":
    main() 