#!/usr/bin/env python3
"""
SVIT UA Image Source Replacement Script
Replaces image src references in HTML files based on scan report data
"""

import os
import json
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class ImageSourceReplacer:
    """Replaces image sources in HTML files based on scan report"""
    
    def __init__(self, base_dir: str = "svituawww.github.io"):
        self.base_dir = Path(base_dir)
        self.report_file = self.base_dir / "database" / "reports" / "image_scan_report.json"
        self.backup_dir = self.base_dir / "backup" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.replacements_made = []
        self.errors = []
        self.skipped = []
        
    def load_scan_report(self) -> Dict:
        """Load the image scan report"""
        if not self.report_file.exists():
            raise FileNotFoundError(f"Scan report not found: {self.report_file}")
        
        with open(self.report_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed for replacement"""
        # Only process HTML files
        allowed_extensions = ['.html', '.htm']
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return False
        
        # Skip backup files
        if 'backup' in file_path.lower():
            return False
        
        return True
    
    def group_replacements_by_file(self, report: Dict) -> Dict[str, List[Dict]]:
        """Group replacements by file_path for efficient processing"""
        file_replacements = {}
        
        for image in report.get('images', []):
            file_path = image.get('file_path', '')
            src = image.get('src', '')
            new_src = image.get('new_src', '')
            context = image.get('context', '')
            source_type = image.get('source_type', '')
            attributes = image.get('attributes', {})
            
            # Skip files that shouldn't be processed
            if not self.should_process_file(file_path):
                print(f"⏭️  Skipping file: {file_path}")
                continue
            
            # Exclude js_reference items with js_array starting with 'partnersData' or 'teamData'
            if source_type == 'js_reference':
                js_array = attributes.get('js_array', '')
                if js_array.startswith('partnersData') or js_array.startswith('teamData'):
                    print(f"⏭️  Skipping JSON data constant: {src} (js_array: {js_array})")
                    continue
            
            if file_path and src and new_src:
                if file_path not in file_replacements:
                    file_replacements[file_path] = []
                
                file_replacements[file_path].append({
                    'src': src,
                    'new_src': new_src,
                    'context': context,
                    'source_type': source_type,
                    'line_number': image.get('line_number', 0)
                })
        
        return file_replacements
    
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of original file"""
        try:
            if file_path.exists():
                # Create backup directory
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy file to backup
                backup_file = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_file)
                print(f"✅ Backup created: {backup_file}")
                return True
            else:
                print(f"⚠️  File not found: {file_path}")
                return False
        except Exception as e:
            print(f"❌ Backup failed for {file_path}: {e}")
            return False
    
    def validate_context(self, html_content: str, scan_context: str, src_to_replace: str) -> bool:
        """Validate that context matches before replacement"""
        try:
            # Clean context for comparison (remove extra whitespace, normalize quotes)
            clean_scan_context = re.sub(r'\s+', ' ', scan_context.strip())
            clean_scan_context = clean_scan_context.replace('"', '"').replace('"', '"')
            
            # Check if context exists in HTML content
            if clean_scan_context in html_content:
                return True
            else:
                # Try with different quote styles
                alt_context = clean_scan_context.replace('"', "'")
                if alt_context in html_content:
                    return True
                
                print(f"⚠️  Context mismatch for {src_to_replace}")
                print(f"   Expected: {clean_scan_context[:100]}...")
                return False
        except Exception as e:
            print(f"❌ Context validation error: {e}")
            return False
    
    def replace_in_file(self, file_path: Path, replacements: List[Dict]) -> Dict:
        """Replace image sources in a single file"""
        result = {
            'file_path': str(file_path),
            'replacements_made': 0,
            'errors': [],
            'skipped': 0
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Process each replacement
            for replacement in replacements:
                src = replacement['src']
                new_src = replacement['new_src']
                context = replacement['context']
                source_type = replacement['source_type']
                
                # Perform replacement based on source type
                if source_type == 'img_tag':
                    # Replace in img tags
                    pattern = f'src=["\']{re.escape(src)}["\']'
                    replacement_str = f'src="{new_src}"'
                    
                elif source_type == 'js_reference':
                    # Replace in JavaScript (handle both quoted and unquoted)
                    escaped_src = re.escape(src)
                    escaped_src_with_slashes = re.escape(src.replace("/", "\\/"))
                    patterns = [
                        f'["\']{escaped_src}["\']',
                        f'["\']{escaped_src_with_slashes}["\']'
                    ]
                    replacement_str = f'"{new_src}"'
                    
                elif source_type == 'srcset':
                    # Replace in srcset attributes
                    pattern = f'{re.escape(src)}'
                    replacement_str = new_src
                    
                else:
                    # Generic replacement
                    pattern = re.escape(src)
                    replacement_str = new_src
                
                # Perform replacement
                if source_type == 'js_reference':
                    # Try multiple patterns for JS references
                    replaced = False
                    for pattern in patterns:
                        if re.search(pattern, content):
                            content = re.sub(pattern, replacement_str, content)
                            replaced = True
                            break
                    if not replaced:
                        result['errors'].append(f"JS pattern not found for {src}")
                        continue
                else:
                    # Standard replacement
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement_str, content)
                    else:
                        result['errors'].append(f"Pattern not found for {src}")
                        continue
                
                result['replacements_made'] += 1
                self.replacements_made.append({
                    'file': str(file_path),
                    'src': src,
                    'new_src': new_src,
                    'source_type': source_type
                })
                print(f"✅ Replaced: {src} → {new_src}")
            
            # Write updated content if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"💾 Updated: {file_path}")
            else:
                print(f"⏭️  No changes needed: {file_path}")
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            print(f"❌ {error_msg}")
            result['errors'].append(error_msg)
            self.errors.append(error_msg)
        
        return result
    
    def process_all_files(self, file_replacements: Dict[str, List[Dict]]) -> Dict:
        """Process all files with their replacements"""
        print("🔄 SVIT UA Image Source Replacement")
        print("=" * 50)
        
        results = {
            'files_processed': 0,
            'total_replacements': 0,
            'total_errors': 0,
            'total_skipped': 0,
            'file_results': []
        }
        
        for file_path_str, replacements in file_replacements.items():
            file_path = Path(file_path_str)
            
            print(f"\n📄 Processing: {file_path}")
            print(f"   Replacements to make: {len(replacements)}")
            
            # Create backup
            if not self.create_backup(file_path):
                results['total_errors'] += 1
                continue
            
            # Process file
            result = self.replace_in_file(file_path, replacements)
            results['file_results'].append(result)
            results['files_processed'] += 1
            results['total_replacements'] += result['replacements_made']
            results['total_errors'] += len(result['errors'])
            results['total_skipped'] += result['skipped']
        
        return results
    
    def generate_report(self, results: Dict) -> Dict:
        """Generate replacement report"""
        report = {
            'replacement_info': {
                'name': 'SVIT UA Image Source Replacement Report',
                'version': '1.0.0',
                'created': datetime.now().isoformat(),
                'description': 'Report of image source replacements in HTML files',
                'backup_location': str(self.backup_dir)
            },
            'summary': results,
            'replacements_made': self.replacements_made,
            'errors': self.errors,
            'skipped': self.skipped
        }
        
        return report
    
    def save_report(self, report: Dict):
        """Save replacement report"""
        report_file = self.base_dir / "database" / "reports" / "image_replacement_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Replacement report saved: {report_file}")
    
    def print_summary(self, results: Dict):
        """Print summary of replacement operation"""
        print("\n" + "=" * 50)
        print("📊 REPLACEMENT SUMMARY")
        print("=" * 50)
        print(f"Files processed: {results['files_processed']}")
        print(f"✅ Replacements made: {results['total_replacements']}")
        print(f"❌ Errors: {results['total_errors']}")
        print(f"⏭️  Skipped: {results['total_skipped']}")
        print(f"📁 Backup location: {self.backup_dir}")
        
        # Show skipped items by reason
        if self.skipped:
            print(f"\n⏭️  Skipped items:")
            skipped_by_reason = {}
            for item in self.skipped:
                reason = item.get('reason', 'unknown')
                if reason not in skipped_by_reason:
                    skipped_by_reason[reason] = 0
                skipped_by_reason[reason] += 1
            
            for reason, count in skipped_by_reason.items():
                if reason == 'context_mismatch':
                    print(f"  - Context mismatches: {count}")
                else:
                    print(f"  - {reason}: {count}")
        
        print(f"\n📋 Exclusion summary:")
        print(f"  - JSON data constants (partnersData/teamData): Excluded at scan level")
        print(f"  - Only functional image references processed")
        
        if results['total_errors'] > 0:
            print("\n❌ Errors encountered:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")

def main():
    """Main function to run the replacement operation"""
    replacer = ImageSourceReplacer()
    
    try:
        # Load scan report
        print("📄 Loading scan report...")
        report = replacer.load_scan_report()
        
        # Group replacements by file
        file_replacements = replacer.group_replacements_by_file(report)
        print(f"📋 Found {len(file_replacements)} HTML files to process")
        
        if not file_replacements:
            print("⚠️  No HTML files found for replacement")
            print("   Only HTML files (.html, .htm) are processed")
            print("   JSON files and other file types are excluded")
            return
        
        # Process all files
        results = replacer.process_all_files(file_replacements)
        
        # Generate and save report
        replacement_report = replacer.generate_report(results)
        replacer.save_report(replacement_report)
        
        # Print summary
        replacer.print_summary(results)
        
        print("\n🎉 Replacement operation completed!")
        
    except Exception as e:
        print(f"❌ Error during replacement operation: {e}")

if __name__ == "__main__":
    main() 