#!/usr/bin/env python3
"""Test question generation to check for repetition"""

import os
from dotenv import load_dotenv
from interviewer import ExcelInterviewer
from models import InterviewSession, InterviewState, DifficultyLevel
import uuid

load_dotenv()

def test_question_uniqueness():
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found")
        return False
    
    print("=== TESTING QUESTION GENERATION ===")
    
    # Create interviewer and session
    interviewer = ExcelInterviewer(api_key=api_key)
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        state=InterviewState.INTRO
    )
    
    generated_questions = []
    
    # Generate 6 questions (full interview)
    for i in range(6):
        print(f"\n--- Generating Question {i+1} ---")
        
        question = interviewer.get_next_question(session)
        
        if question:
            print(f"Q{i+1}: {question[:100]}...")
            generated_questions.append(question)
            
            # Simulate a response to continue the interview
            from models import Response
            dummy_response = Response(
                question_id=f"test_{i+1}",
                answer="Test answer",
                technical_score=7.0,
                efficiency_score=7.0,
                practices_score=7.0,
                communication_score=7.0,
                feedback="Good answer!"
            )
            session.responses.append(dummy_response)
        else:
            print(f"Q{i+1}: No question generated")
            break
    
    # Check for uniqueness
    print(f"\n=== UNIQUENESS CHECK ===")
    print(f"Total questions generated: {len(generated_questions)}")
    
    unique_questions = set(generated_questions)
    print(f"Unique questions: {len(unique_questions)}")
    
    if len(generated_questions) == len(unique_questions):
        print("[PASS] All questions are unique!")
        return True
    else:
        print("[FAIL] Found duplicate questions:")
        for i, q1 in enumerate(generated_questions):
            for j, q2 in enumerate(generated_questions[i+1:], i+1):
                if q1 == q2:
                    print(f"  Duplicate: Q{i+1} == Q{j+1}")
        return False

if __name__ == "__main__":
    success = test_question_uniqueness()
    print(f"\n{'[PASS] TEST PASSED' if success else '[FAIL] TEST FAILED'}")