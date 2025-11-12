import streamlit as st
import os
import shutil
import stat
import datetime
import zipfile
import platform
import psutil

# ------------------ Setup ------------------
st.set_page_config(
    page_title="File Manager",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Widen the sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        width: 360px;  /* Adjust width if needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)

HISTORY_FILE = "history.txt"

# ------------------ Utility Functions ------------------
def log_action(action):
    """Save user actions to history file"""
    with open(HISTORY_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {action}\n")

def list_directory(directory_name):
    try:
        entries = os.listdir(directory_name)
        st.success(f"📂 Contents of directory: {directory_name}")
        for entry in entries:
            st.write(" - ", entry)
        log_action(f"Listed directory: {directory_name}")
        return entries
    except OSError as e:
        st.error(f"Error: {e}")

def show_file_properties(filename):
    try:
        file_stat = os.stat(filename)
        props = {
            "Size": f"{file_stat.st_size} bytes",
            "Permissions": f"{'r' if file_stat.st_mode & stat.S_IRUSR else '-'}"
                           f"{'w' if file_stat.st_mode & stat.S_IWUSR else '-'}"
                           f"{'x' if file_stat.st_mode & stat.S_IXUSR else '-'}",
            "Last Modified": str(datetime.datetime.fromtimestamp(file_stat.st_mtime))
        }
        st.json(props)
        log_action(f"Viewed properties of {filename}")
    except OSError as e:
        st.error(f"Error: {e}")

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        st.success(f"✅ Directory created: {path}")
        log_action(f"Created directory: {path}")
    except OSError as e:
        st.error(f"Error: {e}")

def create_file(path):
    try:
        with open(path, 'w') as file:
            st.success(f"📝 File created: {path}")
        log_action(f"Created file: {path}")
    except OSError as e:
        st.error(f"Error: {e}")

def delete_file(filename):
    try:
        os.remove(filename)
        st.warning(f"🗑️ File deleted: {filename}")
        log_action(f"Deleted file: {filename}")
    except OSError as e:
        st.error(f"Error: {e}")

def delete_directory(directory_name):
    try:
        shutil.rmtree(directory_name)
        st.warning(f"🗑️ Directory deleted: {directory_name}")
        log_action(f"Deleted directory: {directory_name}")
    except OSError as e:
        st.error(f"Error: {e}")

def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        st.success(f"📄 Copied {src} → {dest}")
        log_action(f"Copied file from {src} to {dest}")
    except Exception as e:
        st.error(f"Error: {e}")

def move_file(src, dest):
    try:
        shutil.move(src, dest)
        st.success(f"📁 Moved {src} → {dest}")
        log_action(f"Moved file from {src} to {dest}")
    except Exception as e:
        st.error(f"Error: {e}")

def compress_files(filenames, archive_name):
    try:
        with zipfile.ZipFile(archive_name + '.zip', 'w') as zipf:
            for filename in filenames:
                zipf.write(filename, os.path.basename(filename))
        st.success(f"🗜️ Files compressed into {archive_name}.zip")
        log_action(f"Compressed {filenames} into {archive_name}.zip")
    except Exception as e:
        st.error(f"Error: {e}")

def extract_files(archive_name, destination):
    try:
        shutil.unpack_archive(archive_name, destination)
        st.success(f"📦 Extracted {archive_name} → {destination}")
        log_action(f"Extracted archive: {archive_name} to {destination}")
    except Exception as e:
        st.error(f"Error: {e}")

# ------------------ Sidebar UI ------------------
st.sidebar.title("🗂️ File System Explorer")
st.sidebar.markdown("---")

# 🧭 Operations Section
st.sidebar.subheader("🧭 Choose an Operation")
option = st.sidebar.selectbox(
    "Select an Action:",
    [
        "List Directory",
        "Show File Properties",
        "Create Directory",
        "Create File",
        "Delete Directory",
        "Delete File",
        "Copy File",
        "Move File",
        "Compress Files",
        "Extract Files",
        "View Action History"
    ]
)

# 💻 System Info
st.sidebar.subheader("💻 System Information")

current_dir = os.getcwd()
total_files = sum(len(files) for _, _, files in os.walk(current_dir))
total_dirs = sum(len(dirs) for _, dirs, _ in os.walk(current_dir))
disk = psutil.disk_usage(current_dir)

# System info values
cpu_percent = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory()
ram_percent = ram.percent
ram_used = ram.used // (1024 ** 3)
ram_total = ram.total // (1024 ** 3)

# Sidebar display
st.sidebar.write(f"📂 **Current Dir:** {current_dir}")
st.sidebar.write(f"📁 **Folders:** {total_dirs}")
st.sidebar.write(f"📄 **Files:** {total_files}")
st.sidebar.write(f"🧠 **OS:** {platform.system()} {platform.release()}")
st.sidebar.write(f"⚙️ **Python:** {platform.python_version()}")
st.sidebar.write(f"🧩 **CPU Usage:** {cpu_percent}%")
st.sidebar.progress(int(cpu_percent))
st.sidebar.write(f"💾 **Disk Usage:** {disk.percent}% used ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)")
st.sidebar.progress(int(disk.percent))
st.sidebar.write(f"🧠 **RAM Usage:** {ram_percent}% ({ram_used} GB / {ram_total} GB)")
st.sidebar.progress(int(ram_percent))

# Optional GPU info (if available)
try:
    import GPUtil
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        st.sidebar.write(f"🎮 **GPU:** {gpu.name} ({gpu.load * 100:.1f}% load)")
        st.sidebar.progress(int(gpu.load * 100))
except Exception:
    st.sidebar.write("🎮 **GPU:** Not detected")

st.sidebar.markdown("---")

# 🚪 Exit Button
if st.sidebar.button("🚪 Exit Application"):
    st.stop()

# ------------------ Main UI ------------------
st.title("🧮 File Manager Dashboard")

# Dynamic Quick Tips dictionary
quick_tips = {
    "List Directory": "💡 Tip: Enter a valid directory path like C:\\Users\\Username\\Documents",
    "Show File Properties": "💡 Tip: Enter a file path like C:\\Users\\Username\\Documents\\file.txt",
    "Create Directory": "💡 Tip: Enter a path to create a directory like C:\\My_Files\\NewFolder",
    "Create File": "💡 Tip: Enter full path including file name like C:\\My_Files\\Files.py",
    "Delete Directory": "💡 Tip: Enter directory path to delete, e.g., C:\\My_Files\\OldFolder",
    "Delete File": "💡 Tip: Enter file path to delete, e.g., C:\\My_Files\\Files.py",
    "Copy File": "💡 Tip: Enter source file path and destination folder, e.g., C:\\My_Files\\file.txt → D:\\Backup",
    "Move File": "💡 Tip: Enter source file path and destination folder, e.g., C:\\My_Files\\file.txt → D:\\Backup",
    "Compress Files": "💡 Tip: Enter space-separated file paths and archive name, e.g., file1.txt file2.txt → archive_name",
    "Extract Files": "💡 Tip: Enter zip file name and destination folder, e.g., archive.zip → C:\\Extracted",
    "View Action History": "💡 Tip: View all actions logged in history.txt"
}

# Show relevant quick tip in main interface
if option in quick_tips:
    st.info(quick_tips[option])

# ------------------ Operations ------------------
if option == "List Directory":
    path = st.text_input("Enter directory path:")
    if st.button("List Files"):
        if path:
            files = list_directory(path)
            if files:
                st.info("💡 You can compress or move these files!")

elif option == "Show File Properties":
    file = st.text_input("Enter file path:")
    if st.button("Show Properties"):
        show_file_properties(file)

elif option == "Create Directory":
    path = st.text_input("Enter new directory path:")
    if st.button("Create"):
        create_directory(path)

elif option == "Create File":
    path = st.text_input("Enter file path:")
    if st.button("Create"):
        create_file(path)

elif option == "Delete Directory":
    path = st.text_input("Enter directory path to delete:")
    if st.button("Delete"):
        delete_directory(path)

elif option == "Delete File":
    path = st.text_input("Enter file path to delete:")
    if st.button("Delete"):
        delete_file(path)

elif option == "Copy File":
    src = st.text_input("Enter source file:")
    dest = st.text_input("Enter destination folder:")
    if st.button("Copy"):
        copy_file(src, dest)

elif option == "Move File":
    src = st.text_input("Enter source file:")
    dest = st.text_input("Enter destination folder:")
    if st.button("Move"):
        move_file(src, dest)

elif option == "Compress Files":
    files = st.text_input("Enter file names (space-separated):").split()
    archive = st.text_input("Enter archive name (without .zip):")
    if st.button("Compress"):
        compress_files(files, archive)

elif option == "Extract Files":
    archive = st.text_input("Enter archive name (.zip):")
    dest = st.text_input("Enter destination folder:")
    if st.button("Extract"):
        extract_files(archive, dest)

elif option == "View Action History":
    st.subheader("📜 Action History")
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            st.text(f.read())
    else:
        st.info("No history found yet.")
