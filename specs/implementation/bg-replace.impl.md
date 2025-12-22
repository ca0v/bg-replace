---
artifact: bg-replace
phase: implementation
depends-on: []
references: ["bg-replace.impl"]
last-updated: 2025-12-22
---
# Implementation Specification for bg-replace

## Overview
The bg-replace module is a web-based application for automatic background removal from images and edge detection. It consists of a Flask backend server that processes images using MediaPipe Selfie Segmentation for background removal and OpenCV for edge detection, and a JavaScript frontend that provides a drag-and-drop interface for uploading images, displaying processed results, and allowing interactive visualization of detected edges via SVG overlays.

- **backend/static/app.js** - Frontend JavaScript handling UI interactions, file uploads, and result display.
- **backend/app.py** - Backend Flask server providing API endpoints for image processing using MediaPipe and OpenCV.

## Files Summary
### File: backend/static/app.js
- **Purpose**: Manages the client-side logic for image upload, processing requests, and displaying results with interactive SVG overlays.
- **Classes**: None
- **Interfaces**: None
- **Other Elements**: Global functions for handling file input, processing, display, and UI updates.

### File: backend/app.py
- **Purpose**: Flask web server that handles image background removal using MediaPipe Selfie Segmentation and edge detection using OpenCV.
- **Classes**: None
- **Interfaces**: None
- **Other Elements**: Functions for image processing and Flask route handlers.

## Classes
None

## Interfaces
None

## Other Types
None

## Methods
### handleFile(file) (IMP-1000)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Validates uploaded file type and size, displays the original image, and initiates processing.
- **Parameters**: 
  - file: File object from input or drop event
- **Return Type**: void
- **Algorithm**: Checks if file is an image and under 10MB, reads it as data URL to display, then calls processImage.

### processImage(file) (IMP-1001)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Sends the image file to the backend API for processing and handles the response.
- **Parameters**: 
  - file: File object to process
- **Return Type**: Promise<void>
- **Algorithm**: Shows processing status, creates FormData with file, fetches from /api/process, parses JSON response, calls displayResult on success or shows error.

### displayResult(result) (IMP-1002)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Updates the UI to show the processed image and SVG overlay.
- **Parameters**: 
  - result: Object with image (base64), svg, and vertices count
- **Return Type**: void
- **Algorithm**: Hides placeholder, sets background and processed images, stores SVG content, updates overlay, shows controls, adds to history on image load.

### addToHistory(originalSrc, processedSrc) (IMP-1003)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Creates a canvas preview pair and adds it to the history grid.
- **Parameters**: 
  - originalSrc: Data URL of original image
  - processedSrc: Data URL of processed image
- **Return Type**: void
- **Algorithm**: Creates canvases, draws images on them, draws SVG overlay on processed canvas, prepends to history grid.

### drawSvgOnCanvas(ctx, width, height) (IMP-1004)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Parses SVG content and draws the polygon and vertex circles on a canvas context.
- **Parameters**: 
  - ctx: Canvas 2D context
  - width: Canvas width
  - height: Canvas height
- **Return Type**: void
- **Algorithm**: Parses SVG, extracts polygon points and circles, scales normalized coordinates to canvas size, draws polygon and circles.

### updateSvgOverlay() (IMP-1005)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Updates the SVG overlay element with current SVG content and applies styles.
- **Parameters**: None
- **Return Type**: void
- **Algorithm**: Parses SVG, clears overlay, copies attributes and children, applies overlay styles.

### applyOverlayStyles() (IMP-1006)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Applies current control settings (visibility, color, width) to the SVG overlay.
- **Parameters**: None
- **Return Type**: void
- **Algorithm**: Sets display based on toggle, updates polygon stroke color and width.

### showStatus(message, type) (IMP-1007)
- **Belongs to**: Global scope in backend/static/app.js
- **Description**: Displays status messages with appropriate styling and auto-hide for non-processing messages.
- **Parameters**: 
  - message: String to display
  - type: 'success', 'error', or 'processing'
- **Return Type**: void
- **Algorithm**: Sets text and class, schedules auto-hide after 5 seconds for success/error.

### remove_background(image_bytes) (IMP-1008)
- **Belongs to**: Global scope in backend/app.py
- **Description**: Removes background from image bytes using MediaPipe Selfie Segmentation.
- **Parameters**: 
  - image_bytes: Bytes of input image
- **Return Type**: Tuple of (processed_bytes, image_array)
- **Algorithm**: Loads image with PIL, converts to RGB array, processes with MediaPipe segmenter, creates mask, adds alpha channel, saves as PNG bytes.

### detect_edges(image_array, epsilon_factor=0.002) (IMP-1009)
- **Belongs to**: Global scope in backend/app.py
- **Description**: Detects edges in the processed image array and generates SVG outline.
- **Parameters**: 
  - image_array: RGBA numpy array
  - epsilon_factor: Float for Douglas-Peucker simplification
- **Return Type**: SVG string or None
- **Algorithm**: Extracts alpha channel, scans left and right for edges, approximates contour with cv2, normalizes coordinates, generates SVG with polygon and circles.

### index() (IMP-1010)
- **Belongs to**: Flask app in backend/app.py
- **Description**: Serves the main HTML page.
- **Parameters**: None
- **Return Type**: Flask response
- **Algorithm**: Returns static/index.html file.

### serve_static(path) (IMP-1011)
- **Belongs to**: Flask app in backend/app.py
- **Description**: Serves static files from the static directory.
- **Parameters**: 
  - path: Path relative to static directory
- **Return Type**: Flask response
- **Algorithm**: Returns file from static directory.

### process_image() (IMP-1012)
- **Belongs to**: Flask app in backend/app.py
- **Description**: API endpoint to process uploaded image for background removal and edge detection.
- **Parameters**: None (reads from request.files)
- **Return Type**: JSON response
- **Algorithm**: Validates file, calls remove_background, detect_edges, encodes result as base64, returns JSON with image, svg, vertices.

### health() (IMP-1013)
- **Belongs to**: Flask app in backend/app.py
- **Description**: Health check endpoint.
- **Parameters**: None
- **Return Type**: JSON response
- **Algorithm**: Returns status healthy.

## Data Structures
- Image processing uses numpy arrays for RGBA images.
- SVG content is generated as strings with normalized coordinates.
- History grid uses DOM elements for canvas previews.

## Algorithms
- Background removal: MediaPipe Selfie Segmentation for mask generation.
- Edge detection: Directional scanning for hard edges, contour approximation with Douglas-Peucker.
- SVG generation: Coordinate normalization and XML string formatting.

## Dependencies
- **External Libraries**: Flask, flask-cors, opencv-python, mediapipe, pillow, numpy
- **Internal Dependencies**: None
- **System Requirements**: Python 3.8+, Node.js not required (pure JS frontend)

## Error Handling
- Frontend: Catches fetch errors, displays user-friendly messages.
- Backend: Try-except in process_image, returns JSON error responses.

## Performance Considerations
- Image size limited to 10MB.
- MediaPipe model loaded once at startup.
- SVG coordinates normalized for scalable display.

## Security Considerations
- File type validation for images only.
- Size limit prevents abuse.
- CORS enabled for cross-origin requests.

## Notes
- The application runs on Flask development server.
- SVG overlays are interactive with color and width controls.
- History feature allows previewing multiple processed images.</content>
<parameter name="filePath">/home/ca0v/code/bg-replace/specs/implementation/@bg-replace.impl