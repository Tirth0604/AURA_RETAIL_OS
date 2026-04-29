import os
import sys
import subprocess
import time
import webbrowser

def launch():
    # 1. Start the FastAPI server in the background
    print("Starting AURA RETAIL OS Web Server...")
    # Use the same python executable as current
    python_exe = sys.executable
    server_script = "web_app.py"
    
    # Run the server
    process = subprocess.Popen([python_exe, server_script])
    
    # 2. Wait for server to start
    print("Waiting for server to initialize...")
    time.sleep(3)
    
    # 3. Open Chrome
    url = "http://localhost:8000"
    print(f"Launching {url} in Google Chrome...")
    
    # Common Chrome paths on Windows
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            subprocess.Popen([path, url])
            chrome_found = True
            break
            
    if not chrome_found:
        print("Chrome not found in standard paths. Falling back to default browser.")
        webbrowser.open(url)
        
    print("\nProject is now running in Chrome!")
    print("Keep this terminal open to keep the server alive.")
    print("Press Ctrl+C to stop the server.")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping server...")
        process.terminate()

if __name__ == "__main__":
    launch()
