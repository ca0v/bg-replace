// Global variables
let currentSvg = '';
let overlayVisible = true;
let overlayColor = 'red';
let overlayWidth = 2;

// bg-replace/IMP-1000
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showStatus('Please select an image file.', 'error');
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        showStatus('File size must be under 10MB.', 'error');
        return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('original-image').src = e.target.result;
        document.getElementById('placeholder').style.display = 'none';
        document.getElementById('image-container').style.display = 'block';
        processImage(file);
    };
    reader.readAsDataURL(file);
}

// bg-replace/IMP-1001
async function processImage(file) {
    showStatus('Processing image...', 'processing');
    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            displayResult(result);
            showStatus('Image processed successfully.', 'success');
        } else {
            showStatus(result.error || 'Processing failed.', 'error');
        }
    } catch (error) {
        showStatus('Network error occurred.', 'error');
    }
}

// bg-replace/IMP-1002
function displayResult(result) {
    document.getElementById('placeholder').style.display = 'none';
    document.getElementById('original-image').src = `data:image/png;base64,${result.image}`;
    document.getElementById('processed-image').src = `data:image/png;base64,${result.image}`;
    currentSvg = result.svg;
    updateSvgOverlay();
    document.getElementById('controls').style.display = 'block';
    document.getElementById('processed-image').onload = function() {
        addToHistory(document.getElementById('original-image').src, `data:image/png;base64,${result.image}`);
    };
}

// bg-replace/IMP-1003
function addToHistory(originalSrc, processedSrc) {
    const historyGrid = document.getElementById('history-grid');
    const item = document.createElement('div');
    item.className = 'history-item';
    
    const canvas1 = document.createElement('canvas');
    canvas1.width = 100;
    canvas1.height = 100;
    const ctx1 = canvas1.getContext('2d');
    const img1 = new Image();
    img1.onload = function() {
        ctx1.drawImage(img1, 0, 0, 100, 100);
    };
    img1.src = originalSrc;
    
    const canvas2 = document.createElement('canvas');
    canvas2.width = 100;
    canvas2.height = 100;
    const ctx2 = canvas2.getContext('2d');
    const img2 = new Image();
    img2.onload = function() {
        ctx2.drawImage(img2, 0, 0, 100, 100);
        drawSvgOnCanvas(ctx2, 100, 100);
    };
    img2.src = processedSrc;
    
    item.appendChild(canvas1);
    item.appendChild(canvas2);
    historyGrid.insertBefore(item, historyGrid.firstChild);
}

// bg-replace/IMP-1004
function drawSvgOnCanvas(ctx, width, height) {
    if (!currentSvg) return;
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(currentSvg, 'image/svg+xml');
    const polygon = svgDoc.querySelector('polygon');
    const circles = svgDoc.querySelectorAll('circle');
    
    if (polygon) {
        const points = polygon.getAttribute('points').split(' ').map(p => p.split(',').map(Number));
        ctx.strokeStyle = overlayColor;
        ctx.lineWidth = overlayWidth;
        ctx.beginPath();
        points.forEach((point, i) => {
            const x = point[0] * width;
            const y = point[1] * height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.closePath();
        ctx.stroke();
    }
    
    circles.forEach(circle => {
        const cx = parseFloat(circle.getAttribute('cx')) * width;
        const cy = parseFloat(circle.getAttribute('cy')) * height;
        const r = parseFloat(circle.getAttribute('r')) * Math.min(width, height);
        const fill = circle.getAttribute('fill');
        ctx.fillStyle = fill;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        ctx.fill();
    });
}

// bg-replace/IMP-1005
function updateSvgOverlay() {
    const overlay = document.getElementById('svg-overlay');
    overlay.innerHTML = '';
    if (!currentSvg) return;
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(currentSvg, 'image/svg+xml');
    const svgElement = svgDoc.documentElement;
    overlay.appendChild(svgElement);
    applyOverlayStyles();
}

// bg-replace/IMP-1006
function applyOverlayStyles() {
    const overlay = document.getElementById('svg-overlay');
    const svg = overlay.querySelector('svg');
    if (!svg) return;
    svg.style.display = overlayVisible ? 'block' : 'none';
    const polygon = svg.querySelector('polygon');
    if (polygon) {
        polygon.setAttribute('stroke', overlayColor);
        polygon.setAttribute('stroke-width', overlayWidth / 100); // normalized
    }
}

// bg-replace/IMP-1007
function showStatus(message, type) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    if (type !== 'processing') {
        setTimeout(() => {
            status.style.display = 'none';
        }, 5000);
    } else {
        status.style.display = 'block';
    }
}

// Event listeners (assuming HTML has elements)
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
    
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    // Controls
    document.getElementById('toggle-overlay').addEventListener('change', function(e) {
        overlayVisible = e.target.checked;
        applyOverlayStyles();
    });
    
    document.getElementById('overlay-color').addEventListener('change', function(e) {
        overlayColor = e.target.value;
        applyOverlayStyles();
    });
    
    document.getElementById('overlay-width').addEventListener('input', function(e) {
        overlayWidth = parseInt(e.target.value);
        applyOverlayStyles();
    });
});