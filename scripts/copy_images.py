#!/usr/bin/env python3
"""
SVIT UA Image Copy Script
Copies images from src paths to src1 paths (uploads to uploads1)
"""

import os
import json
import shutil
import sys
import argparse
from pathlib import Path
from typing import List, Dict

class ImageCopier:
    """Copies images from src to src1 paths"""
    
    def __init__(self, base_dir: str = "svituawww.github.io"):
        self.base_dir = Path(base_dir)
        self.report_file = self.base_dir / "database" / "reports" / "image_summary_report.json"
        self.copied_files = []
        self.failed_files = []
        self.skipped_files = []
    
    def load_summary_report(self) -> Dict:
        """Load the image summary report"""
        if not self.report_file.exists():
            raise FileNotFoundError(f"Report file not found: {self.report_file}")
        
        with open(self.report_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_src_paths(self, report: Dict) -> List[Dict[str, str]]:
        """Extract src and src1 paths from the report"""
        paths = []
        for image in report.get('image_sources', []):
            src = image.get('src', '')
            src1 = image.get('src1', '')
            if src and src1:
                paths.append({
                    'src': src,
                    'src1': src1,
                    'filename': os.path.basename(src)
                })
        return paths
    
    def copy_file(self, src_path: str, src1_path: str, overwrite: bool = True) -> bool:
        """Copy a single file from src to src1"""
        # Ensure paths are relative to base_dir
        if src_path.startswith('/'):
            src_path = src_path[1:]  # Remove leading slash
        if src1_path.startswith('/'):
            src1_path = src1_path[1:]  # Remove leading slash
        
        # Build full paths relative to base_dir
        full_src = self.base_dir / src_path
        full_src1 = self.base_dir / src1_path
        
        # Create destination directory if it doesn't exist
        dest_dir = full_src1.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if source file exists
        if not full_src.exists():
            print(f"⚠️  Source file not found: {full_src}")
            return False
        
        # Check if destination file exists
        if full_src1.exists():
            if overwrite:
                print(f"🔄 Replacing existing file: {src1_path}")
            else:
                print(f"⏭️  Skipping existing file: {src1_path}")
                self.skipped_files.append({
                    'src': src_path,
                    'src1': src1_path,
                    'filename': os.path.basename(src_path),
                    'reason': 'file_exists'
                })
                return True
        
        try:
            # Copy the file (will overwrite if overwrite=True)
            shutil.copy2(full_src, full_src1)
            action = "Replaced" if full_src1.exists() else "Copied"
            print(f"✅ {action}: {src_path} → {src1_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to copy {src_path}: {e}")
            return False
    
    def copy_all_images(self, overwrite: bool = True) -> Dict:
        """Copy all images from src to src1 paths"""
        print("🔄 SVIT UA Image Copy Script")
        print("=" * 50)
        print(f"📋 Overwrite existing files: {'Yes' if overwrite else 'No'}")
        print(f"📁 Base directory: {self.base_dir.absolute()}")
        
        # Load the report
        try:
            report = self.load_summary_report()
            print(f"📄 Loaded report: {self.report_file}")
        except Exception as e:
            print(f"❌ Error loading report: {e}")
            return {}
        
        # Get all paths
        paths = self.get_src_paths(report)
        print(f"📋 Found {len(paths)} images to copy")
        
        # Show first few paths for debugging
        print("\n🔍 Sample paths to be processed:")
        for i, path_info in enumerate(paths[:3]):
            print(f"  {i+1}. {path_info['src']} → {path_info['src1']}")
        if len(paths) > 3:
            print(f"  ... and {len(paths) - 3} more")
        
        # Copy each file
        for path_info in paths:
            src = path_info['src']
            src1 = path_info['src1']
            filename = path_info['filename']
            
            if self.copy_file(src, src1, overwrite):
                self.copied_files.append({
                    'src': src,
                    'src1': src1,
                    'filename': filename
                })
            else:
                self.failed_files.append({
                    'src': src,
                    'src1': src1,
                    'filename': filename
                })
        
        # Generate summary
        summary = {
            'total_images': len(paths),
            'copied_files': len(self.copied_files),
            'failed_files': len(self.failed_files),
            'skipped_files': len(self.skipped_files),
            'copied_list': self.copied_files,
            'failed_list': self.failed_files,
            'skipped_list': self.skipped_files,
            'overwrite_mode': overwrite
        }
        
        return summary
    
    def print_summary(self, summary: Dict):
        """Print a summary of the copy operation"""
        print("\n" + "=" * 50)
        print("📊 COPY SUMMARY")
        print("=" * 50)
        print(f"Total images: {summary['total_images']}")
        print(f"✅ Successfully copied: {summary['copied_files']}")
        print(f"❌ Failed to copy: {summary['failed_files']}")
        print(f"⏭️  Skipped: {summary['skipped_files']}")
        
        if summary['failed_files'] > 0:
            print("\n❌ Failed files:")
            for failed in summary['failed_list']:
                print(f"  - {failed['src']}")
        
        # Calculate success rate
        if summary['total_images'] > 0:
            success_rate = (summary['copied_files'] / summary['total_images']) * 100
            print(f"\n📈 Success rate: {success_rate:.1f}%")
    
    def create_backup_report(self, summary: Dict):
        """Create a backup report of the copy operation"""
        backup_report = {
            'backup_info': {
                'name': 'SVIT UA Image Copy Report',
                'version': '1.0.0',
                'created': '2025-07-28',
                'description': 'Report of image copy operation from uploads to uploads1',
                'operation': 'copy_src_to_src1'
            },
            'summary': summary,
            'copied_files': summary['copied_list'],
            'failed_files': summary['failed_list']
        }
        
        # Save backup report
        backup_file = self.base_dir / "database" / "reports" / "image_copy_report.json"
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Backup report saved: {backup_file}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='SVIT UA Image Copy Script')
    parser.add_argument('--no-overwrite', action='store_true', 
                       help='Skip existing files instead of overwriting them')
    parser.add_argument('--overwrite', action='store_true', default=True,
                       help='Overwrite existing files (default)')
    return parser.parse_args()

def main():
    """Main function to run the image copy operation"""
    args = parse_arguments()
    
    # Determine overwrite behavior
    overwrite = not args.no_overwrite
    
    copier = ImageCopier()
    
    try:
        # Copy all images
        summary = copier.copy_all_images(overwrite=overwrite)
        
        # Print summary
        copier.print_summary(summary)
        
        # Create backup report
        copier.create_backup_report(summary)
        
        print("\n🎉 Copy operation completed!")
        
    except Exception as e:
        print(f"❌ Error during copy operation: {e}")

if __name__ == "__main__":
    main() 