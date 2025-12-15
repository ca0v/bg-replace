#!/usr/bin/env python3
"""
Background Removal Web Service
Flask server that processes portrait images and returns background-removed versions with edge detection.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
import io
import base64
from rembg import remove
from PIL import Image

app = Flask(__name__, static_folder='static')
CORS(app)

def remove_background(image_bytes):
    """Remove background from image bytes using rembg"""
    input_image = Image.open(io.BytesIO(image_bytes))
    output_image = remove(input_image)
    
    # Convert to numpy array for further processing
    img_array = np.array(output_image)
    
    # Save to bytes
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    
    return output_buffer.getvalue(), img_array

def detect_edges(image_array, epsilon_factor=0.004):
    """
    Detect edges using directional scanning (left and right)
    Returns SVG string with normalized coordinates
    """
    height, width = image_array.shape[:2]
    
    # Extract alpha channel
    if image_array.shape[2] == 4:
        alpha = image_array[:, :, 3]
    else:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    edge_points = []
    ALPHA_THRESHOLD = 240
    
    def is_hard_edge(y, x):
        if y < 0 or y >= height or x < 0 or x >= width:
            return False
        return alpha[y, x] >= ALPHA_THRESHOLD
    
    def is_solid_edge(start_y, start_x, dy, dx, count=3):
        for i in range(count):
            ny, nx = start_y + i * dy, start_x + i * dx
            if not is_hard_edge(ny, nx):
                return False
        return True
    
    # Scan from LEFT (bottom to top)
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if is_solid_edge(y, x, 0, 1):
                edge_points.append((max(0, x - 1), y))
                break
    
    # Scan from RIGHT (top to bottom)
    for y in range(height):
        for x in range(width - 1, -1, -1):
            if is_solid_edge(y, x, 0, -1):
                edge_points.append((min(width - 1, x + 1), y))
                break
    
    if not edge_points:
        return None
    
    # Convert to numpy array for contour processing
    points_array = np.array(edge_points, dtype=np.int32).reshape(-1, 1, 2)
    
    # Simplify using Douglas-Peucker algorithm
    perimeter = cv2.arcLength(points_array, True)
    epsilon = epsilon_factor * perimeter
    simplified_points = cv2.approxPolyDP(points_array, epsilon, True)
    
    # Convert to list and normalize
    final_points = simplified_points.reshape(-1, 2)
    normalized_points = []
    for x, y in final_points:
        norm_x = (x / width) * 100
        norm_y = (y / height) * 100
        normalized_points.append((norm_x, norm_y))
    
    # Generate SVG
    svg_points = " ".join([f"{x:.2f},{y:.2f}" for x, y in normalized_points])
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
    
    return svg_content

@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/process', methods=['POST'])
def process_image():
    """
    Process uploaded image: remove background and detect edges
    Returns JSON with base64-encoded image and SVG outline
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image bytes
        image_bytes = file.read()
        
        # Remove background
        processed_bytes, image_array = remove_background(image_bytes)
        
        # Detect edges
        svg_outline = detect_edges(image_array)
        
        # Encode processed image as base64
        processed_base64 = base64.b64encode(processed_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{processed_base64}',
            'svg': svg_outline,
            'vertices': len(svg_outline.split('<circle')) - 1 if svg_outline else 0
        })
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'bg-replace'})

if __name__ == '__main__':
    print("Starting Background Removal Service...")
    print("Server running at http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=True)
