import os
import asyncio
import logging
from typing import Dict, Any
from dotenv import load_dotenv
# Make sure you have the correct import
from livekit.plugins import deepgram, elevenlabs, silero  

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("municipal-agent")

# Load environment variables
load_dotenv()

# Import LiveKit components
from livekit.agents import Agent, JobContext, WorkerOptions, cli
from livekit.agents import llm
from livekit.plugins import deepgram, elevenlabs, silero

# Import Gemini
import google.generativeai as genai
# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise


class GeminiLLM(llm.LLM):
    def __init__(self, model_name="gemini-pro"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.chat_sessions = {}  # Store chat sessions by session ID
        
    async def chat(self, messages: list[llm.ChatMessage], **kwargs) -> llm.ChatContext:
        try:
            # Convert LiveKit messages to Gemini format
            gemini_messages = []
            
            for msg in messages:
                role = "user" if msg.role == llm.ChatRole.USER else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
            
            # Use the last message ID as session key (simplified approach)
            session_key = str(id(messages))
            
            # Start new chat session or continue existing one
            if session_key not in self.chat_sessions:
                self.chat_sessions[session_key] = self.model.start_chat(history=gemini_messages[:-1])
            
            chat_session = self.chat_sessions[session_key]
            
            # Generate response using the last user message
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: chat_session.send_message(
                    messages[-1].content,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=150,  # Keep responses concise for voice
                    )
                )
            )
            
            # Create response context
            class GeminiContext(llm.ChatContext):
                async def message(self) -> llm.ChatMessage:
                    return llm.ChatMessage(
                        role=llm.ChatRole.ASSISTANT,
                        content=response.text
                    )
                    
                async def stream(self):
                    # For voice interactions, we typically want the full response
                    yield llm.ChatMessage(
                        role=llm.ChatRole.ASSISTANT,
                        content=response.text
                    )
            
            return GeminiContext()
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            # Return a fallback response
            class FallbackContext(llm.ChatContext):
                async def message(self) -> llm.ChatMessage:
                    return llm.ChatMessage(
                        role=llm.ChatRole.ASSISTANT,
                        content="I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
                    )
                    
                async def stream(self):
                    yield llm.ChatMessage(
                        role=llm.ChatRole.ASSISTANT,
                        content="I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
                    )
            
            return FallbackContext()


class MunicipalAssistant:
    def __init__(self):
        self.complaints: Dict[str, Dict[str, Any]] = {}
        self.complaint_counter = 1
        self.service_codes = {
            "property tax": "PT",
            "water supply": "WS", 
            "waste management": "WM",
            "street light": "SL",
            "certificates": "CI",
            "road issues": "RI",
            "garbage collection": "GC",
            "drainage": "DR"
        }
    
    def generate_complaint_id(self, service_type: str) -> str:
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Get service code or use first two letters
        service_code = self.service_codes.get(service_type.lower(), service_type[:2].upper())
        
        complaint_id = f"{service_code}{date_str}-{self.complaint_counter:04d}"
        self.complaint_counter += 1
        return complaint_id
    
    def submit_complaint(self, service_type: str, description: str, location: str) -> str:
        complaint_id = self.generate_complaint_id(service_type)
        self.complaints[complaint_id] = {
            'type': service_type,
            'description': description,
            'location': location,
            'status': 'submitted',
            'timestamp': asyncio.get_event_loop().time()
        }
        logger.info(f"New complaint submitted: {complaint_id}")
        return complaint_id
    
    def get_complaint_status(self, complaint_id: str) -> Dict[str, Any]:
        return self.complaints.get(complaint_id, {"error": "Complaint ID not found"})
    
    def get_all_complaints(self) -> Dict[str, Dict[str, Any]]:
        return self.complaints

# Create global instance
municipal_assistant = MunicipalAssistant()



async def entrypoint(ctx: JobContext):
    logger.info("Municipal agent starting up...")
    await ctx.connect()
    
    # Set up the AI agent with detailed instructions for municipal services
    agent = Agent(
        name="Municipal Assistant",
        instructions="""You are a helpful Municipal Corporation voice assistant for Indian citizens.
        You help citizens with various municipal services in a friendly, patient manner.

        SERVICES YOU PROVIDE:
        - Property tax inquiries and payments (PT)
        - Water supply complaints and connections (WS)
        - Garbage collection issues (GC)
        - Streetlight repair requests (SL)
        - Birth/death certificate applications (CI)
        - Road and drainage issues (RI/DR)
        - Waste management complaints (WM)

        WHEN CITIZENS REPORT ISSUES:
        1. Politely ask for details about the problem and exact location
        2. Generate a complaint ID using the format: [ServiceCode][Date]-[Number]
        3. Provide the complaint ID and estimated resolution time (24-48 hours for most issues)
        4. Offer relevant department contact information if needed

        COMMUNICATION GUIDELINES:
        - Respond in the same language the user speaks (Hindi or English)
        - Keep responses concise for voice interaction (1-2 sentences maximum)
        - Be warm, patient, and helpful
        - Speak clearly and at a moderate pace
        - For urgent issues, advise calling emergency numbers

        EMERGENCY NUMBERS TO MENTION IF NEEDED:
        - Fire: 101
        - Police: 100
        - Ambulance: 102
        - Municipal Emergency: 1800-123-MUNI

        Remember: You are the first point of contact for citizens seeking help with municipal services."""
    )
    
    # Configure voice processing components
    try:
        # Voice Activity Detection
        vad = silero.VAD.load()
        logger.info("VAD loaded successfully")
        
        # Speech-to-Text (supports Hindi and English)
        stt = deepgram.STT(
            model="nova-2-general",
            language="hi,en",  # Hindi and English
            smart_format=True,
            interim_results=True
        )
        logger.info("Speech-to-Text configured")
        
        # Text-to-Speech (multilingual support)
        tts = elevenlabs.TTS(
            voice="Sarah",
            model="eleven_multilingual_v2",
            stability=0.5,
            similarity_boost=0.8
        )
        logger.info("Text-to-Speech configured")
        
        # Language Model (Gemini)
        llm_model = GeminiLLM(model_name="gemini-pro")
        logger.info("Gemini LLM configured")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    # Create and configure session
    session = ctx.create_session(
        vad=vad,
        stt=stt,
        llm=llm_model,
        tts=tts
    )
    
    # Start the agent session
    logger.info("Starting agent session...")
    await session.start(agent=agent)
    logger.info("Agent session started successfully")

if __name__ == "__main__":
    # Test Gemini connection on startup
    try:
        test_model = genai.GenerativeModel('gemini-pro')
        test_response = test_model.generate_content("Test connection")
        logger.info(f"Gemini test successful: {test_response.text[:50]}...")
    except Exception as e:
        logger.error(f"Gemini test failed: {e}")
    
    # Run the agent
    cli.run_app(WorkerOptions(entrypoint))
