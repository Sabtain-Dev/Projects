# 🗂️ Streamlit File Manager Dashboard

A modern, interactive **File Manager Dashboard** built using **Streamlit**, providing real time system information and file operations like creating, deleting, moving, compressing, and extracting files all through a simple web interface.

---

## 🚀 Features

- 📂 Browse and list directories  
- 📝 Create, delete, copy, and move files or folders  
- 🗜️ Compress and extract `.zip` archives  
- 💻 View detailed system information:
  - OS and Python version  
  - CPU usage  
  - RAM and Disk usage  
  - GPU load (if available)
- 📜 View all user actions logged in `history.txt`
- ⚡ Quick tips displayed dynamically for every operation
- 🧭 Fully interactive sidebar interface

---

## 🧰 Installation & Setup

### 1. Clone the repository
```bash
    git clone https://github.com/your-username/streamlit-file-manager.git
    cd streamlit-file-manager

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run the app
- streamlit run file_manager.py
- python -m streamlit run file_manager.py

## 🧠 Usage Guide
1. When the app opens in your browser:
2. Select an operation from the sidebar (e.g., Create File, List Directory).
3. Enter a valid file or directory path.
4. Follow the on-screen quick tips.
5. Check system information (CPU, RAM, Disk) in the sidebar.
6. All actions will be saved in history.txt automatically.

streamlit-file-manager/
│
├── For Linux OS          # Streamlit App For Linux OS
├── file_manager.py       # Main Streamlit app For Windows
├── history.txt           # Action log file
├── requirements.txt      # Dependencies
├── README.md             # Project description
└── .gitignore            # Git ignore rules

## 🧠 Tech Stack
1. Frontend/UI: Streamlit
2. Backend Logic: Python Standard Library
3. System Info: psutil, GPUtil

## 💡 Author

Developed by: M. Sabtain Khan
