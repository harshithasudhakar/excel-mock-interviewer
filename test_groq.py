#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

def test_groq_connection():
    api_key = os.getenv("GROQ_API_KEY", "")
    
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in environment variables")
        return False
    
    print(f"SUCCESS: API Key found: {api_key[:10]}...")
    
    try:
        client = Groq(api_key=api_key)
        
        # Test simple completion with available model
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Current supported model
            messages=[{"role": "user", "content": "Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}"}],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        print(f"SUCCESS: Groq API Response: {content}")
        
        # Test Excel question generation
        prompt = """Generate a beginner-level Excel interview question about basic formulas.

Return only a JSON object with this format:
{
    "question": "the interview question",
    "expected_answer": "brief expected answer or approach"
}

Make it practical and scenario-based."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Current supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print(f"SUCCESS: Excel Question Generation: {content}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Groq API Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Groq API Connection...")
    test_groq_connection()