#!/usr/bin/env python3
"""
Simple test to verify title extraction from HTML file
"""

import sys
from pathlib import Path

# Add parent directory to path to import from scripts
sys.path.append(str(Path(__file__).parent.parent))

def test_title_extraction():
    """Test title extraction from HTML file."""
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load HTML file
        input_file = Path(__file__).parent.parent / "input" / "index_html_.html"
        file_url = f"file://{input_file.absolute()}"
        print(f"📁 Loading HTML file: {file_url}")
        
        driver.get(file_url)
        
        # Find title element
        title_elements = driver.find_elements(By.XPATH, "//title")
        print(f"🔍 Found {len(title_elements)} title elements")
        
        for i, title_element in enumerate(title_elements):
            title_text = title_element.text.strip()
            title_html = driver.execute_script("return arguments[0].outerHTML;", title_element)
            print(f"   Title {i+1}: '{title_text}'")
            print(f"   HTML: {title_html}")
            
            if title_text:
                print(f"   ✅ Title has text content")
            else:
                print(f"   ❌ Title has no text content")
        
        # Also check for meta description
        meta_elements = driver.find_elements(By.XPATH, "//meta[@name='description']")
        print(f"\n🔍 Found {len(meta_elements)} meta description elements")
        
        for i, meta_element in enumerate(meta_elements):
            content_attr = meta_element.get_attribute("content")
            meta_html = driver.execute_script("return arguments[0].outerHTML;", meta_element)
            print(f"   Meta {i+1}: '{content_attr}'")
            print(f"   HTML: {meta_html}")
            
            if content_attr:
                print(f"   ✅ Meta has content attribute")
            else:
                print(f"   ❌ Meta has no content attribute")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_title_extraction() 