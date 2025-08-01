#!/usr/bin/env python3
"""
SVIT UA Image Scanner
Scans HTML files for all image references and media sources
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

@dataclass
class ImageReference:
    """Represents an image reference found in HTML"""
    source_type: str  # 'img_tag', 'srcset', 'js_reference', 'css_background'
    file_path: str
    line_number: int
    context: str
    attributes: Dict[str, str]
    usage_context: List[str]

class HTMLImageScanner:
    """Scans HTML files for image references"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.found_images: List[ImageReference] = []
        
        # Regex patterns for different image sources
        self.patterns = {
            'img_tag': r'<img[^>]*src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\'][^>]*>',
            'srcset': r'srcset=["\']([^"\']*)["\']',
            'js_image': r'["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            'css_background': r'background(?:-image)?:\s*url\(["\']?([^"\')\s]+\.(?:jpg|jpeg|png|gif|webp|svg))["\']?\)',
            'data_src': r'data-src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            'picture_source': r'<source[^>]*srcset=["\']([^"\']*)["\'][^>]*>'
        }
    
    def scan_html_file(self, file_path: str) -> List[ImageReference]:
        """Scan a single HTML file for image references"""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            return []
        
        print(f"Scanning: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        images = []
        
        # Scan for img tags
        img_matches = re.finditer(self.patterns['img_tag'], content, re.IGNORECASE)
        for match in img_matches:
            src = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            context = self._extract_context(content, match.start(), match.end())
            attributes = self._parse_img_attributes(match.group(0))
            
            images.append(ImageReference(
                source_type='img_tag',
                file_path=str(file_path),
                line_number=line_num,
                context=context,
                attributes=attributes,
                usage_context=self._determine_usage_context(context, attributes)
            ))
        
        # Scan for srcset attributes
        srcset_matches = re.finditer(self.patterns['srcset'], content, re.IGNORECASE)
        for match in srcset_matches:
            srcset_value = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            context = self._extract_context(content, match.start(), match.end())
            
            # Parse srcset for individual images
            srcset_images = self._parse_srcset(srcset_value)
            for img_src in srcset_images:
                images.append(ImageReference(
                    source_type='srcset',
                    file_path=str(file_path),
                    line_number=line_num,
                    context=context,
                    attributes={'srcset': srcset_value, 'src': img_src},
                    usage_context=['responsive', 'srcset']
                ))
        
        # Scan for JavaScript image references
        js_images = self._scan_js_references(content, file_path)
        images.extend(js_images)
        
        # Scan for CSS background images
        css_images = self._scan_css_backgrounds(content, file_path)
        images.extend(css_images)
        
        return images
    
    def _parse_srcset(self, srcset_value: str) -> List[str]:
        """Parse srcset attribute to extract individual image URLs"""
        images = []
        # Split by comma and extract URLs
        parts = srcset_value.split(',')
        for part in parts:
            # Extract URL (before space or width descriptor)
            url = part.strip().split(' ')[0]
            if url and any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                images.append(url)
        return images
    
    def _scan_js_references(self, content: str, file_path: Path) -> List[ImageReference]:
        """Scan for image references in JavaScript code"""
        images = []
        
        # Look for JavaScript objects/arrays with image paths
        js_patterns = [
            r'partnersData\s*=\s*\{[^}]*"selected_images":\s*\[([^\]]+)\]',  # partnersData.selected_images
            r'teamData\s*=\s*\{[^}]*"team_members":\s*\[([^\]]+)\]',  # teamData.team_members
            r'selected_images:\s*\[([^\]]+)\]',  # legacy partnersData.selected_images
            r'image:\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            r'img:\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            r'photo:\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            r'logo:\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']',
            r'image_url:\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']'  # teamData.image_url
        ]
        
        for pattern in js_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'partnersData' in pattern:
                    # Handle partnersData.selected_images array
                    array_content = match.group(1)
                    # Extract normalized_path and original_path from partner objects
                    partner_pattern = r'\{[^}]*"normalized_path":\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\'][^}]*"original_path":\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\'][^}]*\}'
                    partner_matches = re.finditer(partner_pattern, array_content)
                    
                    for partner_match in partner_matches:
                        normalized_path = partner_match.group(1)
                        original_path = partner_match.group(2)
                        # Get the specific partner object context
                        partner_context = partner_match.group(0)
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extract partner name if available
                        name_match = re.search(r'"name":\s*["\']([^"\']*)["\']', partner_context)
                        partner_name = name_match.group(1) if name_match else "Unknown"
                        
                        # Add normalized_path image
                        images.append(ImageReference(
                            source_type='js_reference',
                            file_path=str(file_path),
                            line_number=line_num,
                            context=partner_context,
                            attributes={
                                'js_array': 'partnersData.selected_images', 
                                'src': normalized_path,
                                'partner_name': partner_name,
                                'image_type': 'normalized'
                            },
                            usage_context=['javascript', 'dynamic', 'partner', 'carousel']
                        ))
                        
                        # Add original_path image
                        images.append(ImageReference(
                            source_type='js_reference',
                            file_path=str(file_path),
                            line_number=line_num,
                            context=partner_context,
                            attributes={
                                'js_array': 'partnersData.selected_images', 
                                'src': original_path,
                                'partner_name': partner_name,
                                'image_type': 'original'
                            },
                            usage_context=['javascript', 'dynamic', 'partner', 'carousel']
                        ))
                        
                elif 'selected_images' in pattern:
                    # Handle legacy array of images
                    array_content = match.group(1)
                    img_urls = re.findall(r'["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\']', array_content)
                    for img_url in img_urls:
                        line_num = content[:match.start()].count('\n') + 1
                        context = self._extract_context(content, match.start(), match.end())
                        images.append(ImageReference(
                            source_type='js_reference',
                            file_path=str(file_path),
                            line_number=line_num,
                            context=context,
                            attributes={'js_array': 'selected_images', 'src': img_url},
                            usage_context=['javascript', 'dynamic', 'carousel']
                        ))
                elif 'teamData' in pattern:
                    # Handle teamData.team_members array
                    array_content = match.group(1)
                    # Extract individual team member objects with image_url
                    team_member_pattern = r'\{[^}]*"image_url":\s*["\']([^"\']*\.(?:jpg|jpeg|png|gif|webp|svg))["\'][^}]*\}'
                    team_member_matches = re.finditer(team_member_pattern, array_content)
                    
                    for member_match in team_member_matches:
                        img_url = member_match.group(1)
                        # Get the specific team member object context
                        member_context = member_match.group(0)
                        line_num = content[:match.start()].count('\n') + 1
                        context = self._extract_context(content, match.start(), match.end())
                        
                        # Extract team member name if available
                        name_match = re.search(r'"name":\s*["\']([^"\']*)["\']', member_context)
                        team_member_name = name_match.group(1) if name_match else "Unknown"
                        
                        images.append(ImageReference(
                            source_type='js_reference',
                            file_path=str(file_path),
                            line_number=line_num,
                            context=member_context,  # Individual team member context
                            attributes={
                                'js_array': 'teamData.team_members', 
                                'src': img_url,
                                'team_member_name': team_member_name
                            },
                            usage_context=['javascript', 'dynamic', 'team']
                        ))
                elif 'image_url' in pattern:
                    # Handle individual image_url references
                    img_url = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1
                    context = self._extract_context(content, match.start(), match.end())
                    images.append(ImageReference(
                        source_type='js_reference',
                        file_path=str(file_path),
                        line_number=line_num,
                        context=context,
                        attributes={'src': img_url},
                        usage_context=['javascript', 'dynamic', 'team']
                    ))
                else:
                    # Handle single image reference
                    img_url = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1
                    context = self._extract_context(content, match.start(), match.end())
                    images.append(ImageReference(
                        source_type='js_reference',
                        file_path=str(file_path),
                        line_number=line_num,
                        context=context,
                        attributes={'src': img_url},
                        usage_context=['javascript', 'dynamic']
                    ))
        
        return images
    
    def _scan_css_backgrounds(self, content: str, file_path: Path) -> List[ImageReference]:
        """Scan for CSS background image references"""
        images = []
        
        bg_matches = re.finditer(self.patterns['css_background'], content, re.IGNORECASE)
        for match in bg_matches:
            bg_url = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            context = self._extract_context(content, match.start(), match.end())
            images.append(ImageReference(
                source_type='css_background',
                file_path=str(file_path),
                line_number=line_num,
                context=context,
                attributes={'background': bg_url},
                usage_context=['css', 'background', 'decoration']
            ))
        
        return images
    
    def _extract_context(self, content: str, start: int, end: int) -> str:
        """Extract context around the match"""
        context_start = max(0, start - 50)
        context_end = min(len(content), end + 50)
        return content[context_start:context_end].replace('\n', ' ').strip()
    
    def _parse_img_attributes(self, img_tag: str) -> Dict[str, str]:
        """Parse all attributes from an img tag"""
        attributes = {}
        # Extract src
        src_match = re.search(r'src=["\']([^"\']*)["\']', img_tag)
        if src_match:
            attributes['src'] = src_match.group(1)
        
        # Extract alt
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_tag)
        if alt_match:
            attributes['alt'] = alt_match.group(1)
        
        # Extract other attributes
        attr_matches = re.findall(r'(\w+)=["\']([^"\']*)["\']', img_tag)
        for name, value in attr_matches:
            attributes[name] = value
        
        return attributes
    
    def _determine_usage_context(self, context: str, attributes: Dict[str, str]) -> List[str]:
        """Determine usage context based on surrounding code and attributes"""
        usage = []
        
        # Check for common patterns
        if 'header' in context.lower() or 'nav' in context.lower():
            usage.append('header')
        if 'footer' in context.lower():
            usage.append('footer')
        if 'team' in context.lower() or 'member' in context.lower():
            usage.append('team')
        if 'partner' in context.lower() or 'logo' in context.lower():
            usage.append('partner')
        if 'hero' in context.lower() or 'banner' in context.lower():
            usage.append('hero')
        if 'gallery' in context.lower() or 'event' in context.lower():
            usage.append('gallery')
        
        # Check attributes
        if 'alt' in attributes:
            alt_text = attributes['alt'].lower()
            if 'logo' in alt_text:
                usage.append('logo')
            if 'team' in alt_text or 'member' in alt_text:
                usage.append('team')
            if 'partner' in alt_text:
                usage.append('partner')
        
        return usage if usage else ['general']
    
    def scan_directory(self, directory: str = None) -> List[ImageReference]:
        """Scan HTML files in specific directories: main, en/, sv/"""
        if directory is None:
            directory = self.base_dir
        
        all_images = []
        
        # Define specific directories to scan
        scan_dirs = [
            self.base_dir,  # svituawww.github.io/
            self.base_dir / "en",  # svituawww.github.io/en/
            self.base_dir / "sv"   # svituawww.github.io/sv/
        ]
        
        html_files = []
        
        # Collect HTML files from specific directories only
        for scan_dir in scan_dirs:
            if scan_dir.exists():
                # Get HTML files from this directory (not recursive)
                dir_html_files = list(scan_dir.glob("*.html"))
                html_files.extend(dir_html_files)
                print(f"Found {len(dir_html_files)} HTML files in {scan_dir.name}/")
            else:
                print(f"Directory not found: {scan_dir}")
        
        print(f"Total HTML files to scan: {len(html_files)}")
        
        for html_file in html_files:
            images = self.scan_html_file(str(html_file))
            all_images.extend(images)
            print(f"  Found {len(images)} images in {html_file.name}")
        
        return all_images
    
    def generate_report(self, images: List[ImageReference]) -> Dict:
        """Generate a comprehensive report of found images"""
        report = {
            'summary': {
                'total_images': len(images),
                'unique_files': len(set(img.file_path for img in images)),
                'source_types': {},
                'usage_contexts': {}
            },
            'images': []
        }
        
        # Count source types
        for img in images:
            report['summary']['source_types'][img.source_type] = \
                report['summary']['source_types'].get(img.source_type, 0) + 1
            
            for context in img.usage_context:
                report['summary']['usage_contexts'][context] = \
                    report['summary']['usage_contexts'].get(context, 0) + 1
        
        # Convert to list format for JSON
        for img in images:
            # Extract src from image reference
            src = self._extract_src_from_image(img)
            # Create new_src with uploads1
            new_src = self._build_full_url_with_uploads1(src) if src else ""
            
            report['images'].append({
                'source_type': img.source_type,
                'file_path': img.file_path,
                'line_number': img.line_number,
                'context': img.context,
                'attributes': img.attributes,
                'usage_context': img.usage_context,
                'src': src,
                'new_src': new_src
            })
        
        return report
    
    def generate_summary_report(self, images: List[ImageReference]) -> Dict:
        """Generate a summarized report with only src parameters"""
        summary_report = {
            'summary_info': {
                'name': 'SVIT UA Image Summary Report',
                'version': '1.0.0',
                'created': '2025-07-28',
                'description': 'Summary of all image sources found in HTML files',
                'total_images': len(images),
                'unique_sources': len(set(self._extract_src_from_image(img) for img in images))
            },
            'image_sources': []
        }
        
        # Extract unique src values
        unique_srcs = set()
        for img in images:
            src = self._extract_src_from_image(img)
            if src and src not in unique_srcs:
                unique_srcs.add(src)
                # create clone uploads with the name uploads1
                src1 = src.replace('uploads', 'uploads1')
                # create new_src with full URL using uploads1
                new_src = self._build_full_url_with_uploads1(src)
                summary_report['image_sources'].append({
                    'src': src,
                    'src1': src1,
                    'new_src': new_src,
                    'source_type': img.source_type,
                    'usage_context': img.usage_context
                })
        
        return summary_report
    
    def _extract_src_from_image(self, img: ImageReference) -> str:
        """Extract src value from image reference"""
        if img.source_type == 'img_tag':
            return img.attributes.get('src', '')
        elif img.source_type == 'srcset':
            return img.attributes.get('src', '')
        elif img.source_type == 'js_reference':
            return img.attributes.get('src', '')
        elif img.source_type == 'css_background':
            return img.attributes.get('background', '')
        return ''

    def _build_full_url_with_uploads1(self, src: str) -> str:
        """Build full URL using uploads1 instead of uploads"""
        if not src:
            return ""
        
        # Replace uploads with uploads1 in the path
        src_with_uploads1 = src.replace('uploads', 'uploads1')
        
        # Remove leading slash if present
        if src_with_uploads1.startswith('/'):
            src_with_uploads1 = src_with_uploads1[1:]
        
        # Build full URL
        base_url = "https://svituawww.github.io/"
        return base_url + src_with_uploads1

def main():
    """Main function to run the scanner"""
    scanner = HTMLImageScanner('svituawww.github.io')
    
    print("SVIT UA Image Scanner")
    print("=" * 50)
    
    # Scan all HTML files
    images = scanner.scan_directory()
    
    # Generate full report
    report = scanner.generate_report(images)
    
    # Generate summary report
    summary_report = scanner.generate_summary_report(images)
    
    # Create reports directory if it doesn't exist
    reports_dir = Path('svituawww.github.io/database/reports')
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full report
    output_file = reports_dir / 'image_scan_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Save summary report
    summary_file = reports_dir / 'image_summary_report.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    
    print(f"\nScan complete!")
    print(f"Found {len(images)} image references")
    print(f"Full report saved to: {output_file}")
    print(f"Summary report saved to: {summary_file}")
    
    # Print summary
    print("\nSummary:")
    for source_type, count in report['summary']['source_types'].items():
        print(f"  {source_type}: {count}")
    
    print("\nUsage Contexts:")
    for context, count in report['summary']['usage_contexts'].items():
        print(f"  {context}: {count}")
    
    print(f"\nUnique image sources: {summary_report['summary_info']['unique_sources']}")

if __name__ == "__main__":
    main() 