import cv2
import numpy as np
import matplotlib.pyplot as plt
import imutils
import tkinter as tk
from tkinter import filedialog, Button, Label, Frame
from PIL import Image, ImageTk
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at: {image_path}")
    return img

def enhance_image(img):
    # Make a copy to avoid modifying the original
    img_copy = img.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to remove noise while preserving edges
    bilateral = cv2.bilateralFilter(gray, 11, 17, 17) # diamter,color space isgma, cordinates sigma
    
    # Apply histogram equalization to improve contrast
    hist_eq = cv2.equalizeHist(bilateral)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) #contrast limit trehshold
    clahe_img = clahe.apply(hist_eq)
    
    return gray, clahe_img

def detect_edges(img):
    # Apply Sobel edge detection in x and y directions
    sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
    
    # Combine x and y gradients
    sobel_combined = cv2.magnitude(sobel_x, sobel_y)
    
    # Convert to 8-bit
    sobel_8u = np.uint8(np.absolute(sobel_combined))
    
    # Apply Canny edge detection with multiple thresholds
    edges1 = cv2.Canny(img, 30, 150)
    edges2 = cv2.Canny(img, 50, 200)
    
    # Combine edge detections
    combined_edges = cv2.bitwise_or(edges1, edges2)
    
    # Morphological operations to close gaps
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(combined_edges, kernel, iterations=1)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return closed

def find_plate_contours(edges, original_img):
    # Find contours
    contours = imutils.grab_contours(cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)) #retrive all contours,compress contours
    
    # Copy image for visualization
    img_with_contours = original_img.copy()
    
    # Filter contours based on multiple criteria
    potential_plates = []
    
    # Draw all contours (for visualization)
    cv2.drawContours(img_with_contours, contours, -1, (0, 0, 255), 1)
    
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:30]:
        area = cv2.contourArea(contour)
        
        # Skip too small contours
        if area < 300:
            continue
            
        # Get perimeter and approximate contour
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # License plates typically have 4 corners (rectangular)
        # But we allow more points to accclearount for imperfect detections
        if len(approx) >= 4 and len(approx) <= 8:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (license plates are typically wider than tall)
            aspect_ratio = float(w) / h
            if 1.0 <= aspect_ratio <= 8.0:
                # Calculate extent (ratio of contour area to bounding rect area)
                extent = float(area) / (w * h)
                
                # License plates typically have high extent (mostly filled rectangle)
                if extent > 0.45:
                    # Calculate solidity (ratio of contour area to convex hull area)
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = float(area) / hull_area if hull_area > 0 else 0
                    
                    # License plates typically have high solidity
                    if solidity > 0.7:
                        # Calculate minimum area rectangle (handles tilted plates)
                        rect = cv2.minAreaRect(contour)
                        box = cv2.boxPoints(rect)
                        box = np.intp(box)
                        
                        # Store results
                        score = 0.6 * extent + 0.4 * solidity  # Weighted score
                        potential_plates.append((box, area, aspect_ratio, score))
                        
                        # Draw potential plate contours in blue
                        cv2.drawContours(img_with_contours, [box], 0, (255, 0, 0), 2)
    
    # Sort potential plates by score
    potential_plates.sort(key=lambda x: x[3], reverse=True)
    
    # Highlight top candidates in green
    for i, (box, _, _, _) in enumerate(potential_plates[:3]):
        cv2.drawContours(img_with_contours, [box], 0, (0, 255, 0), 3)
        
        # Add ranking number
        M = cv2.moments(box)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(img_with_contours, f"#{i+1}", (cx, cy), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return potential_plates, img_with_contours

def extract_plate_regions(original_img, potential_plates):
    extracted_plates = []
    
    for i, (box, _, _, score) in enumerate(potential_plates[:5]):
        # Get rotated rectangle
        rect = cv2.minAreaRect(box)
        width, height = rect[1]
        angle = rect[2]
        
        # Get ROI
        src_pts = box.astype("float32")
        
        # Get width and height of the detected rectangle
        width_rect = int(width)
        height_rect = int(height)
        
        # Set destination points for perspective transform
        dst_pts = np.array([[0, 0],
                           [width_rect - 1, 0],
                           [width_rect - 1, height_rect - 1],
                           [0, height_rect - 1]], dtype="float32")
        
        # Perspective transform
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(original_img, M, (width_rect, height_rect))
        
        # Convert to grayscale
        if warped.size == 0:
            continue
            
        gray_plate = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # Enhance the plate image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced_plate = clahe.apply(gray_plate)
        
        # Store extracted plate with its score
        extracted_plates.append((enhanced_plate, score))
        
    return extracted_plates

def detect_license_plate(image_path):
    # Load the original image
    original_img = load_image(image_path)
    
    # Resize if too large
    max_dim = 1200
    h, w = original_img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        original_img = cv2.resize(original_img, None, fx=scale, fy=scale)
    
    # Create a copy for processing
    img_copy = original_img.copy()
    
    # Enhance image
    gray, enhanced = enhance_image(img_copy)
    
    # Detect edges
    edges = detect_edges(enhanced)
    
    # Find potential license plate contours
    potential_plates, contour_img = find_plate_contours(edges, original_img)
    
    # Extract plate regions
    extracted_plates = extract_plate_regions(original_img, potential_plates)
    
    # Prepare best result image
    result_img = original_img.copy()
    
    if potential_plates:
        # Draw the best plate on the result image
        best_plate = potential_plates[0][0]
        cv2.drawContours(result_img, [best_plate], 0, (0, 255, 0), 3)
        
        # Add label
        M = cv2.moments(best_plate)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"]) - 20
            cv2.putText(result_img, "LICENSE PLATE", (cx - 60, cy), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    # Create a dict to store all results
    results = {
        'original': original_img,
        'preprocessed': enhanced,
        'edges': edges,
        'contour_detection': contour_img,
        'result': result_img,
        'plate_regions': extracted_plates if extracted_plates else None,
        'success': len(potential_plates) > 0
    }
    
    return results

class LicensePlateDetectionApp:
    def __init__(self, root):
        self.root = root
        root.title("License Plate Detection System")
        root.geometry("1200x800")
        
        # Create main frames
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.result_frame = tk.Frame(root)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add buttons to top frame
        self.upload_btn = Button(self.top_frame, text="Upload Image", command=self.upload_image, width=15, height=2)
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        
        self.process_btn = Button(self.top_frame, text="Detect Plate", command=self.process_image, width=15, height=2, state=tk.DISABLED)
        self.process_btn.pack(side=tk.LEFT, padx=10)
        
        self.status_label = Label(self.top_frame, text="Upload an image to start", width=40)
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Result display
        self.result_text = Label(self.top_frame, text="", width=30, fg="green")
        self.result_text.pack(side=tk.RIGHT, padx=10)
        
        # Initialize variables
        self.current_image_path = None
        self.results = None
        self.fig = None
        self.canvas = None
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
        
        if file_path:
            self.current_image_path = file_path
            self.status_label.config(text=f"Image loaded: {os.path.basename(file_path)}")
            self.process_btn.config(state=tk.NORMAL)
            
            # Display uploaded image preview
            img = cv2.imread(file_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.display_preview(img)
    
    def display_preview(self, img):
        # Clear existing figure if any
        if self.fig is not None:
            plt.close(self.fig)
            self.canvas.get_tk_widget().destroy()
            
        # Create preview
        self.fig, ax = plt.subplots(figsize=(6, 4))
        ax.imshow(img)
        ax.set_title("Uploaded Image")
        ax.axis('off')
        
        # Display in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.result_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def process_image(self):
        if not self.current_image_path:
            return
            
        self.status_label.config(text="Processing image... Please wait.")
        self.root.update()
        
        try:
            # Run detection pipeline
            self.results = detect_license_plate(self.current_image_path)
            self.display_results()
            
            if self.results['success']:
                self.status_label.config(text="License plate detection complete!")
                self.result_text.config(text="License plate detected successfully!")
            else:
                self.status_label.config(text="Processing complete!")
                self.result_text.config(text="No license plate detected.")
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.result_text.config(text="")
    
    def display_results(self):
        # Clear existing figure if any
        if self.fig is not None:
            plt.close(self.fig)
            self.canvas.get_tk_widget().destroy()
        
        # Create visualization
        self.fig = plt.figure(figsize=(12, 8))
        
        # Original image
        plt.subplot(2, 3, 1)
        plt.title('Original Image')
        plt.imshow(cv2.cvtColor(self.results['original'], cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        # Preprocessed image
        plt.subplot(2, 3, 2)
        plt.title('Preprocessed Image')
        plt.imshow(self.results['preprocessed'], cmap='gray')
        plt.axis('off')
        
        # Edge detection
        plt.subplot(2, 3, 3)
        plt.title('Edge Detection')
        plt.imshow(self.results['edges'], cmap='gray')
        plt.axis('off')
        
        # Contour detection
        plt.subplot(2, 3, 4)
        plt.title('Contour Detection')
        plt.imshow(cv2.cvtColor(self.results['contour_detection'], cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        # Best license plate (if found)
        plt.subplot(2, 3, 5)
        if self.results['plate_regions'] and len(self.results['plate_regions']) > 0:
            plt.title(f'Best Plate Region (Score: {self.results["plate_regions"][0][1]:.2f})')
            plt.imshow(self.results['plate_regions'][0][0], cmap='gray')
        else:
            plt.title('No Plate Detected')
        plt.axis('off')
        
        # Final result
        plt.subplot(2, 3, 6)
        plt.title('Detection Result')
        plt.imshow(cv2.cvtColor(self.results['result'], cv2.COLOR_BGR2RGB))
        plt.axis('off')
        
        plt.tight_layout()
        
        # Display in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.result_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateDetectionApp(root)
    root.mainloop()