from models import Question, QuestionType, DifficultyLevel

QUESTION_BANK = [
    # Warmup Questions
    Question(
        id="w1",
        type=QuestionType.FORMULA,
        difficulty=DifficultyLevel.BEGINNER,
        question="How would you calculate the sum of values in cells A1 through A10?",
        expected_answer="=SUM(A1:A10)",
        scoring_criteria={
            "technical": "Correct SUM function usage",
            "efficiency": "Direct range reference",
            "practices": "Proper cell referencing",
            "communication": "Clear explanation"
        }
    ),
    
    Question(
        id="w2",
        type=QuestionType.FORMULA,
        difficulty=DifficultyLevel.BEGINNER,
        question="What's the difference between relative and absolute cell references? Give an example.",
        expected_answer="Relative (A1) changes when copied, absolute ($A$1) stays fixed. Mixed references like $A1 or A$1 fix only row or column.",
        scoring_criteria={
            "technical": "Understands reference types",
            "efficiency": "Knows when to use each",
            "practices": "Proper $ usage",
            "communication": "Clear examples"
        }
    ),
    
    Question(
        id="w3",
        type=QuestionType.FORMULA,
        difficulty=DifficultyLevel.BEGINNER,
        question="How would you count the number of non-empty cells in a range?",
        expected_answer="Use COUNTA function: =COUNTA(A1:A10)",
        scoring_criteria={
            "technical": "Correct function usage",
            "efficiency": "Direct approach",
            "practices": "Proper syntax",
            "communication": "Clear explanation"
        }
    ),
    
    # Core Assessment
    Question(
        id="c1",
        type=QuestionType.DATA_ANALYSIS,
        difficulty=DifficultyLevel.INTERMEDIATE,
        question="You have sales data with columns: Date, Product, Region, Sales Amount. How would you find the top 3 products by total sales?",
        expected_answer="Use SUMIF or Pivot Table to sum sales by product, then sort descending or use LARGE function with INDEX/MATCH.",
        scoring_criteria={
            "technical": "Correct aggregation method",
            "efficiency": "Optimal approach selection",
            "practices": "Considers data structure",
            "communication": "Step-by-step explanation"
        }
    ),
    
    Question(
        id="c2",
        type=QuestionType.PIVOT_TABLE,
        difficulty=DifficultyLevel.INTERMEDIATE,
        question="Describe how you'd create a pivot table to analyze monthly sales trends by region.",
        expected_answer="Insert > Pivot Table, drag Date to Rows (group by month), Region to Columns, Sales to Values (sum), format appropriately.",
        scoring_criteria={
            "technical": "Correct pivot table setup",
            "efficiency": "Proper field placement",
            "practices": "Data grouping knowledge",
            "communication": "Clear process description"
        }
    ),
    
    Question(
        id="c3",
        type=QuestionType.FORMULA,
        difficulty=DifficultyLevel.INTERMEDIATE,
        question="How would you use VLOOKUP to find a product price from a price list?",
        expected_answer="=VLOOKUP(product_name, price_table, price_column_number, FALSE) for exact match.",
        scoring_criteria={
            "technical": "Correct VLOOKUP syntax",
            "efficiency": "Proper match type",
            "practices": "Table reference method",
            "communication": "Clear parameter explanation"
        }
    ),
    
    # Advanced Challenge
    Question(
        id="a1",
        type=QuestionType.FORMULA,
        difficulty=DifficultyLevel.ADVANCED,
        question="How would you create a dynamic lookup that returns the second highest value for each category in your data?",
        expected_answer="Use LARGE function with criteria: =LARGE(IF(Category=A2,Values),2) as array formula, or MAXIFS with helper columns.",
        scoring_criteria={
            "technical": "Advanced function knowledge",
            "efficiency": "Handles dynamic criteria",
            "practices": "Array formula understanding",
            "communication": "Explains complexity"
        }
    ),
    
    Question(
        id="a2",
        type=QuestionType.BEST_PRACTICES,
        difficulty=DifficultyLevel.ADVANCED,
        question="What are the key principles for building maintainable Excel models for financial analysis?",
        expected_answer="Separate inputs/calculations/outputs, use named ranges, consistent formatting, documentation, error checking, version control.",
        scoring_criteria={
            "technical": "Model structure knowledge",
            "efficiency": "Scalability considerations",
            "practices": "Professional standards",
            "communication": "Comprehensive coverage"
        }
    )
]

def get_questions_by_difficulty(difficulty: DifficultyLevel):
    return [q for q in QUESTION_BANK if q.difficulty == difficulty]

def get_question_by_id(question_id: str):
    return next((q for q in QUESTION_BANK if q.id == question_id), None)