#!/bin/bash

echo "Processing partner logo images 02-09..."

# Function to normalize a single image
normalize_image() {
    local input_file="$1"
    local output_file="$2"
    local filename=$(basename "$input_file")
    
    if [ -f "$input_file" ]; then
        echo "Processing: $filename"
        
        # Get image dimensions
        dimensions=$(magick identify -format "%wx%h" "$input_file")
        width=$(echo $dimensions | cut -d'x' -f1)
        height=$(echo $dimensions | cut -d'x' -f2)
        
        echo "  Original size: ${width}x${height}"
        
        # Resize to fit within 150x150 while maintaining aspect ratio
        magick "$input_file" -resize "150x150>" "$output_file"
        
        # Get new dimensions
        new_dimensions=$(magick identify -format "%wx%h" "$output_file")
        echo "  Normalized size: $new_dimensions"
        echo "  ✓ Saved to: $output_file"
    else
        echo "  ✗ File not found: $input_file"
    fi
    echo ""
}

# Create normalized directory if it doesn't exist
mkdir -p uploads/2025/06/normalized

# Process 02-09.jpg files and create both 02-150.jpg and 2-150.jpg versions
for i in {2..9}; do
    # Check if 0X.jpg exists
    if [ -f "uploads/2025/06/0${i}.jpg" ]; then
        # Create normalized version as X-150.jpg (to match JSON expectations)
        normalize_image "uploads/2025/06/0${i}.jpg" "uploads/2025/06/normalized/${i}-150.jpg"
    fi
done

echo "Processing complete!"
echo "Created normalized versions of 02.jpg-09.jpg as 2-150.jpg-9-150.jpg"
