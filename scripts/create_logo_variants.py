#!/usr/bin/env python3
"""
Logo Variant Generator for SVIT UA
Creates multiple sizes of the logo with proper centering and normalization
"""

import os
import sys
from PIL import Image, ImageOps
import argparse

def create_logo_variants(input_path, output_dir, sizes):
    """
    Create logo variants with proper centering and normalization
    
    Args:
        input_path (str): Path to original logo image
        output_dir (str): Directory to save variants
        sizes (list): List of (width, height) tuples
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Open the original image
        with Image.open(input_path) as original:
            print(f"📸 Original image: {original.size} ({original.mode})")
            
            # Convert to RGBA if not already (handles transparency)
            if original.mode != 'RGBA':
                original = original.convert('RGBA')
            
            for width, height in sizes:
                print(f"\n🔄 Creating {width}x{height} variant...")
                
                # Create a new image with the target size and transparent background
                new_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                
                # Calculate scaling factor to fit the logo within the target size
                # while maintaining aspect ratio
                original_ratio = original.width / original.height
                target_ratio = width / height
                
                if original_ratio > target_ratio:
                    # Original is wider, scale by width
                    new_width = width
                    new_height = int(width / original_ratio)
                else:
                    # Original is taller, scale by height
                    new_height = height
                    new_width = int(height * original_ratio)
                
                # Resize the original image
                resized = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Calculate position to center the logo
                x_offset = (width - new_width) // 2
                y_offset = (height - new_height) // 2
                
                # Paste the resized logo onto the new image
                new_image.paste(resized, (x_offset, y_offset), resized)
                
                # Save the variant
                output_filename = f"logo_{width}x{height}.png"
                output_path = os.path.join(output_dir, output_filename)
                new_image.save(output_path, 'PNG', optimize=True)
                
                print(f"✅ Saved: {output_filename}")
                print(f"   Size: {new_image.size}")
                print(f"   Logo area: {new_width}x{new_height}")
                print(f"   Centered at: ({x_offset}, {y_offset})")
    
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return False
    
    return True

def main():
    # Define the sizes to create
    sizes = [
        (100, 100),
        (120, 120), 
        (150, 150)
    ]
    
    # Paths
    input_path = "svituawww.github.io/uploads1/2025/logo_original.jpg"
    output_dir = "svituawww.github.io/uploads1/2025/"
    
    print("🎨 SVIT UA Logo Variant Generator")
    print("=" * 40)
    print(f"📁 Input: {input_path}")
    print(f"📁 Output: {output_dir}")
    print(f"📏 Sizes: {', '.join([f'{w}x{h}' for w, h in sizes])}")
    print()
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)
    
    # Create variants
    success = create_logo_variants(input_path, output_dir, sizes)
    
    if success:
        print("\n🎉 All logo variants created successfully!")
        print("\n📋 Generated files:")
        for width, height in sizes:
            filename = f"logo_{width}x{height}.png"
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({file_size} bytes)")
    else:
        print("\n❌ Failed to create logo variants")
        sys.exit(1)

if __name__ == "__main__":
    main()
