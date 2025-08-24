import subprocess
import time
import webbrowser
from threading import Thread

def start_token_server():
    """Start the Flask token server"""
    print("Starting token server...")
    subprocess.run(["python", "token_server.py"])

def start_streamlit_app():
    """Start the Streamlit web app"""
    print("Starting Streamlit app...")
    time.sleep(2)  # Wait for token server to start
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    print("🚀 Starting Municipal Voice AI Services...")
    
    # Start token server in a separate thread
    token_thread = Thread(target=start_token_server)
    token_thread.daemon = True
    token_thread.start()
    
    # Wait a moment, then start Streamlit
    time.sleep(1)
    streamlit_thread = Thread(target=start_streamlit_app)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Open the web interface in browser
    time.sleep(3)
    webbrowser.open("http://localhost:8501")
    
    print("✅ Services started! Open http://localhost:8501 in your browser")
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")