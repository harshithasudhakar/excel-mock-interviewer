#!/usr/bin/env python3
"""Quick LLM test to verify Groq API is working"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq_api():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found in environment")
        return False
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    
    try:
        client = Groq(api_key=api_key)
        
        # Test basic question generation
        prompt = """You are a friendly Excel interviewer. Generate a beginner level Excel question.

Start with: "Let's start with something practical..."

Example beginner questions:
- How would you calculate the sum of values in cells A1 through A10?
- What's the difference between relative and absolute cell references?

Generate a conversational, scenario-based Excel question that tests beginner skills.
Focus on: formulas and basic functions.

Return only the question text in a friendly, conversational tone."""
        
        print("Testing Groq API...")
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        generated_question = response.choices[0].message.content.strip()
        
        print("[OK] LLM Response received!")
        print(f"Generated question: {generated_question}")
        print(f"Length: {len(generated_question)} characters")
        
        # Test if it looks like a valid question
        if "?" in generated_question and len(generated_question) > 20:
            print("[OK] Question format looks good!")
            return True
        else:
            print("[WARN] Question format might be problematic")
            return False
            
    except Exception as e:
        print(f"[ERROR] LLM Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== GROQ LLM TEST ===")
    success = test_groq_api()
    print(f"\n{'[PASS] LLM TEST PASSED' if success else '[FAIL] LLM TEST FAILED'}")