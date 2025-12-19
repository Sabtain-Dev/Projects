import streamlit as st
import cv2
import numpy as np
import os
import time
from multiprocessing import Pool, cpu_count
from PIL import Image
import urllib.request

# --- Configuration ---
CASCADE_PATH = "haarcascade_frontalface_default.xml"
OUTPUT_DIR_PAR = "output_parallel"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR_PAR):
    os.makedirs(OUTPUT_DIR_PAR)

# --- Core Face Detection Logic (Fixed minNeighbors) ---

def detect_faces_on_image(image_data, mode="sequential"):
    """
    Performs face detection on an image (as a numpy array).
    Returns the processed image (numpy array) and the face count.
    """
    # Load the cascade classifier inside the function for multiprocessing compatibility
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        st.error(f"Error: Could not load cascade file: {CASCADE_PATH}. Please ensure it is in the project directory.")
        return image_data, 0, 0.0

    start_time = time.time()
    
    # Convert to grayscale for faster processing
    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)

    # Detect faces with increased minNeighbors for better accuracy
    # minNeighbors=8 is a good balance to reduce false positives
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8)

    # Draw bounding boxes
    face_count = len(faces)
    for (x, y, w, h) in faces:
        # Draw a green rectangle around the face
        cv2.rectangle(image_data, (x, y), (x + w, y + h), (0, 255, 0), 2)

    end_time = time.time()
    duration = end_time - start_time
    
    return image_data, face_count, duration

# --- Parallel Processing Logic (Adapted for Streamlit) ---

def process_single_image_parallel(image_path):
    """Wrapper for parallel processing of a file path."""
    img = cv2.imread(image_path)
    if img is None:
        return 0, 0.0 # Return 0 faces and 0 duration on failure
    
    # Convert BGR to RGB for Streamlit display later (optional, but good practice)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    processed_img, face_count, duration = detect_faces_on_image(img_rgb, mode="parallel")
    
    # Save the processed image for comparison (optional, but keeps the original project structure)
    output_filename = os.path.basename(image_path).replace(".", "_parallel.")
    output_path = os.path.join(OUTPUT_DIR_PAR, output_filename)
    cv2.imwrite(output_path, cv2.cvtColor(processed_img, cv2.COLOR_RGB2BGR))
    
    return face_count, duration

def run_parallel_detection(image_paths):
    """Runs parallel face detection on a list of image paths."""
    st.subheader("Parallel Processing Results")
    
    num_processes = cpu_count()
    st.info(f"Using {num_processes} processes for parallel execution.")
    
    total_start_time = time.time()
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_single_image_parallel, image_paths)
        
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    total_faces = sum(r[0] for r in results)
    
    st.success(f"Total images processed: {len(image_paths)}")
    st.success(f"Total faces found: {total_faces}")
    st.success(f"Total time taken: {total_duration:.4f} seconds")
    
    return total_duration

# --- Streamlit GUI Functions ---

def static_image_detection():
    st.header("Static Image Detection (Sequential)")
    
    # Option 1: Upload Image
    uploaded_file = st.file_uploader("Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    # Option 2: URL Retrieval
    st.markdown("---")
    url = st.text_input("Or paste an image URL here:")
    
    image_to_process = None
    
    if uploaded_file is not None:
        # Read file as bytes and convert to numpy array
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image_to_process = cv2.imdecode(file_bytes, 1)
        image_to_process = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2RGB)
        
    elif url:
        try:
            with urllib.request.urlopen(url) as response:
                image_data = response.read()
            
            # Convert bytes to numpy array
            file_bytes = np.asarray(bytearray(image_data), dtype=np.uint8)
            image_to_process = cv2.imdecode(file_bytes, 1)
            image_to_process = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2RGB)
            
        except Exception as e:
            st.error(f"Could not retrieve image from URL: {e}")
            
    if image_to_process is not None:
        st.image(image_to_process, caption="Original Image", use_column_width=True)
        
        if st.button("Run Face Detection"):
            with st.spinner("Detecting faces..."):
                processed_img, face_count, duration = detect_faces_on_image(image_to_process.copy(), mode="sequential")
            
            st.subheader("Detection Result")
            st.image(processed_img, caption=f"Detected {face_count} faces in {duration:.4f} seconds.", use_column_width=True)
            st.success(f"Found {face_count} faces in {duration:.4f} seconds.")

def webcam_detection():
    st.header("Live Webcam Detection")
    st.warning("Webcam functionality requires Streamlit to be run locally and may not work in all cloud environments.")
    
    # The Streamlit component for webcam capture is st.camera_input
    # However, for a continuous live feed with real-time processing, a dedicated component or external library is often needed.
    # For simplicity and reliability in a sandboxed environment, we will use a static capture method.
    
    st.info("To simulate live detection, please capture a photo using the button below.")
    
    camera_image = st.camera_input("Take a picture for face detection")
    
    if camera_image:
        # Convert image to numpy array
        file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        with st.spinner("Detecting faces in live capture..."):
            processed_img, face_count, duration = detect_faces_on_image(img_rgb.copy(), mode="sequential")
            
        st.subheader("Detection Result")
        st.image(processed_img, caption=f"Detected {face_count} faces in {duration:.4f} seconds.", use_column_width=True)
        st.success(f"Found {face_count} faces in {duration:.4f} seconds.")

def main_gui():
    st.set_page_config(page_title="PDC Face Recognition App", layout="wide")
    
    st.title("Face Recognition for Parallel Computing Course")
    st.markdown("Demonstrating Sequential and Parallel Processing with OpenCV Face Detection.")
    
    menu = ["Static Image Detection", "Webcam Detection", "Parallel Batch Test"]
    choice = st.sidebar.selectbox("Select Mode", menu)
    
    if choice == "Static Image Detection":
        static_image_detection()
    elif choice == "Webcam Detection":
        webcam_detection()
    elif choice == "Parallel Batch Test":
        st.header("Parallel Batch Test (Sequential vs. Parallel)")
        st.info("This mode runs the original batch test to compare performance. Please ensure the 'images/' folder contains your test images.")
        
        # Get all image files from the input directory
        INPUT_DIR = "images"
        image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        image_paths = [os.path.join(INPUT_DIR, f) for f in image_files]
        
        if not image_paths:
            st.error(f"No images found in the '{INPUT_DIR}' directory. Please add some images to test.")
            return
        
        if st.button("Run Batch Performance Test"):
            # Run Sequential Baseline
            st.subheader("Sequential Processing Results")
            seq_start_time = time.time()
            seq_faces = 0
            for path in image_paths:
                img = cv2.imread(path)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                _, face_count, duration = detect_faces_on_image(img_rgb.copy(), mode="sequential")
                seq_faces += face_count
                st.text(f"Sequential processing of {os.path.basename(path)}: {face_count} faces found in {duration:.4f} seconds.")
            seq_time = time.time() - seq_start_time
            st.success(f"Sequential Total Time: {seq_time:.4f} seconds. Total Faces: {seq_faces}")
            
            # Run Parallel Implementation
            par_time = run_parallel_detection(image_paths)
            
            # Compare Results
            st.subheader("Performance Comparison")
            st.markdown(f"**Sequential Time:** `{seq_time:.4f} seconds`")
            st.markdown(f"**Parallel Time:** `{par_time:.4f} seconds`")
            
            if par_time < seq_time:
                speedup_par = seq_time / par_time
                st.markdown(f"**Parallel Speedup:** `{speedup_par:.2f}x` (Parallel is faster)")
            else:
                st.markdown("**Parallel Speedup:** No speedup observed (Overhead exceeded benefit).")

if __name__ == "__main__":
    main_gui()
