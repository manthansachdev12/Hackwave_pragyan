#!/usr/bin/env python3
"""
Test script to verify Gemini 2.0 Flash API connection and basic functionality
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    print("Testing Gemini 2.0 Flash API connection...")
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Use the stable alias for Gemini 2.0 Flash
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        response = model.generate_content("What is the capital of India?")
        print("✅ Gemini API test successful!")
        print(f"Response: {response.text}")
        
        municipal_response = model.generate_content(
            "A citizen reports no water supply for 2 days in Sector 15. "
            "Respond helpfully as a municipal assistant in one short sentence."
        )
        print(f"Municipal test response: {municipal_response.text}")
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_gemini()
