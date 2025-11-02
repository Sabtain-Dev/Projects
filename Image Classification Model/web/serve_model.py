import os
from flask import Flask, request, jsonify, send_from_directory
import torch
from torchvision import transforms
from PIL import Image
import logging
import requests
from io import BytesIO

# Initialize Flask app with correct static folder path
app = Flask(__name__, static_folder='../web', static_url_path='')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'web', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif', 'webp'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model architecture
class ImprovedCNN(torch.nn.Module):
    def __init__(self):
        super(ImprovedCNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = torch.nn.BatchNorm2d(32)
        self.conv2 = torch.nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = torch.nn.BatchNorm2d(64)
        self.conv3 = torch.nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = torch.nn.BatchNorm2d(128)
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.fc1 = torch.nn.Linear(128 * 4 * 4, 256)
        self.fc2 = torch.nn.Linear(256, 128)
        self.fc3 = torch.nn.Linear(128, 10)
        self.dropout = torch.nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(torch.nn.functional.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.nn.functional.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.nn.functional.relu(self.bn3(self.conv3(x))))
        x = torch.flatten(x, 1)
        x = self.dropout(torch.nn.functional.relu(self.fc1(x)))
        x = self.dropout(torch.nn.functional.relu(self.fc2(x)))
        x = self.fc3(x)
        return x

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model.pth')
try:
    model = ImprovedCNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    logger.info("Model loaded successfully from %s", MODEL_PATH)
except Exception as e:
    logger.error("Failed to load model: %s", str(e))
    raise

CLASS_NAMES = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    """Basic URL validation"""
    return url.startswith(('http://', 'https://')) and any(url.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filename)
        
        image = Image.open(filename).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0] * 100
            _, predicted = torch.max(outputs, 1)
            predicted_class = CLASS_NAMES[predicted.item()]

        return jsonify({
            "class": predicted_class,
            "confidence": round(probabilities[predicted.item()].item(), 2),
            "all_probabilities": {CLASS_NAMES[i]: round(probabilities[i].item(), 2) 
                                for i in range(len(CLASS_NAMES))}
        })

    except Exception as e:
        logger.error("Prediction error: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/predict-url", methods=["POST"])
def predict_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    try:
        if not is_valid_url(data['url']):
            return jsonify({"error": "Invalid image URL"}), 400

        # Download the image from the URL with timeout
        response = requests.get(data['url'], timeout=10)
        response.raise_for_status()
        
        # Open the image
        image = Image.open(BytesIO(response.content)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0] * 100
            _, predicted = torch.max(outputs, 1)
            predicted_class = CLASS_NAMES[predicted.item()]

        return jsonify({
            "class": predicted_class,
            "confidence": round(probabilities[predicted.item()].item(), 2),
            "all_probabilities": {CLASS_NAMES[i]: round(probabilities[i].item(), 2) 
                                for i in range(len(CLASS_NAMES))}
        })

    except requests.exceptions.RequestException as e:
        logger.error("URL request error: %s", str(e))
        return jsonify({"error": "Failed to fetch image from URL"}), 400
    except Exception as e:
        logger.error("URL prediction error: %s", str(e))
        return jsonify({"error": str(e)}), 500  

if __name__ == "__main__":
    # Print the static folder path for debugging
    print(f"Static folder path: {os.path.abspath(app.static_folder)}")
    print(f"Static files available: {os.listdir(app.static_folder)}")
    app.run(host='0.0.0.0', port=5000, debug=True)