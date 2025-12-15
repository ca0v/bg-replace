#!/usr/bin/env python3
"""
Custom edge detector that scans from all four directions to find boundaries.
Scans top-to-bottom, bottom-to-top, left-to-right, right-to-left to find
the first non-transparent pixel, creating a precise outline.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

def scan_edges_directional(input_path: str, output_svg: str, epsilon_factor=0.004):
    """
    Scan from 4 directions to find edge pixels and create polygon.
    
    Args:
        input_path: Path to PNG with transparency
        output_svg: Output SVG file path
        epsilon_factor: Approximation accuracy for simplification
    """
    print(f"Processing: {input_path}")
    
    # Load image with alpha channel
    image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        print(f"Error: Could not load image")
        return False
    
    height, width = image.shape[:2]
    print(f"Image size: {width}x{height}")
    
    # Extract alpha channel
    if image.shape[2] == 4:
        alpha = image[:, :, 3]
    else:
        # If no alpha, convert to grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # Collect edge points from all four directions
    edge_points = []
    
    def is_solid_edge(start_y, start_x, dy, dx, count=3):
        """Check if 'count' consecutive pixels are non-transparent"""
        for i in range(count):
            ny, nx = start_y + i * dy, start_x + i * dx
            if ny < 0 or ny >= height or nx < 0 or nx >= width:
                return False
            if alpha[ny, nx] <= 1:
                return False
        return True
    
    # Scan from TOP (for each column, find first solid edge from top)
    print("Scanning from top...")
    for x in range(width):
        for y in range(height):
            if is_solid_edge(y, x, 1, 0):  # Check 3 consecutive pixels going down
                edge_points.append((x, y))
                break
    
    # Scan from RIGHT (for each row, find first solid edge from right)
    print("Scanning from right...")
    for y in range(height):
        for x in range(width - 1, -1, -1):
            if is_solid_edge(y, x, 0, -1):  # Check 3 consecutive pixels going left
                edge_points.append((x, y))
                break
    
    # Scan from BOTTOM (for each column, find first solid edge from bottom)
    print("Scanning from bottom...")
    for x in range(width - 1, -1, -1):
        for y in range(height - 1, -1, -1):
            if is_solid_edge(y, x, -1, 0):  # Check 3 consecutive pixels going up
                edge_points.append((x, y))
                break
    
    # Scan from LEFT (for each row, find first solid edge from left)
    print("Scanning from left...")
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if is_solid_edge(y, x, 0, 1):  # Check 3 consecutive pixels going right
                edge_points.append((x, y))
                break
    
    if not edge_points:
        print("Error: No edge points found")
        return False
    
    print(f"Found {len(edge_points)} edge points from directional scanning")
    
    # Sort points by angle from centroid to create simple polygon
    edge_array = np.array(edge_points, dtype=np.float32)
    centroid = edge_array.mean(axis=0)
    
    # Calculate angle from centroid to each point
    angles = np.arctan2(edge_array[:, 1] - centroid[1], 
                        edge_array[:, 0] - centroid[0])
    
    # Sort by angle to get points in order around the perimeter
    sorted_indices = np.argsort(angles)
    edge_points = [edge_points[i] for i in sorted_indices]
    
    # Convert to numpy array for contour processing
    points_array = np.array(edge_points, dtype=np.int32).reshape(-1, 1, 2)
    
    # Simplify using Douglas-Peucker algorithm
    perimeter = cv2.arcLength(points_array, True)
    epsilon = epsilon_factor * perimeter
    simplified_points = cv2.approxPolyDP(points_array, epsilon, True)
    print(f"Simplified to {len(simplified_points)} points")
    
    # Convert to list of tuples
    final_points = simplified_points.reshape(-1, 2)
    
    # Normalize coordinates to 0-100 range
    normalized_points = []
    for x, y in final_points:
        norm_x = (x / width) * 100
        norm_y = (y / height) * 100
        normalized_points.append((norm_x, norm_y))
    
    # Generate SVG with normalized coordinates
    svg_points = " ".join([f"{x:.2f},{y:.2f}" for x, y in normalized_points])
    
    # Generate circle elements for each vertex
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
    print(f"  Polygon has {len(normalized_points)} vertices")
    
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
    
    success = scan_edges_directional(input_path, output_svg)
    
    if success:
        print("\n✓ Done! Run 'npm run view:edges' to see the result")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
