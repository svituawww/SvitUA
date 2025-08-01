#!/usr/bin/env python3
"""
TECH_HTML Tag Collector Runner
Simple runner script for the dedicated TECH_HTML collector
"""

import sys
from pathlib import Path

# Add current directory to path to import from scripts
sys.path.append(str(Path(__file__).parent))

from tech_tag_collector import TechHTMLCollector

def main():
    """Run the TECH_HTML collector with default configuration."""
    print("🚀 Starting TECH_HTML Tag Collector...")
    
    # Create collector instance
    collector = TechHTMLCollector()
    
    # Run the complete TECH_HTML processing pipeline
    collector.run()
    
    # Run the TECH_HTML element loop process
    collector.loop_tech_html_elements()
    
    print("\n✅ TECH_HTML processing completed!")
    print("📁 Check output files in json/ and output/ directories")

if __name__ == "__main__":
    main() 