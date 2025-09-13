# AI-Powered Excel Mock Interviewer

## Design Document & Strategy

### 1. Solution Architecture

**Core Approach**: Conversational AI agent with structured interview flow and intelligent evaluation system.

**Technology Stack**:
- **Backend**: Python + FastAPI (lightweight, async, easy deployment)
- **LLM**: OpenAI GPT-4 (best reasoning for complex Excel evaluation)
- **Frontend**: Streamlit (rapid prototyping, built-in chat interface)
- **State Management**: Pydantic models + session storage
- **Deployment**: Docker + cloud platform (AWS/Render)

### 2. System Components

#### A. Interview Flow Manager
- Structured conversation states (intro → questions → evaluation → summary)
- Dynamic question selection based on difficulty progression
- Context-aware follow-up questions

#### B. Excel Knowledge Evaluator
- Multi-dimensional scoring: Technical accuracy, approach quality, efficiency
- Question bank covering: Formulas, Data Analysis, Pivot Tables, VBA, Best Practices
- Adaptive difficulty based on performance

#### C. State Management System
- Session persistence across conversation turns
- Performance tracking and scoring accumulation
- Interview transcript logging

# Excel Mock Interviewer

Automated system to assess a candidate's Excel skills via a multi-turn interview simulation.

## Features
- Structured interview flow (intro, questions, summary)
- Dynamic, LLM-generated questions
- Intelligent answer evaluation
- Agentic interviewer behavior
- Constructive feedback and report card
- Interactive audio interface:
  - Text-to-speech for questions and feedback
  - Voice input for answers (Web Speech API)
  - Both text and voice input available simultaneously
- Simple React frontend for Q&A

## Tech Stack
- Backend: FastAPI (Python)
- LLM: OpenAI GPT-4o-mini (or Mistral 7B)
- Frontend: React
- Storage: In-memory (no DB)

## How to Run

### Backend (API)
1. Install Python dependencies:
	```powershell
	pip install -r requirements.txt
	```
2. Start FastAPI server:
	```powershell
	uvicorn app:app --reload
	```

### Frontend (React)
1. Go to `frontend` folder:
	```powershell
	cd frontend
	```
2. Install dependencies:
	```powershell
	npm install
	```
3. Start React app:
	```powershell
	npm start
	```

## API Endpoints
- `POST /start` — Start interview, get intro and first question
- `POST /answer` — Submit answer, get feedback and next question
- `GET /summary` — Get interview summary

## Stretch Goals
- Speech-to-text (Whisper API)
- Audio output (TTS)
- Performance score summary

---
Built by GitHub Copilot