import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def run_agent():
    """Run the municipal agent"""
    print("🚀 Starting Municipal Voice AI Agent...")
    
    # Check if required environment variables are set
    required_vars = [
        'GEMINI_API_KEY',
        'LIVEKIT_URL', 
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET',
        'DEEPGRAM_API_KEY',
        'ELEVENLABS_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file")
        return
    
    print("✅ All required environment variables are set")
    print(f"🔗 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    
    try:
        from municipal_agent import entrypoint
        from livekit.agents import WorkerOptions, cli
        
        # Run the agent in development mode
        print("📞 Agent is running. Press Ctrl+C to stop.")
        print("   You can now connect clients to room: municipal-support")
        
        # This will run until interrupted
        cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
        
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_agent())