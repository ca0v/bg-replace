#!/usr/bin/env python3
"""
Download and extract the CelebA aligned faces dataset.
Dataset: img_align_celeba.zip
Source: CelebA (Large-scale CelebFaces Attributes Dataset)
"""

import os
import sys
import zipfile
from pathlib import Path
import urllib.request
from tqdm import tqdm

# Configuration
DATA_DIR = Path("./data")
DATASET_ZIP = DATA_DIR / "img_align_celeba.zip"
DATASET_FOLDER = DATA_DIR / "img_align_celeba"
DATASET_URL = "https://drive.google.com/uc?export=download&id=0B7EVK8r0v71pZjFTYXZWM3FlRnM"

# Alternative: Manual download link
# https://www.kaggle.com/datasets/jessicali9530/celeba-dataset
MANUAL_DOWNLOAD_MSG = """
Note: Google Drive direct download may require authentication.

Alternative download options:
1. Kaggle: https://www.kaggle.com/datasets/jessicali9530/celeba-dataset
2. Official site: http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html

After downloading, place 'img_align_celeba.zip' in the './data' directory.
"""

class DownloadProgressBar(tqdm):
    """Progress bar for download."""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_file(url: str, output_path: str):
    """Download file with progress bar."""
    print(f"Downloading from: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc="Downloading") as t:
            urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
        print("✓ Download complete")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        print(MANUAL_DOWNLOAD_MSG)
        return False

def extract_zip(zip_path: str, extract_to: str = "."):
    """Extract zip file with progress bar."""
    print(f"\nExtracting: {zip_path}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            members = zip_ref.namelist()
            print(f"Files in archive: {len(members)}")
            
            # Extract with progress
            with tqdm(total=len(members), desc="Extracting") as pbar:
                for member in members:
                    zip_ref.extract(member, extract_to)
                    pbar.update(1)
        
        print("✓ Extraction complete")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False

def main():
    print("=" * 60)
    print("CelebA Aligned Faces Dataset Setup")
    print("=" * 60)
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    zip_path = DATASET_ZIP
    folder_path = DATASET_FOLDER
    
    # Check if folder already exists
    if folder_path.exists() and folder_path.is_dir():
        num_files = len(list(folder_path.glob("*.jpg"))) + len(list(folder_path.glob("*.png")))
        print(f"\n✓ Dataset folder already exists: {DATASET_FOLDER}")
        print(f"  Contains {num_files} images")
        
        if num_files > 0:
            print("\nDataset is ready to use!")
            return 0
        else:
            print("\n⚠ Folder exists but appears empty. Will attempt to extract.")
    
    # Check if zip file exists
    if not zip_path.exists():
        print(f"\n✗ Dataset zip not found: {DATASET_ZIP}")
        print("\nAttempting to download...")
        
        # Try to download
        if not download_file(DATASET_URL, str(zip_path)):
            print("\n⚠ Automatic download failed.")
            print(MANUAL_DOWNLOAD_MSG)
            print(f"\nPlace 'img_align_celeba.zip' in: {DATA_DIR.absolute()}")
            return 1
    else:
        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Dataset zip found: {DATASET_ZIP} ({file_size_mb:.1f} MB)")
    
    # Extract if folder doesn't exist or is empty
    if not folder_path.exists() or len(list(folder_path.glob("*.jpg"))) == 0:
        print(f"\nExtracting dataset to: {folder_path}")
        
        if extract_zip(str(zip_path), str(DATA_DIR)):
            num_files = len(list(folder_path.glob("*.jpg"))) + len(list(folder_path.glob("*.png")))
            print(f"\n✓ Dataset ready! Found {num_files} images in {folder_path}")
            return 0
        else:
            return 1
    
    print("\n✓ Dataset is ready!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
