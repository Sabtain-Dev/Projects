# License Plate Detection System (ANPR-App)

This project is an Automatic Number Plate Recognition (ANPR) application built using **Python**, **OpenCV**, **Matplotlib**, and **Tkinter**.  
It provides a graphical user interface to upload an image, process it, detect contours, extract license plate candidates, and visualize the final results.

---

## 🚀 Features
- Image upload through GUI  
- Preprocessing (grayscale, bilateral filtering, histogram equalization, CLAHE)  
- Edge detection (Sobel + Canny + morphological enhancements)  
- Contour detection with filtering techniques  
- Perspective transform for plate extraction  
- Visualization of all processing stages in one interface  
- Highlights the best candidate plate region  

---

## 📦 Installation

### **1. Create a virtual environment (recommended)**  
```
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate    # Windows
```

### **2. Install required dependencies**
```
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the application using:

```
python ANPR-App.py
```

A GUI window will open:

1. Click **Upload Image** to load any `.jpg`, `.png`, `.bmp`, `.tiff` image.  
2. Click **Detect Plate** to start the license plate detection pipeline.  
3. The system will show:
   - Original image  
   - Preprocessed image  
   - Edge map  
   - Contours  
   - Extracted best plate region  
   - Final detection result  

---

## 📁 Project Structure
```
ANPR-App.py
requirements.txt
README.md
```

---

## 🔧 Dependencies
- Python 3.x  
- OpenCV  
- NumPy  
- Matplotlib  
- Imutils  
- Pillow  
- Tkinter  

---

## 📝 Notes
- Works best on vehicle images with clearly visible license plates.  
- You can customize thresholds, filters, or detection parameters inside the script.  

---

## 👨‍💻 Author
**M. Sabtain Khan**  
DIP Project — License Plate Detection System  
