# Face Recognition for Parallel Computing (PDC) Course - GUI Version

This project include a professional Graphical User Interface (GUI) using **Streamlit**, making it easier to demonstrate and test the face detection and parallel computing concepts.

## 🚀 Features

*   **GUI Interface**: A web-based application for easy interaction.
*   **Static Image Detection**: Upload an image, drag-and-drop, or paste a URL to detect faces.
*   **Webcam Detection**: Use your local webcam to detect faces in real-time (or near real-time capture).
*   **Parallel Batch Test**: Run the original Sequential vs. Parallel performance comparison directly from the GUI.
*   **Bug Fixes**: The face detection logic has been tuned to significantly reduce false positives (over-detection).

## 🛠️ Setup (VS Code Friendly)

### Prerequisites

You need **Python 3.8+** installed on your system.

### 1. Clone the Repository

```bash
git clone [REPLACE_WITH_REPO_URL]
cd FaceRecognition_PDC
```
*(Note: Since this is a local sandbox, you will skip this step and just work in the directory.)*

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate
```

### 3. Install Dependencies

The project now requires `streamlit` in addition to the core libraries.

```bash
pip install -r requirements.txt
```

### 4. Add Test Images (For Batch Test)

Place your test images (JPEG or PNG) into the `images/` directory if you plan to run the "Parallel Batch Test" option in the GUI.

## 🏃 How to Run (The New Way)

The `main.py` file is now a simple launcher for the Streamlit application.

1.  **Run the application:**
    ```bash
    python main.py
    ```
2.  **Access the GUI:**
    The command will print a local URL (e.g., `http://localhost:8501`). Open this URL in your web browser to access the application.

## 📂 Project Structure

```
FaceRecognition_PDC/
├── images/                     # Input images for the Batch Test
├── output_sequential/          # Output images from sequential run (Batch Test)
├── output_parallel/            # Output images from parallel run (Batch Test)
├── main.py                     # Launcher for the Streamlit GUI
├── streamlit_app.py            # The core GUI logic and face detection functions
├── requirements.txt            # Python dependencies (now includes Streamlit)
├── haarcascade_frontalface_default.xml # OpenCV's pre-trained face detection model
└── README.md                   # This file
```

## 💡 Key Concepts for PDC Course

The project still clearly demonstrates:
*   **Sequential vs. Parallel**: The performance comparison is available in the "Parallel Batch Test" section of the GUI.
*   **Task Parallelism**: Using `multiprocessing.Pool` to speed up the image processing workload.
*   **Tuning**: The fix for over-detection (`minNeighbors=8`) shows the importance of parameter tuning in computer vision.
