from groq import Groq
from typing import Dict, List
from models import InterviewSession, InterviewState, Response, DifficultyLevel, Question, QuestionType
from question_bank import get_questions_by_difficulty, get_question_by_id
import json
import random
import html

class ExcelInterviewer:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        
    def start_interview(self, session: InterviewSession) -> str:
        session.state = InterviewState.INTRO
        intro_message = """Hi there! 👋 I'm excited to chat with you about Excel today. Think of this as a friendly conversation where I'm curious about how you work with spreadsheets.

I'll ask you about different Excel scenarios - from basic formulas to data analysis tricks. Just explain your approach like you're helping a coworker who's stuck on a problem.

Don't worry about being perfect - I'm more interested in your thought process and practical knowledge. Ready to dive in?"""
        
        session.add_message("assistant", intro_message)
        return intro_message
    
    def evaluate_answer(self, session: InterviewSession, question, user_answer: str) -> Response:
        # Analyze the answer content for better feedback
        answer_lower = user_answer.lower()
        answer_words = answer_lower.split()
        
        # Check for uncertainty indicators
        uncertainty_phrases = ["not sure", "don't know", "not certain", "unsure", "no idea", "can't remember"]
        is_uncertain = any(phrase in answer_lower for phrase in uncertainty_phrases) or len(user_answer.strip()) < 20
        
        # Check for Excel-related terms
        excel_terms = ["formula", "function", "vlookup", "pivot", "sum", "average", "count", "index", "match", 
                      "if", "sumif", "countif", "chart", "graph", "data", "cell", "range", "worksheet", "workbook"]
        has_excel_knowledge = any(term in answer_words for term in excel_terms)
        
        if is_uncertain:
            feedback_options = [
                "No worries at all! That's a complex scenario. Let's move on to the next question!",
                "That's totally understandable! These advanced topics can be tricky. Ready for the next one?",
                "No problem! It's better to be honest than to guess. Let's continue!"
            ]
            feedback = random.choice(feedback_options)
            scores = [0.0, 0.0, 0.0, 2.0]  # Very low scores for no knowledge shown
        elif has_excel_knowledge:
            # They mentioned relevant Excel concepts
            feedback_options = [
                "Great! I can see you know your Excel functions. Nice thinking on that one!",
                "Awesome! You're definitely familiar with Excel tools. I like your approach!",
                "Perfect! You've got solid Excel knowledge there. Well done!",
                "Excellent! That's exactly the kind of Excel expertise I was hoping to hear!"
            ]
            feedback = random.choice(feedback_options)
            scores = [7.5, 8.0, 7.0, 8.5]
        else:
            # General attempt but no clear Excel knowledge shown
            feedback_options = [
                "I appreciate you giving it a try! Let's explore some Excel solutions for this.",
                "Thanks for your thoughts! There are some specific Excel techniques that could help here.",
                "Good effort! This is where Excel's advanced features really shine.",
                "Nice attempt! Let me share how Excel could tackle this challenge."
            ]
            feedback = random.choice(feedback_options)
            scores = [2.0, 3.0, 2.0, 4.0]  # Lower scores for attempts without Excel knowledge
        
        evaluation = Response(
            question_id=question.id,
            answer=user_answer,
            technical_score=scores[0],
            efficiency_score=scores[1],
            practices_score=scores[2],
            communication_score=scores[3],
            feedback=feedback
        )
        
        session.responses.append(evaluation)
        session.add_message("user", user_answer)
        return evaluation
    
    def generate_summary(self, session: InterviewSession) -> str:
        try:
            session.state = InterviewState.SUMMARY
            
            if not session.responses:
                return """EXCEL SKILLS ASSESSMENT REPORT
==================================================

No responses were recorded during this interview session.
Please restart the interview to complete your assessment.

Status: Incomplete
Recommendation: Retake the assessment when ready."""
            
            overall_score = session.calculate_overall_score()
        except Exception as e:
            print(f"Error in generate_summary: {e}")
            # Create a basic summary even if there's an error
            basic_summary = f"""EXCEL SKILLS ASSESSMENT REPORT
==================================================

Interview completed with {len(session.responses) if hasattr(session, 'responses') else 0} questions answered.

Thank you for participating in the Excel skills assessment.
Please retake the interview for a complete evaluation.

Status: Completed
Assessment Complete"""
            session.add_message("assistant", basic_summary)
            session.state = InterviewState.COMPLETED
            return basic_summary
        
        # Calculate averages using list comprehension
        technical_avg = sum(r.technical_score for r in session.responses) / len(session.responses)
        efficiency_avg = sum(r.efficiency_score for r in session.responses) / len(session.responses)
        practices_avg = sum(r.practices_score for r in session.responses) / len(session.responses)
        communication_avg = sum(r.communication_score for r in session.responses) / len(session.responses)
        
        # Determine skill level
        if overall_score >= 8.5:
            level = "Expert"
        elif overall_score >= 7.0:
            level = "Advanced"
        elif overall_score >= 5.5:
            level = "Intermediate"
        else:
            level = "Beginner"
        
        # Professional report format
        summary_parts = [
            "EXCEL SKILLS ASSESSMENT REPORT",
            "=" * 50,
            "",
            "OVERALL PERFORMANCE",
            f"Score: {overall_score:.1f}/10 | Level: {level}",
            "",
            "COMPETENCY BREAKDOWN",
            f"Technical Accuracy    {technical_avg:.1f}/10 | {'Good' if technical_avg >= 7 else 'Average' if technical_avg >= 5 else 'Needs Improvement'}",
            f"Efficiency           {efficiency_avg:.1f}/10 | {'Good' if efficiency_avg >= 7 else 'Average' if efficiency_avg >= 5 else 'Needs Improvement'}",
            f"Best Practices       {practices_avg:.1f}/10 | {'Good' if practices_avg >= 7 else 'Average' if practices_avg >= 5 else 'Needs Improvement'}",
            f"Communication        {communication_avg:.1f}/10 | {'Good' if communication_avg >= 7 else 'Average' if communication_avg >= 5 else 'Needs Improvement'}",
            "",
            "AREAS FOR IMPROVEMENT",
        ]
        
        # Add improvement areas
        improvements = []
        if technical_avg < 7: improvements.append("1. Technical Knowledge: Focus on Excel formulas and functions")
        if efficiency_avg < 7: improvements.append("2. Efficiency: Learn optimal approaches for data analysis")
        if practices_avg < 7: improvements.append("3. Best Practices: Study professional Excel modeling standards")
        if communication_avg < 7: improvements.append("4. Communication: Practice explaining technical concepts clearly")
        
        if improvements:
            summary_parts.extend(improvements)
        else:
            summary_parts.append("No significant areas for improvement identified.")
        
        summary_parts.extend([
            "",
            "INTERVIEW TRANSCRIPT",
        ])
        
        # Add question-by-question transcript
        for i, response in enumerate(session.responses, 1):
            summary_parts.append(f"Q{i}: [Question {i} from interview]")
            summary_parts.append(f"A{i}: {html.escape(response.answer[:100])}{'...' if len(response.answer) > 100 else ''}")
            summary_parts.append(f"Score: {((response.technical_score + response.efficiency_score + response.practices_score + response.communication_score) / 4):.1f}/10")
            summary_parts.append(f"Feedback: {html.escape(response.feedback)}")
            summary_parts.append("")
        
        summary_parts.extend([
            "RECOMMENDATION",
        ])
        
        if overall_score >= 8.0:
            recommendation = "Recommended: Strong Excel skills demonstrated. Ready for advanced analytical roles."
        elif overall_score >= 6.0:
            recommendation = "Recommended: Good foundation with room for growth. Consider advanced Excel training."
        else:
            recommendation = "Not Recommended: Fundamental Excel training required before proceeding."
        
        summary_parts.extend([
            recommendation,
            "",
            f"Questions Answered: {len(session.responses)}",
            "Assessment Complete"
        ])
        
        try:
            summary = "\n".join(summary_parts)
            session.add_message("assistant", summary)
            session.state = InterviewState.COMPLETED
            return summary
        except Exception as e:
            print(f"Error finalizing summary: {e}")
            # Return basic summary if formatting fails
            basic_summary = f"""EXCEL SKILLS ASSESSMENT REPORT
==================================================

OVERALL PERFORMANCE
Score: {overall_score:.1f}/10 | Level: {level}

Questions Answered: {len(session.responses)}
Assessment Complete"""
            return basic_summary
    
    def should_continue_interview(self, session: InterviewSession) -> bool:
        """Simple rule-based termination"""
        return len(session.responses) < 6  # Always ask exactly 6 questions
    
    def get_next_question(self, session: InterviewSession):
        """Generate next question using LLM with question bank as examples"""
        print(f"Getting next question. Current responses: {len(session.responses)}")
        
        # Check if interview should continue
        if not self.should_continue_interview(session):
            print(f"Interview should not continue. Responses: {len(session.responses)}")
            session.state = InterviewState.SUMMARY
            return None
        
        # Determine difficulty based on progress
        if len(session.responses) >= 4:
            difficulty = DifficultyLevel.ADVANCED
        elif len(session.responses) >= 2:
            difficulty = DifficultyLevel.INTERMEDIATE
        else:
            difficulty = DifficultyLevel.BEGINNER
        
        # Get example questions for the LLM
        example_questions = get_questions_by_difficulty(difficulty)
        
        # Build context from previous responses and questions
        performance_context = ""
        previous_questions = ""
        
        if session.responses:
            recent_scores = [(r.technical_score + r.efficiency_score + r.practices_score + r.communication_score) / 4 
                           for r in session.responses[-2:]]
            avg_recent = sum(recent_scores) / len(recent_scores)
            performance_context = f"Recent performance: {avg_recent:.1f}/10. "
            
        # Get previous questions to avoid repetition
        if hasattr(session, 'messages') and session.messages:
            asked_questions = [msg.content for msg in session.messages if msg.role == 'assistant' and '?' in msg.content]
            if asked_questions:
                previous_questions = f"\nPrevious questions asked:\n{chr(10).join([f'- {q[:80]}...' for q in asked_questions[-3:]])}"
        
        # Create conversational prompt for LLM to generate question
        conversation_starters = {
            DifficultyLevel.BEGINNER: ["Let's start with something practical...", "Here's a common scenario...", "Imagine you're helping a colleague with..."],
            DifficultyLevel.INTERMEDIATE: ["Now let's get a bit more interesting...", "Here's a situation that comes up often...", "Let's say you need to..."],
            DifficultyLevel.ADVANCED: ["Time for a challenge...", "Here's something that might test your expertise...", "Let's dive into something more complex..."]
        }
        
        starter = random.choice(conversation_starters[difficulty])
        
        prompt = f"""You are a friendly Excel interviewer having a conversational chat. Generate a {difficulty.value} level Excel question.

{performance_context}Question #{len(session.responses) + 1} of 6.

Start with: "{starter}"

Example {difficulty.value} questions:
{chr(10).join([f"- {q.question}" for q in example_questions[:2]])}
{previous_questions}

IMPORTANT: Generate a NEW question that is DIFFERENT from any previous questions. Avoid repeating topics or scenarios.

Generate a conversational, scenario-based Excel question that tests {difficulty.value} skills. 
Make it sound like you're asking a colleague about a real work situation.
Focus on: {'formulas and basic functions' if difficulty == DifficultyLevel.BEGINNER else 'data analysis and intermediate functions' if difficulty == DifficultyLevel.INTERMEDIATE else 'advanced functions and best practices'}.

Return only the question text in a friendly, conversational tone."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400  # Increased for complete questions
            )
            
            generated_question = response.choices[0].message.content.strip()
            
            # Create a dynamic question object
            question_id = f"gen_{len(session.responses) + 1}"
            session.current_question = Question(
                id=question_id,
                type=QuestionType.FORMULA,  # Default type
                difficulty=difficulty,
                question=generated_question,
                expected_answer="Dynamic evaluation",
                scoring_criteria={"dynamic": "LLM-based evaluation"}
            )
            
            # Add question to conversation history
            session.add_message("assistant", generated_question)
            
            return generated_question
            
        except Exception as e:
            print(f"Question generation error: {e}")
            # Fallback to example questions
            if example_questions:
                print(f"Using fallback question from question bank")
                question = example_questions[0]
                session.current_question = question
                # Add question to conversation history
                session.add_message("assistant", question.question)
                return question.question
            
            print(f"No fallback questions available, ending interview early")
            session.state = InterviewState.SUMMARY
            return None
    
    def evaluate_response(self, session: InterviewSession, user_answer: str):
        """Evaluate user response and return feedback"""
        if not session.current_question:
            fallback_response = Response(
                question_id="unknown",
                answer=user_answer,
                technical_score=7.0,
                efficiency_score=7.0,
                practices_score=7.0,
                communication_score=7.0,
                feedback="Thanks for that! Let's keep the conversation going."
            )
            session.responses.append(fallback_response)
            session.add_message("user", user_answer)
            return fallback_response
        
        return self.evaluate_answer(session, session.current_question, user_answer)