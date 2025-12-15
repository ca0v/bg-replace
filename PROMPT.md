# AI Development Session Prompts

This document captures the incremental progression of prompts used to develop this project. These prompts can be reused with future AI models to reproduce or extend the functionality.

## Session Context

**Development Environment**: WSL2 (Ubuntu/Debian)  
**Initial Goal**: Create a background removal application  
**Final Implementation**: Web-based app with Python ML backend + edge detection

---

## Phase 1: Project Initialization

### Prompt 1: Project Planning
```
Create a README.md file to document a plan for a windows desktop app that allows the user to drop a portrait photo into the left side of the form and show the same photo on the right size of the form but with the background replaced
```

**Expected Output**: README.md with architecture plan

### Prompt 2: Architecture Pivot
```
use HTML and typescript
```

**Expected Output**: Updated README.md with web-based architecture for WSL compatibility

---

## Phase 2: Environment Setup

### Prompt 3: Package Management
```
Create package.json that has decomposed the bash script into separate installation scripts that can be run with npm run install:X
```

**Expected Output**: package.json with granular install scripts (install:system, install:pytorch, install:core, etc.)

### Prompt 4: Installation Execution
```
Run the installation and fix any errors
```

**Expected Output**: 
- Fixed Detectron2 installation (--no-build-isolation flag)
- Complete ML environment with PyTorch, OpenCV, MediaPipe, rembg, dlib, Detectron2

### Prompt 5: Version Control Setup
```
Generate a .gitignore
```

**Expected Output**: .gitignore excluding bust_env/, detectron2/, data/, models/, node_modules/

### Prompt 6: Git Configuration
```
Set my git user.name to 'Corey'
```

**Expected Output**: Git configured with user.name and user.email

---

## Phase 3: Background Removal Implementation

### Prompt 7: Test Scripts
```
Create a 'scripts' folder that has some simple examples/tests using what was installed
```

**Expected Output**: 
- scripts/remove_bg_simple.py (basic rembg)
- scripts/remove_bg_advanced.py (compares 3 methods)

### Prompt 8: NPM Integration
```
Add those commands to package.json
```

**Expected Output**: test:bg-simple, test:bg-advanced scripts added

### Prompt 9: Basic Test
```
npm run test:bg
```

**Expected Output**: mugshot1_no_bg.png generated from mugshot1.png

### Prompt 10: Dataset Integration
```
Add a script that checks for the zip file (img_align_celeba.zip) in the ./data folder and if found, extracts it. If not found, tell the user how to download it.
```

**Expected Output**: scripts/setup_celeba.py with dataset handling

### Prompt 11: Random Testing
```
add a 'test:bg:random' script that picks a random image from the CelebA dataset
```

**Expected Output**: test:bg:random script in package.json

### Prompt 12: Quality Assessment
```
All three models fail in different ways. What are some ideas for improvement?
```

**Expected Output**: 
- Analysis of failure modes
- scripts/remove_bg_improved.py with 4 enhanced methods (morphological operations, alpha matting, hybrid, ensemble)

---

## Phase 4: Edge Detection Development

### Prompt 13: Edge Detection Foundation
```
Add edge detector library and utilize it to generate a polygon of the outline of the person. Save this as an SVG file with normalized coordinates (0-100 range).
```

**Expected Output**:
- scripts/detect_edges.py with OpenCV contour detection
- Normalized SVG output with viewBox="0 0 100 100"

### Prompt 14: Interactive Visualization
```
Create an HTML file that displays the background-removed image with the SVG polygon overlay. Include a checkerboard background pattern to visualize transparency. Add controls for stroke color, width, and opacity.
```

**Expected Output**: edge_viewer.html with interactive controls

### Prompt 15: Parameter Tuning (Iteration 1)
```
The edge detection is capturing too many points. Adjust epsilon_factor to simplify the polygon to approximately 15-20 vertices.
```

**Expected Output**: epsilon_factor=0.004 producing ~16 vertices from ~181 contour points

### Prompt 16: Custom Edge Detector
```
Generate a python script that accepts a jpg, scans top-to-bottom, bottom-to-top, left-to-right, right-to-left to determine where the first non-transparent pixel is. Convert that to a contour then reduce the number of points and convert them to a normalize svg outline as previously implemented.
```

**Expected Output**: scripts/detect_edges_custom.py with directional scanning

### Prompt 17: Point Ordering
```
The edge_points need to be sorted along the x axis to generate a simple polygon.
```

**Expected Output**: Angle-based sorting from centroid (prevents self-intersection)

### Prompt 18: Phantom Pixel Detection
```
Perhaps there are phantom non-transparent pixels. Test a few pixels further into the scan and if transparent is found, keep going until a non-transparent is found and repeat this until three non-transparent pixels are found in sequence.
```

**Expected Output**: 3-pixel validation with phantom detection logging

### Prompt 19: Diagnostic Output
```
Log if any such scenario is encountered. I am seeing transparent pixels within the polygon, which should not be the case, but I do not know why.
```

**Expected Output**: Enhanced logging showing phantom pixels and missing edges

### Prompt 20: Debug Visualization
```
That is not the issue, I wonder if the SVG is just being rendered in the wrong position. Lets do this...inject red pixels into the source image at all the edge points. This way I will know if our edge positions are wrong or if the SVG is misaligned.
```

**Expected Output**: mugshot1_no_bg_edges_debug.png with red markers at edge points

### Prompt 21: Edge Threshold Refinement
```
You are setting 9 pixels, only set one.
```

**Expected Output**: Single-pixel markers instead of 3x3 circles

### Prompt 22: Hard Edge Detection
```
Okay, that was helpful. We need a more aggressive scan...the pixel has to have strong color presence and strong opacity to count as not transparent. There is some blending going on that I want to ignore. I want to find the hard edges.
```

**Expected Output**: ALPHA_THRESHOLD=240, COLOR_THRESHOLD=30 for hard edge detection

### Prompt 23: Boundary Adjustment
```
That is one pixel too aggressive.
```

**Expected Output**: Boundary pixel marked one pixel outside the solid edge

### Prompt 24: UI Enhancement
```
Perfect. Add the original image to the HTML page.
```

**Expected Output**: edge_viewer.html with side-by-side original and processed images

### Prompt 25: Layout Fix
```
The original image should be on the left, the altered one to the right of it.
```

**Expected Output**: flex-wrap: nowrap with left-to-right ordering

### Prompt 26: Unified Test Script
```
Add a single npm script called "test" which picks a random image, runs the simple background replacement, generates edge detection.
```

**Expected Output**: Single "test" script combining all operations

### Prompt 27: Build Optimization
```
Use npm-run-all to simplify package.json
```

**Expected Output**: package.json using npm-run-all -s for sequential script execution

### Prompt 28: Color Bias Removal
```
Black is a common hair color so I think the scan should not bias against that color. We are looking for pixels that are strongly not transparent.
```

**Expected Output**: Removed COLOR_THRESHOLD, keeping only ALPHA_THRESHOLD>=240

### Prompt 29: Scanning Simplification
```
I am not understanding a problem in the sorting of the edge points. There is really no need to scan from the bottom or top in my scenario.
```

**Expected Output**: Left/right horizontal scanning only (eliminates top/bottom scans)

### Prompt 30: Sequential Ordering
```
The scan should be from bottom left to top left and then from top-right to bottom-right. Do not sort the edge_points.
```

**Expected Output**: 
- Left scan: bottom-to-top
- Right scan: top-to-bottom  
- No angle sorting (natural scan order preserved)

### Prompt 31: Repository Publishing
```
Push changes to https://github.com/ca0v/bg-replace
```

**Expected Output**: Repository initialized and pushed to GitHub

### Prompt 32: Full Application Implementation
```
You now have enough information to implement the application. The user drops a mugshot into the left/receiving photo, the browser renders the image, sends it to the server which does a background removal and edge detection and responds with the new image and svg outline.
```

**Expected Output**:
- backend/app.py: Flask server with /api/process endpoint
- backend/static/index.html: Drag-and-drop interface
- backend/static/styles.css: Modern gradient design
- backend/static/app.js: Client-side logic (fetch API, image handling, controls)
- Updated package.json with "start" script
- Flask and Flask-CORS installed
- Server running at http://localhost:5000

---

## Phase 5: Application Completion

### Complete Application Features

**Backend (Flask)**:
- `/api/process` endpoint accepts multipart/form-data
- Background removal using rembg
- Edge detection using custom directional scanning
- Returns JSON with base64 image and SVG
- Static file serving for frontend
- CORS enabled for development

**Frontend (Vanilla JS)**:
- Drag & drop or click to upload
- Shows original image (left panel)
- Sends to server via fetch API
- Displays processed image + SVG overlay (right panel)
- Interactive controls: toggle outline, stroke color, stroke width
- Download processed image
- Reset functionality
- Status updates (processing/success/error)

**Key Implementation Details**:
- Image encoding: base64 for network transfer
- SVG overlay: Absolute positioning over processed image
- Checkerboard background: CSS gradients for transparency visualization
- Error handling: Try-catch with user feedback
- File validation: Type and size checks (10MB max)

## Key Implementation Details

### Edge Detection Algorithm (Final Version)
1. Scan left edge: bottom → top, find first 3 consecutive pixels with alpha >= 240
2. Scan right edge: top → bottom, find first 3 consecutive pixels with alpha >= 240
3. Mark boundary pixel one pixel outside the solid edge
4. Preserve scan order (no sorting)
5. Simplify with Douglas-Peucker (epsilon_factor=0.004)
6. Normalize to 0-100 viewBox for resolution independence

### Critical Configuration Values
- **ALPHA_THRESHOLD**: 240 (strong opacity)
- **Consecutive pixels**: 3 (phantom detection)
- **epsilon_factor**: 0.004 (polygon simplification)
- **Boundary offset**: -1 pixel from solid edge

### File Structure
```
backend/
  - app.py (Flask server with /api/process endpoint)
  - static/
    - index.html (drag-and-drop UI)
    - styles.css (gradient design)
    - app.js (vanilla JavaScript)

scripts/
  - remove_bg_simple.py (rembg basic)
  - remove_bg_advanced.py (3 methods comparison)
  - remove_bg_improved.py (4 enhanced methods)
  - detect_edges.py (OpenCV contour)
  - detect_edges_custom.py (directional scan - FINAL)
  - setup_celeba.py (dataset management)

## Phase 8: UI Refinement

### Prompt 33: Background Layer
```
Render a second copy of the original image behind the processed image, but render it with 50% opacity
```

**Expected Output**: 
- Updated index.html with background image element
- Updated styles.css with layered positioning (background at 50% opacity, processed image, SVG overlay)
- Updated app.js to populate background image source
- Z-index layering: background (z-index: 1, opacity: 0.5), processed (z-index: 2), SVG (z-index: 3)

### Prompt 34: SVG Opacity Fix
```
Seems like the svg opacity changed, it should remain 100%
```

**Expected Output**: 
- Updated styles.css with explicit `opacity: 1` and `z-index: 3` on .svg-overlay
- SVG remains fully opaque on top of layered images

---

## Repository Structure (Final)

```
bg-replace/
├── backend/
│   ├── app.py (Flask server with /api/process endpoint)
│   └── static/
│       ├── index.html (drag-and-drop UI with layered images)
│       ├── app.js (fetch API + image layering)
│       └── styles.css (gradient design with z-index layers)
├── scripts/
│   ├── remove_bg_simple.py
│   ├── remove_bg_advanced.py
│   ├── remove_bg_improved.py
│   ├── detect_edges.py
│   ├── detect_edges_custom.py (directional scan - FINAL)
│   └── setup_celeba.py (dataset management)
├── edge_viewer.html (interactive visualization)
├── package.json (npm-run-all scripts + start)
├── PROMPT.md (this file)
└── README.md (project documentation)
```

---

## Reproduction Instructions

1. Start with Prompt 1-2 for project planning
2. Execute Prompts 3-6 for environment setup
3. Run Prompts 7-12 for background removal implementation
4. Execute Prompts 13-30 iteratively for edge detection refinement
5. Execute Prompt 31 for repository setup
6. Execute Prompt 32 for full application implementation
7. Execute Prompts 33-34 for UI layering refinement
8. Run `npm start` to launch the application

Each prompt builds on the previous state - maintain context between prompts.

## Notes for Future Development

- The custom edge detector evolved through multiple iterations based on visual inspection
- Key insight: Black hair required removing color-based filtering
- Scanning direction matters for polygon vertex ordering
- Phantom pixel detection prevents artifacts from anti-aliasing
- Debug visualizations (red pixels, edge markers) were crucial for tuning
- Image layering: Background (50% opacity) → Processed → SVG overlay (100% opacity)

## Extension Opportunities

Based on this foundation, future prompts could explore:
- Multi-person detection and separate outline generation
- Background replacement with texture mapping
- Real-time video processing
- GPU acceleration for batch processing
- Additional background options (solid colors, patterns, gradients)
- Adjustable opacity controls for background layer
