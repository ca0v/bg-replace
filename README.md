# Background Replacement Desktop App

## Project Overview

A web-based application that enables users to drop a portrait photo and instantly see the same image with the background removed/replaced. The application uses a Python backend that serves both the web interface and handles advanced image processing using machine learning libraries. The frontend is built with HTML, CSS, and TypeScript.

## Architecture

### Frontend (HTML/TypeScript)
- **Platform**: Web-based Single Page Application
- **Build**: TypeScript compiled to single `index.js` bundle
- **Styling**: Single CSS file
- **Responsibilities**:
  - Drag-and-drop interface for image input
  - Display original image (left panel)
  - Display processed image with replaced background (right panel)
  - HTTP API calls to Python backend
  - User controls for background selection/customization

### Backend (Python)
- **Platform**: Python 3.x with Flask/FastAPI
- **Responsibilities**:
  - Serve static web application (HTML, CSS, JS)
  - RESTful API for image processing
  - Background removal using state-of-the-art ML models
  - Portrait segmentation and person detection
  - Image processing and manipulation

## Dependencies & Installation

### Python Backend Setup

The project relies on several powerful Python libraries for image processing and machine learning:

#### Installation Script Analysis

The provided `install_dependencies.sh` script automates the installation of all required Python dependencies. Here's what it does:

**System Requirements** (WSL):
- WSL2 with Ubuntu 20.04+ or Debian
- Requires root/sudo privileges
- Minimum 4GB RAM recommended
- 2GB disk space for dependencies
- Node.js 18+ for TypeScript compilation (frontend development)

**Installation Steps**:

1. **System Packages** (`apt install`)
   - `python3`, `python3-venv`, `python3-pip`: Python runtime and package management
   - `git`: Version control for cloning repositories
   - `cmake`, `build-essential`: Build tools for compiling native extensions
   - `libatlas-base-dev`: Linear algebra library for numerical operations
   - `libgtk-3-dev`: GTK development libraries for GUI operations
   - `libopencv-dev`: OpenCV development headers
   - `ffmpeg`: Video/image codec support

2. **Virtual Environment**
   - Creates an isolated Python environment named `bust_env`
   - Prevents dependency conflicts with system Python packages
   - Must be activated before use: `source bust_env/bin/activate`

3. **PyTorch** (CPU version)
   - Deep learning framework required by Detectron2 and other models
   - CPU-only version for broad compatibility (can be upgraded to CUDA for GPU acceleration)

4. **Core Libraries**:
   - **opencv-python**: Computer vision and image processing operations
   - **mediapipe**: Google's ML framework for pose/face detection
   - **rembg**: Specialized background removal using U2-Net model
   - **numpy**: Numerical computing foundation
   - **pillow**: Python Imaging Library for image I/O

5. **dlib**
   - Advanced face detection and landmark recognition
   - Pre-built wheels available for most platforms

6. **Detectron2**
   - Facebook AI's object detection and segmentation framework
   - Installed from source for latest features
   - Provides state-of-the-art person segmentation

#### Script Validation

✅ **Valid** - The script is well-structured with proper error handling (`set -e`)

⚠️ **Considerations**:
- Script is designed for **WSL2** with Ubuntu/Debian
- Ensure WSL2 is properly configured with sufficient resources (4GB+ RAM)
- Detectron2 installation from source may take 10-15 minutes
- Total download size: ~1-2GB
- Run the script from within WSL: `bash install_dependencies.sh`

#### Frontend Development Dependencies

Install Node.js and TypeScript tools in WSL:
```bash
# Install Node.js 18+ (using nvm recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Install TypeScript and build tools
npm install -g typescript
npm install -g esbuild  # or webpack, rollup for bundling
```

## Planned Features

### Phase 1: Core Functionality
- [ ] Basic drag-and-drop interface
- [ ] Python backend service with REST API
- [ ] Background removal using rembg
- [ ] Side-by-side image comparison view
- [ ] Save processed image

### Phase 2: Enhanced Features
- [ ] Multiple background removal models (rembg, MediaPipe, Detectron2)
- [ ] Custom background color selection
- [ ] Custom background image replacement
- [ ] Edge refinement options
- [ ] Batch processing

### Phase 3: Advanced Features
- [ ] Real-time preview
- [ ] Background blur/bokeh effect
- [ ] Portrait enhancement filters
- [ ] Cloud processing option for heavy workloads

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Frontend UI | HTML5 + CSS3 |
| Frontend Logic | Vanilla JavaScript |
| Web Server | Python Flask 3.1+ |
| Backend Processing | Python 3.12 |
| ML Frameworks | PyTorch 2.9.1, Detectron2 0.6, MediaPipe 0.10 |
| Background Removal | rembg 2.0.69 (U2-Net) |
| Image Processing | OpenCV 4.12, Pillow 12.0, NumPy 2.2 |
| Edge Detection | Custom directional scanning algorithm |
| Communication | HTTP REST API (JSON + base64) |

## API Endpoints

### POST /api/process
Processes an uploaded image with background removal and edge detection.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` file field

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "svg": "<svg>...</svg>",
  "vertices": 20
}
```

### GET /
Serves the main application interface.

### GET /health
Health check endpoint returning service status.

## Development Roadmap

1. ✅ **Setup Development Environment**
   - Installed Python dependencies using npm scripts in WSL2
   - Setup project structure with backend/ and scripts/

2. ✅ **Build Python Backend**
   - Created Flask service for background removal
   - Implemented background removal pipeline with rembg
   - Added /api/process endpoint for image processing
   - Configured static file serving for web assets

3. ✅ **Build Frontend**
   - Created HTML structure with drag-and-drop zones
   - Styled with CSS (gradient design, responsive)
   - Implemented vanilla JavaScript for:
     - File upload handling (drag & drop + click)
     - API client with fetch
     - Image display management
     - UI interactions and controls

4. ✅ **Integration & Testing**
   - Connected frontend to backend API
   - Error handling and user feedback
   - Status updates during processing
   - Interactive edge visualization controls

5. 🚧 **Deployment** (Next Steps)
   - Build production configuration
   - Docker containerization
   - Optional: Cloud deployment (AWS, Azure, GCP)
   - Performance optimization with caching

## Project Structure

```
bg-replace/
├── backend/               # Python Processing Service + Web Server
│   ├── app.py            # Flask application with REST API
│   └── static/           # Served frontend assets
│       ├── index.html    # Single page application
│       ├── styles.css    # Styling with gradient design
│       └── app.js        # Client-side logic (vanilla JS)
├── scripts/              # Background removal & edge detection
│   ├── remove_bg_simple.py       # Basic rembg
│   ├── remove_bg_advanced.py     # 3 methods comparison
│   ├── remove_bg_improved.py     # 4 enhanced methods
│   ├── detect_edges.py           # OpenCV contour detection
│   ├── detect_edges_custom.py    # Directional scanning (FINAL)
│   └── setup_celeba.py           # Dataset management
├── edge_viewer.html      # Development visualization tool
├── package.json          # npm scripts for installation & testing
├── .gitignore           # Excludes bust_env/, data/, models/
├── README.md            # This file
├── PROMPT.md            # AI prompt progression documentation
└── bust_env/            # Python virtual environment (gitignored)
```

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/ca0v/bg-replace.git
cd bg-replace

# Install dependencies (requires WSL2/Ubuntu)
npm run install:all

# Download CelebA dataset (optional, for testing)
npm run setup:celeba
```

### Running the Application
```bash
# Start the Flask server
npm start

# Server runs at http://localhost:5000
# Open in your browser and drop an image!
```

### Testing Edge Detection (Standalone)
```bash
# Test with random CelebA image
npm test

# View results in browser
npm run view:edges
```

## Features Implemented

### ✅ Phase 1: Core Functionality
- [x] Drag-and-drop interface
- [x] Python Flask backend with REST API
- [x] Background removal using rembg
- [x] Side-by-side image comparison view
- [x] Download processed image
- [x] Custom edge detection with directional scanning
- [x] Interactive SVG overlay visualization
- [x] Real-time processing status

### 🚧 Phase 2: Enhanced Features (Planned)
- [ ] Multiple background removal models (rembg, MediaPipe, Detectron2)
- [ ] Custom background color selection
- [ ] Custom background image replacement
- [ ] Edge refinement options
- [ ] Batch processing

### 💡 Phase 3: Advanced Features (Planned)
- [ ] Real-time preview
- [ ] Background blur/bokeh effect
- [ ] Portrait enhancement filters
- [ ] Cloud processing option for heavy workloads

## License

TBD

## Notes

- The Python server runs on localhost during development (e.g., http://localhost:5000)
- Frontend build process bundles TypeScript into a single index.js for simplicity
- The server serves static files from the `/static` directory
- For production, consider:
  - Reverse proxy (nginx) for serving static assets
  - Docker containerization for easy deployment
  - GPU acceleration (CUDA) for significantly improved processing speed
- All development done within WSL2 environment
