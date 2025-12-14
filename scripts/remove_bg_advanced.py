#!/usr/bin/env python3
"""
Advanced background removal script with multiple methods.
Supports: rembg (U2-Net), MediaPipe, and basic OpenCV approaches.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

def remove_bg_rembg(input_path: str, output_path: str):
    """Remove background using rembg (U2-Net model) - most accurate."""
    from rembg import remove
    
    print("Using rembg (U2-Net) method...")
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    output_image.save(output_path)
    print(f"✓ Saved to: {output_path}")

def remove_bg_mediapipe(input_path: str, output_path: str):
    """Remove background using MediaPipe selfie segmentation."""
    import mediapipe as mp
    
    print("Using MediaPipe segmentation method...")
    
    # Initialize MediaPipe
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    
    # Read image
    image = cv2.imread(input_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_seg:
        results = selfie_seg.process(image_rgb)
        
        # Create mask (threshold the segmentation)
        mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
        
        # Apply mask to create transparent background
        b, g, r = cv2.split(image)
        rgba = [r, g, b, mask]
        output_image = cv2.merge(rgba)
        
        # Save
        cv2.imwrite(output_path, output_image)
    
    print(f"✓ Saved to: {output_path}")

def remove_bg_opencv_simple(input_path: str, output_path: str):
    """Simple background removal using OpenCV GrabCut algorithm."""
    print("Using OpenCV GrabCut method...")
    
    # Read image
    image = cv2.imread(input_path)
    mask = np.zeros(image.shape[:2], np.uint8)
    
    # Define rectangle around the subject (assuming centered portrait)
    h, w = image.shape[:2]
    rect = (int(w*0.1), int(h*0.1), int(w*0.8), int(h*0.8))
    
    # Initialize background/foreground models
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    # Apply GrabCut
    cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    
    # Create binary mask
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    
    # Apply mask
    b, g, r = cv2.split(image)
    alpha = mask2 * 255
    rgba = [r, g, b, alpha]
    output_image = cv2.merge(rgba)
    
    # Save
    cv2.imwrite(output_path, output_image)
    print(f"✓ Saved to: {output_path}")

def main():
    if len(sys.argv) < 2:
        input_path = "./mugshot1.png"
    else:
        input_path = sys.argv[1]
    
    if not Path(input_path).exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)
    
    input_file = Path(input_path)
    base_name = input_file.stem
    
    print(f"\nProcessing: {input_path}\n")
    print("=" * 60)
    
    # Try different methods
    methods = [
        ("rembg", remove_bg_rembg, f"{base_name}_rembg.png"),
        ("mediapipe", remove_bg_mediapipe, f"{base_name}_mediapipe.png"),
        ("opencv", remove_bg_opencv_simple, f"{base_name}_opencv.png"),
    ]
    
    for name, method, output_name in methods:
        try:
            method(input_path, output_name)
        except Exception as e:
            print(f"✗ {name} method failed: {e}")
        print()
    
    print("=" * 60)
    print("\nDone! Compare the results to see which method works best.")

if __name__ == "__main__":
    main()
