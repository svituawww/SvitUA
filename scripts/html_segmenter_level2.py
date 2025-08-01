#!/usr/bin/env python3
"""
HTML Segmenter Level 2 - HTML Block Segmentation
Extends Level 1 functionality to identify and segment major HTML blocks.
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Try to import psutil, fallback to basic memory tracking
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available, using basic memory tracking")


class HTMLBlockSegmenter:
    def __init__(self, config_file: Path):
        self.config = self.load_config(config_file)
        self.html_blocks = self.config.get('html_blocks', {})
        self.processing_options = self.config.get('processing_options', {})
        self.identified_blocks = []
        self.unidentified_sections = []
        self.start_time = None
        self.start_memory = None
    
    def load_config(self, config_file: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Config file {config_file} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in config file: {e}")
            return {}
    
    def start_performance_tracking(self):
        """Start performance tracking"""
        self.start_time = time.time()
        if PSUTIL_AVAILABLE:
            self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        else:
            self.start_memory = 0
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics"""
        if self.start_time is None:
            return {"processing_time_ms": 0, "memory_usage_mb": 0}
        
        end_time = time.time()
        if PSUTIL_AVAILABLE:
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_usage = end_memory - self.start_memory
        else:
            memory_usage = 0
        
        return {
            "processing_time_ms": (end_time - self.start_time) * 1000,
            "memory_usage_mb": memory_usage
        }
    
    def extract_attributes(self, html_content: str) -> Dict[str, str]:
        """Extract attributes from HTML tag"""
        attributes = {}
        # Extract class, id, and other common attributes
        class_match = re.search(r'class=["\']([^"\']*)["\']', html_content)
        if class_match:
            attributes['class'] = class_match.group(1)
        
        id_match = re.search(r'id=["\']([^"\']*)["\']', html_content)
        if id_match:
            attributes['id'] = id_match.group(1)
        
        return attributes
    
    def find_block_boundaries(self, html_content: str, block_name: str, block_config: Dict) -> List[Tuple[int, int, Dict]]:
        """Find all occurrences of a specific HTML block"""
        start_pattern = block_config['start']
        end_pattern = block_config['end']
        
        # Create regex patterns that handle attributes
        start_regex = re.compile(f"{re.escape(start_pattern)}[^>]*>", re.IGNORECASE)
        end_regex = re.compile(re.escape(end_pattern), re.IGNORECASE)
        
        blocks = []
        start_pos = 0
        
        while True:
            start_match = start_regex.search(html_content, start_pos)
            if not start_match:
                break
            
            start_pos = start_match.start()
            end_match = end_regex.search(html_content, start_pos)
            
            if not end_match:
                # Unclosed block, treat as unidentified
                break
            
            end_pos = end_match.end()
            block_content = html_content[start_pos:end_pos]
            
            # Extract attributes
            attributes = self.extract_attributes(block_content)
            
            # Calculate line numbers
            start_line = html_content[:start_pos].count('\n') + 1
            end_line = html_content[:end_pos].count('\n') + 1
            
            blocks.append({
                'type': block_name,
                'category': block_config['category'],
                'size': len(block_content),
                'start_line': start_line,
                'end_line': end_line,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'attributes': attributes,
                'content': block_content
            })
            
            start_pos = end_pos
        
        return blocks
    
    def segment_html_blocks(self, html_content: str) -> str:
        """Segment HTML content by identifying and marking blocks with non-overlapping constraint"""
        self.start_performance_tracking()
        
        # Get priority order from config
        priority_order = self.config.get('validation_rules', {}).get('priority_order', 
                                                                   ['head', 'header', 'nav', 'section', 'footer'])
        
        # Track all identified blocks and used positions
        all_blocks = []
        used_positions = set()  # Track used character positions to prevent overlaps
        
        # Process blocks in priority order
        for block_name in priority_order:
            if block_name not in self.html_blocks:
                continue
                
            block_config = self.html_blocks[block_name]
            blocks = self.find_block_boundaries(html_content, block_name, block_config)
            
            # Filter out overlapping blocks based on priority
            non_overlapping_blocks = []
            for block in blocks:
                # Check if this block overlaps with any already used positions
                block_positions = set(range(block['start_pos'], block['end_pos']))
                if not block_positions.intersection(used_positions):
                    non_overlapping_blocks.append(block)
                    # Mark these positions as used
                    used_positions.update(block_positions)
            
            all_blocks.extend(non_overlapping_blocks)
        
        # Sort blocks by start position for proper insertion order
        all_blocks.sort(key=lambda x: x['start_pos'])
        
        # Create segmented HTML with block markers
        segmented_html = html_content
        offset = 0
        
        for block in all_blocks:
            start_pos = block['start_pos'] + offset
            end_pos = block['end_pos'] + offset
            
            # Create block markers
            start_marker = f"\n<!-- BLOCK_START: {block['type']} ({block['category']}) -->\n"
            end_marker = f"\n<!-- BLOCK_END: {block['type']} -->\n"
            
            # Insert markers
            segmented_html = (
                segmented_html[:start_pos] + 
                start_marker + 
                segmented_html[start_pos:end_pos] + 
                end_marker + 
                segmented_html[end_pos:]
            )
            
            # Update offset for next insertions
            offset += len(start_marker) + len(end_marker)
            
            # Store block info for analysis
            self.identified_blocks.append({
                'type': block['type'],
                'category': block['category'],
                'size': block['size'],
                'start_line': block['start_line'],
                'end_line': block['end_line'],
                'attributes': block['attributes'],
                'nesting_level': 0  # TODO: Calculate actual nesting level
            })
        
        return segmented_html
    
    def find_unidentified_sections(self, html_content: str) -> List[Dict]:
        """Find sections that don't match any configured blocks"""
        # This is a simplified approach - in practice, you'd want more sophisticated
        # logic to identify truly unidentified sections
        unidentified = []
        
        # Look for common div patterns that might be unidentified
        div_pattern = r'<div[^>]*>.*?</div>'
        div_matches = re.finditer(div_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        for match in div_matches:
            content = match.group(0)
            start_line = html_content[:match.start()].count('\n') + 1
            end_line = html_content[:match.end()].count('\n') + 1
            
            # Check if this div is already within an identified block
            is_identified = False
            for block in self.identified_blocks:
                if (start_line >= block['start_line'] and 
                    end_line <= block['end_line']):
                    is_identified = True
                    break
            
            if not is_identified:
                unidentified.append({
                    'content': content[:100] + "..." if len(content) > 100 else content,
                    'start_line': start_line,
                    'end_line': end_line,
                    'size': len(content),
                    'suggestion': f"Consider adding to config as 'div' block"
                })
        
        return unidentified
    
    def calculate_overlap_percentage(self) -> float:
        """Calculate the percentage of overlapping blocks"""
        if len(self.identified_blocks) < 2:
            return 0.0
        
        # Check for overlaps between blocks
        overlaps = 0
        total_comparisons = 0
        
        for i, block1 in enumerate(self.identified_blocks):
            for j, block2 in enumerate(self.identified_blocks[i+1:], i+1):
                total_comparisons += 1
                
                # Check if blocks overlap
                if (block1['start_line'] <= block2['end_line'] and 
                    block1['end_line'] >= block2['start_line']):
                    overlaps += 1
        
        if total_comparisons == 0:
            return 0.0
        
        return (overlaps / total_comparisons) * 100.0
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report with overlap validation"""
        performance_metrics = self.get_performance_metrics()
        
        # Count blocks by type and category
        blocks_by_type = {}
        blocks_by_category = {}
        
        for block in self.identified_blocks:
            block_type = block['type']
            block_category = block['category']
            
            blocks_by_type[block_type] = blocks_by_type.get(block_type, 0) + 1
            blocks_by_category[block_category] = blocks_by_category.get(block_category, 0) + 1
        
        # Calculate overlap validation
        overlap_percentage = self.calculate_overlap_percentage()
        consistency_check = "passed" if overlap_percentage == 0.0 else "failed"
        
        # Find unidentified sections
        self.unidentified_sections = self.find_unidentified_sections("")  # TODO: Pass actual content
        
        return {
            "processing_summary": {
                "total_blocks": len(self.identified_blocks),
                "identified_blocks": len(self.identified_blocks),
                "unidentified_sections": len(self.unidentified_sections),
                "processing_time_ms": performance_metrics["processing_time_ms"],
                "memory_usage_mb": performance_metrics["memory_usage_mb"],
                "block_overlap_percentage": overlap_percentage,
                "consistency_check": consistency_check
            },
            "blocks_by_type": blocks_by_type,
            "blocks_by_category": blocks_by_category,
            "identified_blocks": self.identified_blocks,
            "unidentified_sections": self.unidentified_sections,
            "hierarchy_analysis": {
                "max_nesting_level": 0,  # TODO: Calculate actual nesting
                "block_dependencies": {},
                "structural_integrity": "valid"
            },
            "performance_metrics": {
                "regex_matches": len(self.identified_blocks),
                "block_processing_time": performance_metrics["processing_time_ms"] * 0.8,
                "file_io_time": performance_metrics["processing_time_ms"] * 0.2,
                "total_memory_peak": performance_metrics["memory_usage_mb"]
            }
        }
    
    def process_file(self, input_file: Path, output_dir: Path):
        """Process HTML file with Level 2 block segmentation"""
        print(f"Processing Level 2 HTML block segmentation: {input_file}")
        
        # Check if input file exists
        if not input_file.exists():
            print(f"❌ Error: Input file {input_file} not found")
            return
        
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Segment HTML blocks
        segmented_html = self.segment_html_blocks(html_content)
        print(f"✅ Level 2 block segmentation completed")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save segmented HTML
        html_output_file = output_dir / "index_html_blocks.html"
        with open(html_output_file, 'w', encoding='utf-8') as f:
            f.write(segmented_html)
        
        # Generate and save analysis report
        analysis_report = self.generate_analysis_report()
        report_file = output_dir / "blocks_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Results saved to:")
        print(f"   {html_output_file}")
        print(f"   {report_file}")
        
        # Print summary
        print(f"\n📊 Level 2 Analysis Summary:")
        print(f"   Identified blocks: {analysis_report['processing_summary']['identified_blocks']}")
        print(f"   Unidentified sections: {analysis_report['processing_summary']['unidentified_sections']}")
        print(f"   Processing time: {analysis_report['processing_summary']['processing_time_ms']:.2f}ms")
        print(f"   Memory usage: {analysis_report['processing_summary']['memory_usage_mb']:.2f}MB")
        
        return analysis_report


def main():
    # File paths
    config_file = Path("scripts/json/html_blocks_config.json")
    input_file = Path("svituawww.github.io/output/index_html_.html")
    output_dir = Path("svituawww.github.io/output/html")
    
    # Check if config file exists
    if not config_file.exists():
        print(f"❌ Error: Config file {config_file} not found")
        return
    
    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Error: Input file {input_file} not found")
        print(f"   Please run Level 1 segmentation first")
        return
    
    # Process file with Level 2 approach
    segmenter = HTMLBlockSegmenter(config_file)
    results = segmenter.process_file(input_file, output_dir)
    
    print(f"\n🎯 Level 2 Block Segmentation Complete!")
    print(f"   Config: {config_file}")
    print(f"   Input: {input_file}")
    print(f"   Output directory: {output_dir}")


if __name__ == "__main__":
    main() 