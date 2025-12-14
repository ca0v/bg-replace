#!/bin/bash
# Script to install prerequisites for on-prem bust outline detection using OpenCV, dlib, MediaPipe, Detectron2, and rembg.
# Assumes Ubuntu/Debian Linux; run as root or with sudo.
# Creates a Python virtual environment and installs everything locally.

set -e  # Exit on error

# Update system and install build essentials
apt update
apt install -y python3 python3-venv python3-pip git cmake build-essential libatlas-base-dev libgtk-3-dev libopencv-dev ffmpeg

# Create virtual environment
python3 -m venv bust_env
source bust_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version for broad compatibility)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install core libraries
pip install opencv-python mediapipe rembg[cpu] numpy pillow

# Install dlib (requires cmake; wheels available for many platforms)
pip install dlib

# Install Detectron2 from source (requires torch; adjust for CUDA if available)
git clone https://github.com/facebookresearch/detectron2.git
cd detectron2
pip install -e .
cd ..

echo "Installation complete. Activate environment with: source bust_env/bin/activate"
