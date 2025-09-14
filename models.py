from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class InterviewState(str, Enum):
    INTRO = "intro"
    WARMUP = "warmup"
    CORE = "core"
    ADVANCED = "advanced"
    SUMMARY = "summary"
    COMPLETED = "completed"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionType(str, Enum):
    FORMULA = "formula"
    DATA_ANALYSIS = "data_analysis"
    PIVOT_TABLE = "pivot_table"
    VBA = "vba"
    BEST_PRACTICES = "best_practices"

class Question(BaseModel):
    id: str
    type: QuestionType
    difficulty: DifficultyLevel
    question: str
    expected_answer: str
    scoring_criteria: Dict[str, str]

class Response(BaseModel):
    question_id: str
    answer: str
    technical_score: float
    efficiency_score: float
    practices_score: float
    communication_score: float
    feedback: str

class InterviewSession(BaseModel):
    session_id: str
    state: InterviewState
    current_question: Optional[Question] = None
    responses: List[Response] = []
    overall_score: float = 0.0
    transcript: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.transcript.append({"role": role, "content": content})
    
    @property
    def conversation_history(self):
        return self.transcript
    
    @property
    def messages(self):
        """Alias for transcript to maintain compatibility"""
        return self.transcript

    def calculate_overall_score(self) -> float:
        if not self.responses:
            return 0.0
        total_score = 0.0
        for response in self.responses:
            weighted_score = (
                response.technical_score * 0.4 +
                response.efficiency_score * 0.3 +
                response.practices_score * 0.2 +
                response.communication_score * 0.1
            )
            total_score += weighted_score
        self.overall_score = total_score / len(self.responses)
        return self.overall_score


# InterviewerAgent manages the interview flow, state, and LLM interaction
import uuid
from typing import Any

class InterviewerAgent:
    def __init__(self, llm_client: Any):
        self.llm_client = llm_client
        self.session = InterviewSession(
            session_id=str(uuid.uuid4()),
            state=InterviewState.INTRO,
            responses=[],
            transcript=[],
        )
        self.round = 0
        self.max_rounds = 5

    def start_interview(self):
        intro = "Hello, I'm your Excel mock interviewer. I'll ask you a series of questions to assess your skills. Ready to begin?"
        self.session.add_message("interviewer", intro)
        self.session.state = InterviewState.WARMUP
        return intro

    def next_question(self):
        # Use LLM to generate next question based on history
        prompt = self._build_question_prompt()
        question_data = self.llm_client.generate_question(prompt)
        question = Question(**question_data)
        self.session.current_question = question
        self.session.add_message("interviewer", question.question)
        self.round += 1
        return question.question

    def submit_answer(self, answer: str):
        self.session.add_message("candidate", answer)
        eval_prompt = self._build_evaluation_prompt(answer)
        feedback_data = self.llm_client.evaluate_answer(eval_prompt)
        response = Response(
            question_id=self.session.current_question.id,
            answer=answer,
            technical_score=feedback_data["technical_score"],
            efficiency_score=feedback_data["efficiency_score"],
            practices_score=feedback_data["practices_score"],
            communication_score=feedback_data["communication_score"],
            feedback=feedback_data["feedback"]
        )
        self.session.responses.append(response)
        self.session.add_message("interviewer", response.feedback)
        # Advance state or finish
        if self.round >= self.max_rounds:
            self.session.state = InterviewState.SUMMARY
        return response.feedback

    def get_summary(self):
        # Use LLM to generate summary based on responses
        summary_prompt = self._build_summary_prompt()
        summary = self.llm_client.generate_summary(summary_prompt)
        self.session.add_message("interviewer", summary)
        self.session.state = InterviewState.COMPLETED
        return summary

    def _build_question_prompt(self):
        # Build prompt for LLM to generate next question
        history = self.session.transcript[-5:] if len(self.session.transcript) > 5 else self.session.transcript
        return {
            "history": history,
            "difficulty": "adaptive",
            "topic": "Excel"
        }

    def _build_evaluation_prompt(self, answer: str):
        # Build prompt for LLM to evaluate answer
        return {
            "question": self.session.current_question.question,
            "expected_answer": self.session.current_question.expected_answer,
            "candidate_answer": answer,
            "criteria": self.session.current_question.scoring_criteria
        }

    def _build_summary_prompt(self):
        # Build prompt for LLM to generate summary
        return {
            "responses": [r.dict() for r in self.session.responses],
            "overall_score": self.session.calculate_overall_score(),
            "transcript": self.session.transcript
        }