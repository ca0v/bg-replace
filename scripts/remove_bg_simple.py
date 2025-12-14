#!/usr/bin/env python3
"""
Simple background removal script using rembg.
Usage: python remove_bg_simple.py [input_image] [output_image]
"""

import sys
from pathlib import Path
from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str = None):
    """Remove background from an image using rembg."""
    
    # Set default output path if not provided
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_no_bg.png")
    
    print(f"Processing: {input_path}")
    
    # Load input image
    try:
        input_image = Image.open(input_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
    
    # Remove background
    print("Removing background...")
    output_image = remove(input_image)
    
    # Save result
    output_image.save(output_path)
    print(f"✓ Saved to: {output_path}")
    
    return True

if __name__ == "__main__":
    # Default to mugshot1.png if no arguments provided
    if len(sys.argv) < 2:
        input_path = "./mugshot1.png"
        output_path = "./mugshot1_no_bg.png"
    elif len(sys.argv) == 2:
        input_path = sys.argv[1]
        output_path = None
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    
    # Check if input exists
    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        print("Please provide the image or use: python remove_bg_simple.py <input_image> [output_image]")
        sys.exit(1)
    
    success = remove_background(input_path, output_path)
    sys.exit(0 if success else 1)
