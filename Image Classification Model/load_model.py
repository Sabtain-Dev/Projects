import torch
from PIL import Image
import os
from torchvision import transforms

# Define your model architecture
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
MODEL_PATH = "models/best_model.pth"
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file not found at {MODEL_PATH}")
    exit(1)

print("Loading model...")
net = ImprovedCNN()
net.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
net.eval()
print("Model loaded successfully")

# Transform for single image
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Class names
class_names = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# Test on multiple images from a folder
image_folder = 'test-images'
supported_formats = ('.png', '.jpg', '.jpeg', '.webp', '.avif')

print("\nTesting on sample images:")
for img_file in os.listdir(image_folder):
    if img_file.lower().endswith(supported_formats):
        img_path = os.path.join(image_folder, img_file)
        try:
            image = Image.open(img_path).convert("RGB")
            image = transform(image).unsqueeze(0)  # Add batch dim
            with torch.no_grad():
                output = net(image)
                _, predicted = torch.max(output, 1)
                probabilities = torch.nn.functional.softmax(output, dim=1)[0] * 100
            print(f"Image: {img_file:15} --> Predicted: {class_names[predicted.item()]:6} ({probabilities[predicted.item()]:.1f}%)")
        except Exception as e:
            print(f"Error processing {img_file}: {str(e)}")