import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# ---------------- GEMINI ----------------
async def test_gemini_connection():
    """Test if Gemini API is working"""
    print("🔍 Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("What is the capital of India?")

        print(f"✅ Gemini API test successful: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False


# ---------------- LIVEKIT ----------------
async def test_livekit_connection():
    """Test if LiveKit credentials are valid"""
    print("🔍 Testing LiveKit credentials...")
    try:
        from livekit import AccessToken
        from livekit.models import VideoGrant

        token = api.AccessToken(
            os.getenv("LIVEKIT_API_KEY"),
            os.getenv("LIVEKIT_API_SECRET"),
        )
        grant = api.VideoGrant(room_join=True, room="test-room")
        token.add_grant(grant)

        # ✅ identity is passed here now
        test_token = token.to_jwt(identity="test-user")
        if test_token:
            print("✅ LiveKit credentials test successful")
            return True
        else:
            print("❌ LiveKit credentials test failed: Could not generate token")
            return False
    except Exception as e:
        print(f"❌ LiveKit credentials test failed: {e}")
        return False


# ---------------- DEEPGRAM ----------------
async def test_deepgram_connection():
    """Test if Deepgram API is working"""
    print("🔍 Testing Deepgram API connection...")
    try:
        import requests

        response = requests.get(
            "https://api.deepgram.com/v1/projects",
            headers={"Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}"},
        )

        if response.status_code == 200:
            print("✅ Deepgram API test successful")
            return True
        else:
            print(f"❌ Deepgram API test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Deepgram API test failed: {e}")
        return False


# ---------------- ELEVENLABS ----------------
async def test_elevenlabs_connection():
    """Test if ElevenLabs API is working"""
    print("🔍 Testing ElevenLabs API connection...")
    try:
        import requests

        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")},
        )

        if response.status_code == 200:
            print("✅ ElevenLabs API test successful")
            return True
        else:
            print(f"❌ ElevenLabs API test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ElevenLabs API test failed: {e}")
        return False


# ---------------- COMPLAINT SYSTEM ----------------
async def test_complaint_system():
    """Test the complaint generation system"""
    print("🔍 Testing complaint system...")
    try:
        from municipal_agent import MunicipalAssistant

        assistant = MunicipalAssistant()
        complaint_id = assistant.submit_complaint(
            "Water Supply", "No water for 3 days", "Sector 15, Gandhinagar"
        )

        print(f"✅ Complaint system test successful: Generated ID {complaint_id}")

        complaint = assistant.complaints.get(complaint_id)
        if complaint:
            print(
                f"   Complaint details: {complaint['type']} - {complaint['description']}"
            )
        return True
    except Exception as e:
        print(f"❌ Complaint system test failed: {e}")
        return False


# ---------------- AGENT INITIALIZATION ----------------
async def test_agent_initialization():
    """Test if the agent can initialize properly"""
    print("🔍 Testing agent initialization...")
    try:
        from municipal_agent import MunicipalAssistant, GeminiLLM
        from livekit.plugins import deepgram, elevenlabs
        from livekit_plugins import silero  # ✅ correct silero import

        # Test component initialization
        assistant = MunicipalAssistant()
        llm = GeminiLLM()
        stt = deepgram.STT()
        tts = elevenlabs.TTS()
        vad_model = silero.VAD.load()  # ✅ correct usage

        print("✅ Agent initialization test successful")
        return True
    except Exception as e:
        print(f"❌ Agent initialization test failed: {e}")
        return False


# ---------------- MAIN ----------------
async def main():
    """Run all tests"""
    print("🧪 Starting comprehensive tests for Municipal Voice AI Assistant...")
    print("=" * 60)

    tests = [
        test_gemini_connection(),
        test_livekit_connection(),
        test_deepgram_connection(),
        test_elevenlabs_connection(),
        test_complaint_system(),
        test_agent_initialization(),
    ]

    results = await asyncio.gather(*tests)

    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All {total} tests passed! The system is ready for use.")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please check the failed tests.")

    if not all(results):
        print("\n🔧 Troubleshooting tips:")
        if not results[0]:
            print("  - Check your GEMINI_API_KEY in the .env file")
            print("  - Ensure you have a valid Gemini API key from https://aistudio.google.com/app/apikey")
        if not results[1]:
            print("  - Check your LIVEKIT_API_KEY and LIVEKIT_API_SECRET in the .env file")
            print("  - Get these from https://cloud.livekit.io/")
        if not results[2]:
            print("  - Check your DEEPGRAM_API_KEY in the .env file")
            print("  - Get a key from https://console.deepgram.com/signup")
        if not results[3]:
            print("  - Check your ELEVENLABS_API_KEY in the .env file")
            print("  - Get a key from https://elevenlabs.io/app")

    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
