import os
import subprocess

# --- Configuration ---
APP_FILE = "streamlit_app.py"

def main():
    """Launches the Streamlit GUI application."""
    print(f"Launching Streamlit application: {APP_FILE}")
    print("Please open the provided URL in your browser to access the GUI.")
    
    # Use subprocess to run the streamlit command
    try:
        # The command to run Streamlit
        command = ["streamlit", "run", APP_FILE, "--server.port", "8501", "--server.headless", "true"]
        
        # Start the process
        process = subprocess.Popen(command, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Keep the main script running to keep the Streamlit process alive
        process.wait()
        
    except FileNotFoundError:
        print("\nERROR: Streamlit command not found.")
        print("Please ensure Streamlit is installed: pip install streamlit")
    except KeyboardInterrupt:
        print("\nStreamlit application stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred while running Streamlit: {e}")

if __name__ == "__main__":
    main()
