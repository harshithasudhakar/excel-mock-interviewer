
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
excel_interviewer = ExcelInterviewer(api_key=GROQ_API_KEY)

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

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(f.read())

@app.post("/api/start")
def start_interview():
    try:
        global session
        # Reset session for new interview
        session = InterviewSession(
            session_id=str(uuid.uuid4()),
            state=InterviewState.INTRO
        )
        # Reset interviewer state
        
        intro = excel_interviewer.start_interview(session)
        question = excel_interviewer.get_next_question(session)
        
        if not question:
            return JSONResponse({"error": "No questions available"})
        
        # Get timer based on difficulty
        timer_seconds = 60 if session.current_question.difficulty == DifficultyLevel.BEGINNER else 90 if session.current_question.difficulty == DifficultyLevel.INTERMEDIATE else 120
        
        return JSONResponse({"intro": intro, "question": question, "timer": timer_seconds})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/answer")
def submit_answer(req: AnswerRequest):
    try:
        evaluation = excel_interviewer.evaluate_response(session, req.answer)
        feedback = evaluation.feedback
        
        # Check if we should end the interview (after 6 questions)
        if len(session.responses) >= 6:
            try:
                summary = excel_interviewer.generate_summary(session)
                return JSONResponse({"feedback": feedback, "summary": summary, "completed": True})
            except Exception as summary_error:
                # Fallback summary if generation fails
                fallback_summary = f"Interview completed with {len(session.responses)} questions answered."
                return JSONResponse({"feedback": feedback, "summary": fallback_summary, "completed": True})
        
        # Get next question
        next_q = excel_interviewer.get_next_question(session)
        if next_q is None:
            # Only end if we've actually reached 6 questions
            if len(session.responses) >= 6:
                try:
                    summary = excel_interviewer.generate_summary(session)
                    return JSONResponse({"feedback": feedback, "summary": summary, "completed": True})
                except Exception as summary_error:
                    fallback_summary = f"Interview completed with {len(session.responses)} questions answered."
                    return JSONResponse({"feedback": feedback, "summary": fallback_summary, "completed": True})
            else:
                # Question generation failed but we haven't reached 6 questions - return error
                print(f"Question generation failed at question {len(session.responses) + 1}")
                return JSONResponse({"error": "Failed to generate next question"}, status_code=500)
        
        # Get timer for next question
        timer_seconds = 60 if session.current_question and session.current_question.difficulty == DifficultyLevel.BEGINNER else 90 if session.current_question and session.current_question.difficulty == DifficultyLevel.INTERMEDIATE else 120
        
        return JSONResponse({"feedback": feedback, "question": next_q, "timer": timer_seconds, "completed": False})
    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return JSONResponse({"error": f"Server error: {str(e)}"}, status_code=500)


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
