#!/usr/bin/env python3
"""
Logo Color Analyzer for SVIT UA
Analyzes the colors in the logo and identifies the most prominent ones
"""

import os
from PIL import Image
from collections import Counter

def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color code"""
    return f"#{r:02x}{g:02x}{b:02x}"

def analyze_logo_colors(image_path, top_colors=5):
    """
    Analyze the colors in the logo and return the most prominent ones
    
    Args:
        image_path (str): Path to the logo image
        top_colors (int): Number of top colors to return
    
    Returns:
        list: List of (color_hex, count, percentage) tuples
    """
    
    try:
        # Open the image
        with Image.open(image_path) as img:
            print(f"📸 Analyzing image: {img.size} ({img.mode})")
            
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get all pixels as a list of RGB tuples
            pixels = list(img.getdata())
            
            # Count occurrences of each color
            color_counts = Counter(pixels)
            
            # Calculate total pixels
            total_pixels = len(pixels)
            
            # Get the most common colors
            most_common = color_counts.most_common(top_colors)
            
            # Convert to hex and calculate percentages
            results = []
            for (r, g, b), count in most_common:
                hex_color = rgb_to_hex(r, g, b)
                percentage = (count / total_pixels) * 100
                results.append((hex_color, count, percentage))
            
            return results
    
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return []

def display_color_info(color_data):
    """Display color information in a formatted way"""
    
    print("\n🎨 Logo Color Analysis")
    print("=" * 50)
    
    for i, (hex_color, count, percentage) in enumerate(color_data, 1):
        # Create a visual representation of the color
        color_block = "█" * 20
        
        print(f"\n{i}. {hex_color}")
        print(f"   Pixels: {count:,}")
        print(f"   Percentage: {percentage:.2f}%")
        print(f"   Visual: {color_block}")
        
        # Try to identify the color name
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        
        # Simple color identification
        if r > 200 and g > 200 and b > 200:
            color_name = "White/Light"
        elif r < 50 and g < 50 and b < 50:
            color_name = "Black/Dark"
        elif r > 200 and g < 100 and b < 100:
            color_name = "Red"
        elif r < 100 and g > 200 and b < 100:
            color_name = "Green"
        elif r < 100 and g < 100 and b > 200:
            color_name = "Blue"
        elif r > 200 and g > 200 and b < 100:
            color_name = "Yellow"
        elif r > 200 and g < 100 and b > 200:
            color_name = "Magenta"
        elif r < 100 and g > 200 and b > 200:
            color_name = "Cyan"
        else:
            color_name = "Mixed"
        
        print(f"   Type: {color_name}")
        print(f"   RGB: ({r}, {g}, {b})")

def main():
    # Path to the logo
    logo_path = "svituawww.github.io/uploads1/2025/logo_original.jpg"
    
    print("🔍 SVIT UA Logo Color Analyzer")
    print("=" * 40)
    print(f"📁 Logo: {logo_path}")
    
    # Check if file exists
    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        return
    
    # Analyze colors
    color_data = analyze_logo_colors(logo_path, top_colors=5)
    
    if color_data:
        display_color_info(color_data)
        
        print(f"\n📊 Summary:")
        print(f"   Total colors analyzed: {len(color_data)}")
        print(f"   Most prominent color: {color_data[0][0]} ({color_data[0][2]:.2f}%)")
        
        # Calculate color diversity
        total_percentage = sum(percentage for _, _, percentage in color_data)
        print(f"   Top colors coverage: {total_percentage:.2f}%")
        
    else:
        print("❌ Failed to analyze logo colors")

if __name__ == "__main__":
    main()
