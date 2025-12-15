#!/usr/bin/env python3
"""
Edge detection and polygon generation from background-removed image.
Generates a single polygon outline in SVG format.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

def detect_edges_to_polygon(input_path: str, output_svg: str, epsilon_factor=0.0025):
    """
    Detect edges and create a simplified polygon from transparent image.
    
    Args:
        input_path: Path to PNG with transparency
        output_svg: Output SVG file path
        epsilon_factor: Approximation accuracy (lower = more detail)
    """
    print(f"Processing: {input_path}")
    
    # Load image
    image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        print(f"Error: Could not load image")
        return False
    
    height, width = image.shape[:2]
    print(f"Image size: {width}x{height}")
    
    # Extract alpha channel (transparency)
    if image.shape[2] == 4:
        alpha = image[:, :, 3]
    else:
        # If no alpha, convert to grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # Ensure we capture all non-transparent pixels accurately
    # Use a very low threshold to detect any non-zero alpha
    _, binary_mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
    
    # Optional: Apply slight morphological closing to connect nearby pixels
    # This helps with any small gaps in the alpha channel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # Find contours - use CHAIN_APPROX_NONE to capture all boundary pixels
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    if not contours:
        print("Error: No contours found")
        return False
    
    # Get the largest contour (main subject)
    largest_contour = max(contours, key=cv2.contourArea)
    print(f"Found contour with {len(largest_contour)} points")
    
    # Approximate the contour to reduce points (Douglas-Peucker algorithm)
    epsilon = epsilon_factor * cv2.arcLength(largest_contour, True)
    simplified_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
    print(f"Simplified to {len(simplified_contour)} points")
    
    # Convert to polygon points
    points = simplified_contour.reshape(-1, 2)
    
    # Normalize coordinates to 0-100 range
    normalized_points = []
    for x, y in points:
        norm_x = (x / width) * 100
        norm_y = (y / height) * 100
        normalized_points.append((norm_x, norm_y))
    
    # Generate SVG with normalized coordinates
    svg_points = " ".join([f"{x:.2f},{y:.2f}" for x, y in normalized_points])
    
    # Generate circle elements for each vertex (normalized coordinates)
    circles = "\n  ".join([f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.5" fill="white" stroke="black" stroke-width="0.3"/>' 
                           for x, y in normalized_points])
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <polygon points="{svg_points}" 
           fill="none" 
           stroke="red" 
           stroke-width="0.5"
           vector-effect="non-scaling-stroke"/>
  {circles}
</svg>'''
    
    # Save SVG
    with open(output_svg, 'w') as f:
        f.write(svg_content)
    
    print(f"✓ Saved polygon to: {output_svg}")
    print(f"  Polygon has {len(points)} vertices")
    
    return True

def main():
    if len(sys.argv) < 2:
        input_path = "./mugshot1_no_bg.png"
    else:
        input_path = sys.argv[1]
    
    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        print("Run 'npm run test:bg' first to generate the image")
        sys.exit(1)
    
    # Generate output filename
    input_file = Path(input_path)
    output_svg = str(input_file.with_suffix('.svg'))
    
    success = detect_edges_to_polygon(input_path, output_svg)
    
    if success:
        print("\n✓ Done! Run 'npm run view:edges' to see the result")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
