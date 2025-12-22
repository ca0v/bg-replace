from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import io
import base64
import json

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmenter = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# bg-replace/IMP-1008
def remove_background(image_bytes):
    """
    Removes background from image bytes using MediaPipe Selfie Segmentation.
    """
    # Load image with PIL
    image = Image.open(io.BytesIO(image_bytes))
    image_array = np.array(image.convert('RGB'))
    
    # Process with MediaPipe
    results = segmenter.process(image_array)
    mask = results.segmentation_mask
    
    # Create mask
    mask = (mask > 0.5).astype(np.uint8) * 255
    
    # Add alpha channel
    rgba = np.concatenate([image_array, mask[:, :, np.newaxis]], axis=2)
    
    # Convert back to PIL and save as PNG bytes
    processed_image = Image.fromarray(rgba, 'RGBA')
    output = io.BytesIO()
    processed_image.save(output, format='PNG')
    processed_bytes = output.getvalue()
    
    return processed_bytes, rgba

# bg-replace/IMP-1009
def detect_edges(image_array, epsilon_factor=0.002):
    """
    Detects edges in the processed image array and generates SVG outline.
    """
    # Extract alpha channel
    alpha = image_array[:, :, 3]
    
    # Scan left and right for edges
    edges = []
    height, width = alpha.shape
    for y in range(height):
        left_edge = None
        right_edge = None
        for x in range(width):
            if alpha[y, x] > 128:
                left_edge = x
                break
        for x in range(width - 1, -1, -1):
            if alpha[y, x] > 128:
                right_edge = x
                break
        if left_edge is not None and right_edge is not None:
            edges.append((left_edge, y))
            edges.append((right_edge, y))
    
    if not edges:
        return None
    
    # Approximate contour
    edges = np.array(edges, dtype=np.float32)
    epsilon = epsilon_factor * cv2.arcLength(edges, True)
    approx = cv2.approxPolyDP(edges, epsilon, True)
    
    # Normalize coordinates
    points = []
    for point in approx:
        x, y = point[0]
        points.append((x / width, y / height))
    
    # Generate SVG
    svg_points = ' '.join(f'{x},{y}' for x, y in points)
    svg = f'<svg width="100%" height="100%" viewBox="0 0 1 1" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<polygon points="{svg_points}" fill="none" stroke="red" stroke-width="0.005"/>'
    for x, y in points:
        svg += f'<circle cx="{x}" cy="{y}" r="0.01" fill="blue"/>'
    svg += '</svg>'
    
    return svg

# bg-replace/IMP-1010
@app.route('/')
def index():
    """
    Serves the main HTML page.
    """
    return send_from_directory('static', 'index.html')

# bg-replace/IMP-1011
@app.route('/static/<path:path>')
def serve_static(path):
    """
    Serves static files from the static directory.
    """
    return send_from_directory('static', path)

# bg-replace/IMP-1012
@app.route('/api/process', methods=['POST'])
def process_image():
    """
    API endpoint to process uploaded image for background removal and edge detection.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            return jsonify({'error': 'Invalid file type'}), 400
        
        image_bytes = file.read()
        
        # Remove background
        processed_bytes, image_array = remove_background(image_bytes)
        
        # Detect edges
        svg = detect_edges(image_array)
        
        # Encode to base64
        image_b64 = base64.b64encode(processed_bytes).decode('utf-8')
        
        vertices = len(svg.split('<circle')) - 1 if svg else 0
        
        return jsonify({
            'image': image_b64,
            'svg': svg,
            'vertices': vertices
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# bg-replace/IMP-1013
@app.route('/health')
def health():
    """
    Health check endpoint.
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)