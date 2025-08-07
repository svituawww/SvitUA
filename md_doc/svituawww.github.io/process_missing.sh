#!/bin/bash

echo "Processing missing partner logo images with leading zeros..."

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

# Process the missing images (01-09)
for i in {01..09}; do
    normalize_image "uploads/2025/06/${i}.jpg" "uploads/2025/06/normalized/${i}-150.jpg"
done

echo "Processing complete!"
