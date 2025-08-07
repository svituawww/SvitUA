#!/bin/bash

# Script to normalize all original carousel images to 150px while maintaining aspect ratio
# This creates new normalized files without modifying originals

echo "Starting image normalization process..."

# Create directory for normalized images
mkdir -p "uploads/2025/06/normalized"

# Counter for progress
count=0
total=46

# Function to normalize image
normalize_image() {
    local input_file="$1"
    local output_file="$2"
    local filename=$(basename "$input_file")
    
    if [ -f "$input_file" ]; then
        echo "Processing ($((++count))/$total): $filename"
        
        # Get image dimensions
        dimensions=$(magick identify -format "%wx%h" "$input_file")
        width=$(echo $dimensions | cut -d'x' -f1)
        height=$(echo $dimensions | cut -d'x' -f2)
        
        echo "  Original size: ${width}x${height}"
        
        # Resize to fit within 150x150 while maintaining aspect ratio
        # The ^ flag means "minimum values" - it will resize so the smallest dimension is 150
        # The > flag means "only if larger" - don't upscale smaller images
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

echo "=== Normalizing Gallery Images ==="
echo ""

# Gallery images
normalize_image "uploads/2025/06/galery-1-1.jpg" "uploads/2025/06/normalized/galery-1-1-150.jpg"
normalize_image "uploads/2025/06/galery-2.jpg" "uploads/2025/06/normalized/galery-2-150.jpg"
normalize_image "uploads/2025/06/galery-3.jpg" "uploads/2025/06/normalized/galery-3-150.jpg"
normalize_image "uploads/2025/06/galery-4.jpg" "uploads/2025/06/normalized/galery-4-150.jpg"
normalize_image "uploads/2025/06/galery-5.jpg" "uploads/2025/06/normalized/galery-5-150.jpg"
normalize_image "uploads/2025/06/galery-6.jpg" "uploads/2025/06/normalized/galery-6-150.jpg"
normalize_image "uploads/2025/06/galery-7.jpg" "uploads/2025/06/normalized/galery-7-150.jpg"
normalize_image "uploads/2025/06/galery-8.jpg" "uploads/2025/06/normalized/galery-8-150.jpg"
normalize_image "uploads/2025/06/galery-9.jpg" "uploads/2025/06/normalized/galery-9-150.jpg"

echo "=== Normalizing Partner Logo Images ==="
echo ""

# Partner logo images
for i in {01..09}; do
    normalize_image "uploads/2025/06/${i}.jpg" "uploads/2025/06/normalized/${i}-150.jpg"
done

for i in {10..37}; do
    normalize_image "uploads/2025/06/${i}.jpg" "uploads/2025/06/normalized/${i}-150.jpg"
done

echo "=== Normalization Complete ==="
echo ""
echo "Summary:"
echo "- Processed $count images"
echo "- All normalized images saved to: uploads/2025/06/normalized/"
echo "- Original images preserved unchanged"
echo ""
echo "Normalization method used:"
echo "- Resizes to fit within 150x150 pixels"
echo "- Maintains original aspect ratio (no cropping/distortion)"
echo "- Only reduces size if original is larger than 150px"
echo "- Preserves quality and proportions"
