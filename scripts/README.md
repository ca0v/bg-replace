# Scripts

Example scripts for testing background removal.

## Scripts

### `remove_bg_simple.py`
Basic background removal using rembg (recommended for best quality).

**Usage:**
```bash
# Activate virtual environment first
source ../bust_env/bin/activate

# Process mugshot1.png (default)
python remove_bg_simple.py

# Process any image
python remove_bg_simple.py path/to/image.jpg

# Specify output path
python remove_bg_simple.py input.jpg output.png
```

### `remove_bg_advanced.py`
Compare multiple background removal methods side-by-side.

**Usage:**
```bash
source ../bust_env/bin/activate

# Compare all methods on mugshot1.png
python remove_bg_advanced.py

# Compare methods on any image
python remove_bg_advanced.py path/to/image.jpg
```

**Output files:**
- `*_rembg.png` - Using U2-Net model (best quality)
- `*_mediapipe.png` - Using MediaPipe segmentation (fast)
- `*_opencv.png` - Using OpenCV GrabCut (basic)

## Requirements

All scripts require the virtual environment to be activated:
```bash
source ../bust_env/bin/activate
```

The required libraries are already installed:
- rembg
- opencv-python
- mediapipe
- pillow

## Test Image

Place your test image as `mugshot1.png` in the project root, or specify a different path when running the scripts.
