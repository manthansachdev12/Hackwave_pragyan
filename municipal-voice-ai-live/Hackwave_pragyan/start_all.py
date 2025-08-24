import subprocess
import time
import threading
import webbrowser
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def run_command(command, description, wait=True):
    """Run a command and print its output"""
    print(f"🚀 Starting {description}...")
    try:
        if wait:
            result = subprocess.run(command, shell=True, check=True)
            return result.returncode == 0
        else:
            # For processes that need to run in the background
            subprocess.Popen(command, shell=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start {description}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting {description}: {e}")
        return False

def start_token_server():
    """Start the token server"""
    return run_command("python token_server.py", "token server", wait=False)

def start_agent():
    """Start the voice agent"""
    time.sleep(2)  # Wait for token server to start
    return run_command("python run_agent.py", "voice agent", wait=False)

def start_web_interface():
    """Start the web interface"""
    time.sleep(3)  # Wait for other services to start
    return run_command("streamlit run app.py", "web interface", wait=False)

def open_browser():
    """Open the web interface in browser"""
    time.sleep(5)  # Wait for web interface to start
    webbrowser.open("http://localhost:8501")
    print("🌐 Opening web interface in browser...")

def main():
    """Start all services"""
    print("🏛️ Municipal Voice AI Assistant - Starting All Services")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ No .env file found. Please create one with your API keys.")
        print("   Use the .env.example file as a template.")
        return
    
    # Start services in sequence
    services = [
        ("Token Server", start_token_server),
        ("Voice Agent", start_agent),
        ("Web Interface", start_web_interface)
    ]
    
    for service_name, service_func in services:
        if not service_func():
            print(f"❌ Failed to start {service_name}. Exiting.")
            return
    
    # Open browser after a delay
    threading.Timer(6.0, open_browser).start()
    
    print("=" * 50)
    print("✅ All services started successfully!")
    print("📞 Voice Agent: Ready for incoming calls")
    print("🌐 Web Interface: http://localhost:8501")
    print("🔑 Token Server: http://localhost:5000")
    print("\n Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")

if __name__ == "__main__":
    main()