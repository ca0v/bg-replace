#!/usr/bin/env python3
"""
Improved background removal with post-processing and method combining.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path
from rembg import remove
import sys

def refine_mask(mask, blur_size=5, morph_size=5):
    """Apply morphological operations and blur to refine mask edges."""
    # Convert to numpy if PIL Image
    if isinstance(mask, Image.Image):
        mask = np.array(mask)
    
    # Apply morphological closing to fill small holes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Apply morphological opening to remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Blur the edges for smoother transition
    mask = cv2.GaussianBlur(mask, (blur_size, blur_size), 0)
    
    return mask

def remove_bg_enhanced_rembg(input_path: str, output_path: str):
    """Enhanced rembg with edge refinement and contrast adjustment."""
    print("Using enhanced rembg method...")
    
    # Load and remove background
    input_image = Image.open(input_path)
    output_image = remove(input_image)
    
    # Extract alpha channel
    if output_image.mode == 'RGBA':
        r, g, b, alpha = output_image.split()
        
        # Convert to numpy for processing
        alpha_np = np.array(alpha)
        
        # Apply edge refinement
        alpha_refined = refine_mask(alpha_np, blur_size=3, morph_size=3)
        
        # Create new image with refined alpha
        alpha_refined_pil = Image.fromarray(alpha_refined)
        output_image = Image.merge('RGBA', (r, g, b, alpha_refined_pil))
    
    output_image.save(output_path)
    print(f"✓ Saved to: {output_path}")

def remove_bg_hybrid(input_path: str, output_path: str):
    """Hybrid approach: Use rembg for quality, mediapipe for refinement."""
    import mediapipe as mp
    
    print("Using hybrid method (rembg + mediapipe refinement)...")
    
    # Step 1: Get rembg result for overall quality
    input_image = Image.open(input_path)
    rembg_result = remove(input_image)
    
    # Step 2: Get mediapipe mask for better edge detection
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    image_cv = cv2.imread(input_path)
    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_seg:
        results = selfie_seg.process(image_rgb)
        mp_mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
    
    # Step 3: Combine masks - use mediapipe for edges, rembg for quality
    if rembg_result.mode == 'RGBA':
        rembg_alpha = np.array(rembg_result.split()[3])
        
        # Blend the masks: use mediapipe edges where rembg might fail
        # but keep rembg quality in the center
        combined_mask = np.maximum(rembg_alpha * 0.7, mp_mask * 0.5).astype(np.uint8)
        
        # Refine combined mask
        combined_mask = refine_mask(combined_mask, blur_size=5, morph_size=3)
        
        # Apply to original image
        r, g, b = rembg_result.split()[:3]
        alpha_refined = Image.fromarray(combined_mask)
        output_image = Image.merge('RGBA', (r, g, b, alpha_refined))
    else:
        output_image = rembg_result
    
    output_image.save(output_path)
    print(f"✓ Saved to: {output_path}")

def remove_bg_with_matting(input_path: str, output_path: str):
    """Use rembg with trimap for better edge quality."""
    from rembg import remove, new_session
    
    print("Using rembg with alpha matting...")
    
    input_image = Image.open(input_path)
    
    # Use alpha matting for better edges
    session = new_session("u2net")
    output_image = remove(
        input_image,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )
    
    output_image.save(output_path)
    print(f"✓ Saved to: {output_path}")

def remove_bg_ensemble(input_path: str, output_path: str):
    """Ensemble method: Average multiple models for robustness."""
    import mediapipe as mp
    
    print("Using ensemble method (averaging multiple models)...")
    
    # Get rembg mask
    input_image = Image.open(input_path)
    rembg_result = remove(input_image)
    rembg_alpha = np.array(rembg_result.split()[3]) if rembg_result.mode == 'RGBA' else None
    
    # Get mediapipe mask
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    image_cv = cv2.imread(input_path)
    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_seg:
        results = selfie_seg.process(image_rgb)
        mp_mask = (results.segmentation_mask > 0.5).astype(np.uint8) * 255
    
    if rembg_alpha is not None:
        # Average the masks with weights favoring rembg
        ensemble_mask = (rembg_alpha * 0.7 + mp_mask * 0.3).astype(np.uint8)
        
        # Refine
        ensemble_mask = refine_mask(ensemble_mask, blur_size=5, morph_size=5)
        
        # Apply to image
        r, g, b = input_image.split()
        alpha = Image.fromarray(ensemble_mask)
        output_image = Image.merge('RGBA', (r, g, b, alpha))
    else:
        output_image = rembg_result
    
    output_image.save(output_path)
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
    
    # Try improved methods
    methods = [
        ("Enhanced rembg", remove_bg_enhanced_rembg, f"{base_name}_enhanced.png"),
        ("With alpha matting", remove_bg_with_matting, f"{base_name}_matting.png"),
        ("Hybrid (rembg+mediapipe)", remove_bg_hybrid, f"{base_name}_hybrid.png"),
        ("Ensemble average", remove_bg_ensemble, f"{base_name}_ensemble.png"),
    ]
    
    for name, method, output_name in methods:
        try:
            print(f"\n{name}:")
            method(input_path, output_name)
        except Exception as e:
            print(f"✗ Failed: {e}")
        print()
    
    print("=" * 60)
    print("\nDone! Compare results to find the best approach.")
    print("\nRecommendations:")
    print("- Enhanced rembg: Best for general use")
    print("- Alpha matting: Best for fine hair detail")
    print("- Hybrid: Best when both face and edges are important")
    print("- Ensemble: Most robust but may be conservative")

if __name__ == "__main__":
    main()
