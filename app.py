
# FastAPI backend for Excel Mock Interviewer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

# Use ExcelInterviewer for interview logic
from interviewer import ExcelInterviewer
from models import InterviewSession, InterviewState, DifficultyLevel, Response
import uuid
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Groq API key from environment
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Hugging Face token (free)

# Check if running on Railway
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT_NAME", "local")
print(f"Running in environment: {RAILWAY_ENVIRONMENT}")
print(f"Groq API key configured: {bool(GROQ_API_KEY)}")
print(f"Hugging Face token configured: {bool(HF_TOKEN)}")

excel_interviewer = ExcelInterviewer(api_key=GROQ_API_KEY, hf_token=HF_TOKEN)

# Store session in memory (single user for MVP)
session = InterviewSession(
    session_id=str(uuid.uuid4()),
    state=InterviewState.INTRO
)


class AnswerRequest(BaseModel):
    answer: str




@app.get("/api")
def api_root():
    return {"message": "Excel Mock Interviewer API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "groq_key_set": bool(GROQ_API_KEY)}

@app.get("/debug/llm")
def debug_llm():
    """Debug endpoint to test LLM in production"""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Generate a simple Excel question about SUM function."}],
            temperature=0.7,
            max_tokens=100
        )
        
        return {
            "llm_working": True,
            "api_key_length": len(GROQ_API_KEY) if GROQ_API_KEY else 0,
            "test_question": response.choices[0].message.content.strip(),
            "model": "llama-3.1-8b-instant"
        }
    except Exception as e:
        return {
            "llm_working": False,
            "error": str(e),
            "api_key_length": len(GROQ_API_KEY) if GROQ_API_KEY else 0
        }

# Mount static files AFTER API routes to avoid conflicts
# This is done at the end of the file

@app.post("/api/start")
def start_interview():
    try:
        global session, excel_interviewer
        print(f"Starting interview - Groq key available: {bool(GROQ_API_KEY)}")
        print(f"HF token available: {bool(HF_TOKEN)}")
        
        # Reset session for new interview
        session = InterviewSession(
            session_id=str(uuid.uuid4()),
            state=InterviewState.INTRO
        )
        
        # Try LLM-based interview first
        try:
            intro = excel_interviewer.start_interview(session)
            question = excel_interviewer.get_next_question(session)
            
            if question:
                # LLM worked, use it
                timer_seconds = 90 if session.current_question.difficulty == DifficultyLevel.BEGINNER else 120 if session.current_question.difficulty == DifficultyLevel.INTERMEDIATE else 150
                return JSONResponse({"intro": intro, "question": question, "timer": timer_seconds})
        except Exception as llm_error:
            print(f"LLM interview failed: {llm_error}")
        
        # Fallback to question bank
        print("Using question bank fallback")
        intro = "Welcome to the Excel Mock Interviewer! I'll ask you 6 questions to assess your Excel skills. Let's begin!"
        
        from question_bank import QUESTION_BANK
        if QUESTION_BANK:
            question_obj = QUESTION_BANK[0]
            session.current_question = question_obj
            question = question_obj.question
        else:
            question = "How would you calculate the sum of values in cells A1 through A10?"
            from models import Question, QuestionType, DifficultyLevel
            session.current_question = Question(
                id="fallback_1",
                type=QuestionType.FORMULA,
                difficulty=DifficultyLevel.BEGINNER,
                question=question,
                expected_answer="=SUM(A1:A10)",
                scoring_criteria={"basic": "SUM function usage"}
            )
        
        return JSONResponse({"intro": intro, "question": question, "timer": 90})
        
    except Exception as e:
        print(f"Critical error in start_interview: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "intro": "Welcome to Excel Mock Interviewer!",
            "question": "How would you calculate the sum of values in cells A1 through A10?",
            "timer": 90
        })


@app.post("/api/answer")
def submit_answer(req: AnswerRequest):
    try:
        # Try LLM evaluation first
        try:
            evaluation = excel_interviewer.evaluate_response(session, req.answer)
            feedback = evaluation.feedback
        except Exception as eval_error:
            print(f"LLM evaluation failed: {eval_error}")
            # Fallback evaluation
            feedback = "Thank you for your answer! Let's continue with the next question."
            from models import Response
            evaluation = Response(
                question_id=session.current_question.id if session.current_question else "unknown",
                answer=req.answer,
                technical_score=7.0,
                efficiency_score=7.0,
                practices_score=7.0,
                communication_score=7.0,
                feedback=feedback
            )
            session.responses.append(evaluation)
        
        # Check if we should end the interview (after 6 questions)
        if len(session.responses) >= 6:
            try:
                summary = excel_interviewer.generate_summary(session)
            except Exception as summary_error:
                print(f"LLM summary failed: {summary_error}")
                summary = f"Interview completed! You answered {len(session.responses)} questions. Thank you for participating in the Excel skills assessment."
            return JSONResponse({"feedback": feedback, "summary": summary, "completed": True})
        
        # Try to get next question from LLM
        try:
            next_q = excel_interviewer.get_next_question(session)
            if next_q:
                timer_seconds = 90 if session.current_question.difficulty == DifficultyLevel.BEGINNER else 120 if session.current_question.difficulty == DifficultyLevel.INTERMEDIATE else 150
                return JSONResponse({"feedback": feedback, "question": next_q, "timer": timer_seconds, "completed": False})
        except Exception as question_error:
            print(f"LLM question generation failed: {question_error}")
        
        # Fallback to question bank
        from question_bank import QUESTION_BANK
        question_index = len(session.responses)
        
        if question_index < len(QUESTION_BANK):
            next_question_obj = QUESTION_BANK[question_index]
            session.current_question = next_question_obj
            next_q = next_question_obj.question
        else:
            fallback_questions = [
                "How would you use VLOOKUP to find data?",
                "What's the difference between COUNT and COUNTA?",
                "How would you create a pivot table?",
                "What are some Excel keyboard shortcuts you use?"
            ]
            next_q = fallback_questions[question_index % len(fallback_questions)]
        
        return JSONResponse({"feedback": feedback, "question": next_q, "timer": 90, "completed": False})
        
    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return JSONResponse({
            "feedback": "Thank you for your answer!",
            "question": "What Excel functions do you use most often?",
            "timer": 90,
            "completed": False
        })


@app.post("/api/timeout")
def handle_timeout():
    """Handle when timer runs out"""
    try:
        # Add timeout response
        timeout_response = Response(
            question_id=session.current_question.id if session.current_question else "timeout",
            answer="[No answer - time expired]",
            technical_score=0.0,
            efficiency_score=0.0,
            practices_score=0.0,
            communication_score=0.0,
            feedback="Time's up! Let's move on."
        )
        session.responses.append(timeout_response)
        
        # Check if this was the last question (6th question)
        if len(session.responses) >= 6:
            # End interview - generate summary
            try:
                summary = excel_interviewer.generate_summary(session)
                return JSONResponse({"summary": summary, "completed": True})
            except Exception as summary_error:
                print(f"Summary generation error: {summary_error}")
                basic_summary = f"""EXCEL SKILLS ASSESSMENT REPORT
{'=' * 50}

Interview completed with {len(session.responses)} questions.
Some questions timed out.

Assessment Complete"""
                return JSONResponse({"summary": basic_summary, "completed": True})
        else:
            # Move to next question
            next_question = excel_interviewer.get_next_question(session)
            if next_question:
                timer_seconds = 60 if session.current_question.difficulty == DifficultyLevel.BEGINNER else 90 if session.current_question.difficulty == DifficultyLevel.INTERMEDIATE else 120
                return JSONResponse({
                    "feedback": "Time's up! Let's move on.",
                    "question": next_question,
                    "timer": timer_seconds,
                    "completed": False
                })
            else:
                # Question generation failed - end interview only if we have enough questions
                if len(session.responses) >= 6:
                    summary = excel_interviewer.generate_summary(session)
                    return JSONResponse({"summary": summary, "completed": True})
                else:
                    print(f"Timeout: Question generation failed at question {len(session.responses) + 1}")
                    fallback_summary = f"Interview ended early due to technical issues. {len(session.responses)} questions completed."
                    return JSONResponse({"summary": fallback_summary, "completed": True})
            
    except Exception as e:
        print(f"Timeout error: {e}")
        # Fallback - end interview
        fallback_summary = "Interview ended due to timeout. Please try again when you have more time available."
        return JSONResponse({"summary": fallback_summary, "completed": True})

@app.get("/api/summary")
def get_summary():
    try:
        summary = excel_interviewer.generate_summary(session)
        overall_score = session.calculate_overall_score()
        return JSONResponse({"summary": summary, "score": overall_score})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/debug/session")
def debug_session():
    """Debug current session state"""
    return {
        "session_id": session.session_id,
        "state": session.state,
        "responses_count": len(session.responses),
        "messages_count": len(session.messages) if hasattr(session, 'messages') else 0,
        "current_question_id": session.current_question.id if session.current_question else None,
        "groq_key_set": bool(GROQ_API_KEY),
        "groq_key_prefix": GROQ_API_KEY[:10] if GROQ_API_KEY else "None"
    }

# Mount static files AFTER all API routes
if os.path.exists("frontend/build/index.html"):
    # Serve React build
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
else:
    # Serve static HTML
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    def root():
        try:
            with open("static/index.html", "r") as f:
                return HTMLResponse(f.read())
        except:
            return HTMLResponse("""
<!DOCTYPE html>
<html><head><title>Excel Mock Interviewer</title></head>
<body>
<h1>🎯 Excel Mock Interviewer</h1>
<p>API is running. Use /api/start to begin.</p>
</body></html>
            """)
