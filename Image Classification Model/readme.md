# Image Classification Web Application

A web-based image classification system that can classify images into 10 different categories using a deep learning model built with PyTorch.

## 🎯 Project Overview

This project provides a web interface for image classification using a Convolutional Neural Network (CNN) trained on the CIFAR-10 dataset. Users can upload images or provide image URLs to get real-time predictions.

## 📁 Project Structure
Image-classification-folder/
- ├── models/
- │ ├── best_model.pth # Trained PyTorch model
- │ ├── model_onnx.onnx # Model in ONNX format
- │ └── model_torchscript.pt # Model in TorchScript format
- ├── test-images/ # Sample test images
- ├── web/
- │ ├── serve_model.py # Flask server and main application
- │ ├── index.html # Web interface
- │ ├── style.css # Styling
- │ ├── app/ # Frontend application files
- │ ├── bg/ # Background assets
- │ ├── icon/ # Icons and logos
- │ └── uploads/ # Temporary upload directory
- └── requirements.txt # Python dependencies


## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Image-Classification-Model

2. **Install dependencies**
    pip install -r requirements.txt

3. **Run the application**
    cd web
    python serve_model.py

4. **Access the application**
    Open your web browser and navigate to:
    http://localhost:5000

## 🖼️ Supported Image Categories
The model can classify images into the following 10 categories:

✈️ Airplane
🚗 Car
🐦 Bird
🐱 Cat
🦌 Deer
🐕 Dog
🐸 Frog
🐴 Horse
🚢 Ship
🚚 Truck

## 📊 Features
- Image Upload: Upload images directly from your device
- URL Prediction: Provide image URLs for classification
- Real-time Results: Instant classification with confidence scores
- Multiple Format Support: PNG, JPG, JPEG, GIF, AVIF, WebP
- Detailed Probabilities: See confidence scores for all categories

## 🔧 Technical Details
### Model Architecture
- ImprovedCNN: Custom Convolutional Neural Network
- Layers: 3 convolutional layers with batch normalization
- Activation: ReLU with MaxPooling
- Regularization: Dropout (0.5) to prevent overfitting
- Input Size: 32x32 RGB images
- Output: 10-class classification

### Technologies Used
- Backend: Flask, PyTorch, TorchVision
- Frontend: HTML, CSS, JavaScript
- Image Processing: PIL/Pillow
- Model Formats: PyTorch, ONNX, TorchScript

## 🐛 Troubleshooting
### Common Issues
1. Port already in use
2. Model loading failed
3. Import errors
4. Upload folder issues

## 📈 Performance
- The model achieves good accuracy on CIFAR-10 test images
- Supports batch processing for multiple images
- Optimized for both CPU and GPU inference

## 🤝 Contributing
- Fork the repository
- Create a feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- CIFAR-10 dataset providers
- PyTorch and Flask communities
- Contributors and testers
