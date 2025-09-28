#!/usr/bin/env python3
"""
Missing Images Checker
Checks which images in media_info.json are actually missing from the filesystem
"""

import json
import os
from pathlib import Path

def check_missing_images():
    """Check for missing image files referenced in media_info.json"""
    
    # Paths
    base_dir = Path("/Users/nirsixadmin/Desktop/SvitUA/svituawww.github.io")
    media_info_path = base_dir / "media_info.json"
    
    # Check if media_info.json exists
    if not media_info_path.exists():
        print(f"❌ Error: {media_info_path} not found")
        return False
    
    # Load media_info.json
    print(f"📥 Loading data from {media_info_path}")
    with open(media_info_path, 'r', encoding='utf-8') as f:
        media_data = json.load(f)
    
    media_files = media_data.get('media_files', [])
    print(f"📊 Found {len(media_files)} media file entries")
    
    # Check each file
    missing_files = []
    existing_files = []
    
    for file_info in media_files:
        file_path = file_info.get('file_path', '')
        if not file_path:
            continue
            
        # Create full path
        full_path = base_dir / file_path
        
        if full_path.exists():
            existing_files.append(file_path)
        else:
            missing_files.append({
                'file_path': file_path,
                'filename': file_info.get('filename', 'Unknown'),
                'directory': file_info.get('directory', 'Unknown'),
                'file_size_mb': file_info.get('file_size_mb', 0)
            })
    
    # Report results
    print(f"\n📊 Image File Status Report")
    print(f"=" * 50)
    print(f"✅ Existing files: {len(existing_files)}")
    print(f"❌ Missing files: {len(missing_files)}")
    print(f"📈 Success rate: {len(existing_files)/len(media_files)*100:.1f}%")
    
    if missing_files:
        print(f"\n❌ Missing Files ({len(missing_files)}):")
        print("-" * 30)
        
        # Group by directory
        missing_by_dir = {}
        for file in missing_files:
            directory = file['directory']
            if directory not in missing_by_dir:
                missing_by_dir[directory] = []
            missing_by_dir[directory].append(file)
        
        for directory, files in missing_by_dir.items():
            print(f"\n📁 Directory: {directory} ({len(files)} missing)")
            for file in files[:10]:  # Show first 10 files
                print(f"   • {file['filename']} ({file['file_size_mb']:.2f} MB)")
            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more files")
    
    # Check for common issues
    print(f"\n🔍 Common Issues Check:")
    print("-" * 30)
    
    # Check if directories exist
    directories = set(file['directory'] for file in missing_files)
    for directory in directories:
        dir_path = base_dir / directory
        if dir_path.exists():
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
    
    # Suggest fixes
    if missing_files:
        print(f"\n💡 Suggestions:")
        print("-" * 30)
        print("1. Run the media scanner to update media_info.json:")
        print("   cd ptb_parser && python3 scripts/media_scanner.py")
        print("2. Check if images were moved or deleted")
        print("3. Verify file permissions")
        print("4. Update gallery-data.js after fixing:")
        print("   python3 scripts/update_gallery_data.py")
    
    return len(missing_files) == 0

def main():
    """Main function"""
    print("🔍 Missing Images Checker")
    print("=" * 50)
    
    try:
        success = check_missing_images()
        if success:
            print(f"\n🎉 All images are available!")
        else:
            print(f"\n⚠️  Some images are missing - see details above")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
