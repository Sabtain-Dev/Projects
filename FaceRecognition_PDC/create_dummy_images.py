from PIL import Image, ImageDraw
import os

INPUT_DIR = "images"
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

def create_dummy_image(filename="dummy_face.jpg"):
    """Creates a simple image with a black circle on a white background."""
    img = Image.new('RGB', (400, 400), color = 'white')
    d = ImageDraw.Draw(img)
    # Draw a circle (face-like shape)
    d.ellipse((100, 100, 300, 300), fill = 'black', outline ='black')
    
    path = os.path.join(INPUT_DIR, filename)
    img.save(path)
    print(f"Created dummy image: {path}")
    return path

def generate_test_images(count=10):
    """Generates multiple copies of the dummy image for batch processing."""
    base_path = create_dummy_image()
    
    for i in range(1, count + 1):
        new_filename = f"test_image_{i}.jpg"
        new_path = os.path.join(INPUT_DIR, new_filename)
        os.system(f"cp {base_path} {new_path}")
        print(f"Generated test image: {new_path}")

if __name__ == "__main__":
    generate_test_images(count=10)
    print("Test images generated. Please replace these with actual face images for real-world testing.")
