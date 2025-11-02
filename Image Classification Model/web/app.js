// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('imageInput');
const imageUrlInput = document.getElementById('imageUrl');
const fetchUrlBtn = document.getElementById('fetchUrl');
const resultDiv = document.getElementById('result');
const imagePreview = document.getElementById('imagePreview');

// Animation Configuration
const loadingAnimations = [
  '🕒 Analyzing pixels...',
  '🔍 Identifying patterns...',
  '🧠 Making predictions...',
  '🎯 Finalizing results...'
];

// Utility Functions
function extractDirectImageUrl(googleUrl) {
  try {
    const url = new URL(googleUrl);
    const imgurlParam = url.searchParams.get('imgurl');
    return imgurlParam ? decodeURIComponent(imgurlParam) : null;
  } catch {
    return null;
  }
}

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight() {
  dropZone.classList.add('highlight');
}

function unhighlight() {
  dropZone.classList.remove('highlight');
}

function showLoadingAnimation() {
  let counter = 0;
  resultDiv.innerHTML = `<div class="processing">${loadingAnimations[0]}</div>`;
  
  const interval = setInterval(() => {
    counter = (counter + 1) % loadingAnimations.length;
    resultDiv.innerHTML = `<div class="processing">${loadingAnimations[counter]}</div>`;
  }, 1000);
  
  return interval;
}

function displayPreview(file) {
  if (typeof file === 'string') {
    imagePreview.src = file;
    imagePreview.style.display = 'block';
  } else {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}

function displayResult(data) {
  const sortedClasses = Object.entries(data.all_probabilities)
    .sort((a, b) => b[1] - a[1]);

  resultDiv.innerHTML = `
    <div class="result-card">
      <h3>Prediction Result</h3>
      <div class="prediction-main">
        <span class="predicted-class">${data.class}</span>
        <span class="confidence">${data.confidence}% confidence</span>
      </div>
      <div class="probabilities">
        <h4>All Probabilities:</h4>
        <ul>
          ${sortedClasses.map(([cls, prob]) => `
            <li class="${cls === data.class ? 'top-prediction' : ''}">
              <span class="class-name">${cls}</span>
              <span class="class-prob">${prob}%</span>
              <div class="probability-bar" style="width: ${prob}%"></div>
            </li>
          `).join('')}
        </ul>
      </div>
    </div>
  `;
}

function showError(message) {
  resultDiv.innerHTML = `<div class="error">${message}</div>`;
}

// Event Handlers
function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files.length) {
    fileInput.files = files;
    handleFiles({ target: fileInput });
  }
}

function handleFiles(e) {
  const files = e.target.files;
  if (files.length) {
    const file = files[0];
    displayPreview(file);
    
    const loadingInterval = showLoadingAnimation();
    
    setTimeout(() => {
      uploadFile(file);
      clearInterval(loadingInterval);
    }, 5000 + Math.random() * 5000);
  }
}

function handleUrl() {
  const imageUrl = imageUrlInput.value.trim();
  if (!imageUrl) {
    showError('Please enter a valid URL');
    return;
  }

  let finalUrl = imageUrl.includes('google.com/imgres') 
    ? extractDirectImageUrl(imageUrl) 
    : imageUrl;

  if (!finalUrl) {
    showError('Could not extract image URL from Google link');
    return;
  }

  if (!/^https?:\/\/.+(\.(jpe?g|png|gif|webp|avif))($|\?)/i.test(finalUrl)) {
    showError('Please enter a valid image URL (jpg, png, gif, webp, avif)');
    return;
  }

  imagePreview.src = finalUrl;
  imagePreview.style.display = 'block';
  
  const loadingInterval = showLoadingAnimation();
  
  setTimeout(() => {
    fetch('/predict-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: finalUrl })
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw new Error(err.error); });
      }
      return response.json();
    })
    .then(data => {
      displayResult(data);
      clearInterval(loadingInterval);
    })
    .catch(error => {
      showError(error.message);
      clearInterval(loadingInterval);
    });
  }, 2000 + Math.random() * 2000);
}

function uploadFile(file) {
  const formData = new FormData();
  formData.append('image', file);

  fetch('/predict', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => { throw new Error(err.error); });
    }
    return response.json();
  })
  .then(data => {
    displayResult(data);
  })
  .catch(error => {
    showError(error.message);
  });
}

// Event Listeners
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, preventDefaults, false);
  document.body.addEventListener(eventName, preventDefaults, false);
});

['dragenter', 'dragover'].forEach(eventName => {
  dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, unhighlight, false);
});

dropZone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', handleFiles);
fetchUrlBtn.addEventListener('click', handleUrl);
imageUrlInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleUrl();
});