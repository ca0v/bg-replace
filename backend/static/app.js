// Background Removal Application
// Handles image upload, processing, and visualization

const dropZone = document.getElementById('dropZone');
const dropZoneContent = document.getElementById('dropZoneContent');
const originalImage = document.getElementById('originalImage');
const resultZone = document.getElementById('resultZone');
const resultPlaceholder = document.getElementById('resultPlaceholder');
const resultContainer = document.getElementById('resultContainer');
const processedImage = document.getElementById('processedImage');
const backgroundImage = document.getElementById('backgroundImage');
const svgOverlay = document.getElementById('svgOverlay');
const status = document.getElementById('status');
const controls = document.getElementById('controls');

const toggleOverlay = document.getElementById('toggleOverlay');
const strokeColor = document.getElementById('strokeColor');
const strokeWidth = document.getElementById('strokeWidth');
const strokeWidthValue = document.getElementById('strokeWidthValue');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const historyGrid = document.getElementById('historyGrid');

let currentSvgContent = null;

// File input for click-to-browse
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.accept = 'image/*';
fileInput.style.display = 'none';
document.body.appendChild(fileInput);

// Drag and drop handlers
dropZone.addEventListener('click', () => {
    fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// bg-replace/IMP-1000
function handleFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showStatus('Please select an image file', 'error');
        return;
    }
    
    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
        showStatus('File size must be less than 10MB', 'error');
        return;
    }
    
    // Display original image
    const reader = new FileReader();
    reader.onload = (e) => {
        originalImage.src = e.target.result;
        originalImage.style.display = 'block';
        dropZoneContent.style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // Send to server for processing
    processImage(file);
}

// bg-replace/IMP-1001
async function processImage(file) {
    showStatus('Processing image...', 'processing');
    
    // Show spinner in result area
    resultPlaceholder.innerHTML = '<div class="spinner"></div><p>Removing background and detecting edges...</p>';
    
    try {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Processing failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayResult(result);
            showStatus(`✓ Success! Detected ${result.vertices} edge vertices`, 'success');
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Processing error:', error);
        showStatus(`Error: ${error.message}`, 'error');
        resultPlaceholder.innerHTML = '<p>Processing failed. Please try again.</p>';
    }
}

// bg-replace/IMP-1002
function displayResult(result) {
    // Hide placeholder, show result container
    resultPlaceholder.style.display = 'none';
    resultContainer.style.display = 'flex';
    
    // Set background image (original at 50% opacity)
    backgroundImage.src = originalImage.src;
    
    // Set processed image
    processedImage.src = result.image;
    
    // Store and display SVG
    currentSvgContent = result.svg;
    updateSvgOverlay();
    
    // Show controls
    controls.style.display = 'flex';
    
    // Setup SVG once image loads
    processedImage.onload = () => {
        updateSvgOverlay();
        addToHistory(originalImage.src, result.image);
    };
}

// bg-replace/IMP-1003
function addToHistory(originalSrc, processedSrc) {
    // Create container for this pair
    const pairContainer = document.createElement('div');
    pairContainer.className = 'history-pair';
    
    // Create canvas for original image
    const originalCanvas = document.createElement('canvas');
    originalCanvas.className = 'history-canvas';
    const originalImg = new Image();
    originalImg.onload = () => {
        originalCanvas.width = originalImg.width;
        originalCanvas.height = originalImg.height;
        const ctx = originalCanvas.getContext('2d');
        ctx.drawImage(originalImg, 0, 0);
    };
    originalImg.src = originalSrc;
    
    // Create canvas for processed image with SVG overlay
    const processedCanvas = document.createElement('canvas');
    processedCanvas.className = 'history-canvas';
    const processedImg = new Image();
    processedImg.onload = () => {
        processedCanvas.width = processedImg.width;
        processedCanvas.height = processedImg.height;
        const ctx = processedCanvas.getContext('2d');
        ctx.drawImage(processedImg, 0, 0);
        
        // Draw SVG outline on canvas
        if (currentSvgContent) {
            drawSvgOnCanvas(ctx, processedCanvas.width, processedCanvas.height);
        }
    };
    processedImg.src = processedSrc;
    
    // Add canvases to pair container
    pairContainer.appendChild(originalCanvas);
    pairContainer.appendChild(processedCanvas);
    
    // Prepend to history grid
    historyGrid.prepend(pairContainer);
}

// bg-replace/IMP-1004
function drawSvgOnCanvas(ctx, width, height) {
    if (!currentSvgContent) return;
    
    // Parse SVG to extract polygon points
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(currentSvgContent, 'image/svg+xml');
    const polygon = svgDoc.querySelector('polygon');
    const circles = svgDoc.querySelectorAll('circle');
    
    if (!polygon) return;
    
    // Get polygon points (normalized 0-100)
    const pointsAttr = polygon.getAttribute('points');
    const points = pointsAttr.split(' ').map(p => {
        const [x, y] = p.split(',').map(Number);
        return {
            x: (x / 100) * width,
            y: (y / 100) * height
        };
    });
    
    // Draw polygon
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.closePath();
    ctx.strokeStyle = strokeColor.value;
    ctx.lineWidth = parseFloat(strokeWidth.value);
    ctx.stroke();
    
    // Draw circles (vertices)
    circles.forEach(circle => {
        const cx = (parseFloat(circle.getAttribute('cx')) / 100) * width;
        const cy = (parseFloat(circle.getAttribute('cy')) / 100) * height;
        const r = (1.5 / 100) * Math.min(width, height);
        
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 0.3;
        ctx.stroke();
    });
}

// bg-replace/IMP-1005
function updateSvgOverlay() {
    if (!currentSvgContent) return;
    
    // Parse SVG
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(currentSvgContent, 'image/svg+xml');
    const svgElement = svgDoc.querySelector('svg');
    
    if (!svgElement) return;
    
    // Clear existing overlay
    svgOverlay.innerHTML = '';
    
    // Copy attributes
    Array.from(svgElement.attributes).forEach(attr => {
        svgOverlay.setAttribute(attr.name, attr.value);
    });
    
    // Copy child elements
    while (svgElement.firstChild) {
        svgOverlay.appendChild(svgElement.firstChild);
    }
    
    // Apply current control settings
    applyOverlayStyles();
}

// bg-replace/IMP-1006
function applyOverlayStyles() {
    const polygon = svgOverlay.querySelector('polygon');
    const circles = svgOverlay.querySelectorAll('circle');
    
    if (!polygon) return;
    
    // Apply visibility
    svgOverlay.style.display = toggleOverlay.checked ? 'block' : 'none';
    
    // Apply stroke color
    polygon.setAttribute('stroke', strokeColor.value);
    
    // Apply stroke width
    const width = parseFloat(strokeWidth.value) * 0.25;
    polygon.setAttribute('stroke-width', width);
}

// Control event listeners
toggleOverlay.addEventListener('change', applyOverlayStyles);

strokeColor.addEventListener('input', applyOverlayStyles);

strokeWidth.addEventListener('input', (e) => {
    strokeWidthValue.textContent = e.target.value;
    applyOverlayStyles();
});

downloadBtn.addEventListener('click', () => {
    if (!processedImage.src) return;
    
    // Create download link
    const link = document.createElement('a');
    link.href = processedImage.src;
    link.download = `background-removed-${Date.now()}.png`;
    link.click();
    
    showStatus('✓ Image downloaded', 'success');
});

resetBtn.addEventListener('click', () => {
    // Reset UI
    originalImage.style.display = 'none';
    originalImage.src = '';
    dropZoneContent.style.display = 'block';
    
    resultPlaceholder.style.display = 'flex';
    resultPlaceholder.innerHTML = '<p>Processed image will appear here</p>';
    resultContainer.style.display = 'none';
    processedImage.src = '';
    backgroundImage.src = '';
    
    controls.style.display = 'none';
    currentSvgContent = null;
    
    status.textContent = '';
    status.className = 'status';
    
    fileInput.value = '';
});

// bg-replace/IMP-1007
function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    
    // Auto-hide success/error messages after 5 seconds
    if (type !== 'processing') {
        setTimeout(() => {
            if (status.className.includes(type)) {
                status.textContent = '';
                status.className = 'status';
            }
        }, 5000);
    }
}

// Initialize
console.log('Background Removal App loaded');
