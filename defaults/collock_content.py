import random

# =============================================================================
# RECRUITER PERSONAS
# =============================================================================
# Each value is injected verbatim into the LLM system prompt to shape how it
# phrases questions and feedback.

PERSONAS = {
  "The Friendly Coach": {
    "description": "You are a warm, encouraging recruiter who makes the candidate feel at ease. You celebrate strengths, frame all feedback constructively, and keep energy high.",
    "img_prompt": "Photorealistic recruiter portrait. Persona: warm, encouraging, reassuring. Soft smile, relaxed posture, open body language, attentive eyes. Business casual. Modern office, neutral background. DSLR, 50mm, shallow depth, natural light, realistic skin. Chest-up, eye-level."
  },
  "The Tough Realist": {
    "description": "You are a direct, no-nonsense recruiter who values candour over comfort. You challenge vague answers, demand specifics, and hold the candidate to a high standard. Your feedback is blunt but fair.",
    "img_prompt": "Photorealistic recruiter portrait. Persona: direct, strict, no-nonsense. Serious expression, steady gaze, composed posture, minimal smile. Formal business attire. Corporate office, neutral or slightly dark background. DSLR, 50mm, shallow depth, natural light, realistic skin. Chest-up, eye-level."
  },
  "The Technical Deep-Diver": {
    "description": "You are a technically rigorous recruiter who digs into implementation details, architectural trade-offs, and edge cases. Every answer earns a deeper follow-up. You prize precision and depth over breadth.",
    "img_prompt": "Photorealistic recruiter portrait. Persona: analytical, highly technical, focused. Thoughtful expression, attentive eyes, calm posture, professional demeanor. Smart business casual. Modern office or tech workspace. DSLR, 50mm, shallow depth, natural light, realistic skin. Chest-up, eye-level."
  }
}


# =============================================================================
# FALLBACK QUESTION BANKS
# =============================================================================
# Used by get_ai_response() when the LLM call fails (no internet, wrong key,
# rate limit, etc.). Guarantees the interview can continue offline.

QUESTION_BANKS = {
    "General": [
        "Tell me about yourself and what motivates your career choices.",
        "What is one project you are most proud of and why?",
        "How do you prioritize tasks when you have multiple competing deadlines?",
        "Where do you see yourself professionally in the next three years?",
        "Describe your ideal working environment and team dynamic.",
        "What does success look like to you in the first 90 days of a new role?",
    ],
    "Technical": [
        "Describe a technically complex problem you solved. Walk me through your approach.",
        "How would you debug a slow API endpoint in a production web application?",
        "What trade-offs do you consider when choosing between SQL and NoSQL databases?",
        "How do you approach writing code that others will need to maintain long-term?",
        "Explain the difference between concurrency and parallelism, and when you'd use each.",
        "How do you decide when to introduce an abstraction versus keeping code simple and repetitive?",
    ],
    "Behavioral": [
        "Tell me about a conflict with a teammate and how you resolved it.",
        "Describe a time you received critical feedback. How did you respond?",
        "Tell me about a project where the scope changed mid-way. How did you adapt?",
        "Give an example of a time you had to learn something new very quickly.",
        "Describe a situation where you disagreed with a manager's decision.",
        "Tell me about a time you took ownership of something outside your formal responsibilities.",
    ],
}

# Mixed and Coding draw from the combined or technical pool respectively.
QUESTION_BANKS["Mixed"] = (
    QUESTION_BANKS["General"] +
    QUESTION_BANKS["Technical"] +
    QUESTION_BANKS["Behavioral"]
)
QUESTION_BANKS["Coding"] = QUESTION_BANKS["Technical"]


def fallback_question(interview_type: str) -> str:
    pool = QUESTION_BANKS.get(interview_type, QUESTION_BANKS["General"])
    return random.choice(pool)


def get_img_prompt(persona_name: str) -> str:
    return PERSONAS.get(persona_name, PERSONAS["The Friendly Coach"])["img_prompt"]


# =============================================================================
# CODING TASKS
# =============================================================================

CODING_TASKS = [
    {
        "title": "Array Intersection",
        "difficulty": "Medium",
        "language": "Python",
        "description": (
            "Write a function that returns the intersection of two lists — "
            "only elements present in both, with no duplicates."
        ),
        "starter_code": (
            "def intersect(list1, list2):\n"
            "    result = []\n"
            "    # Your code here\n"
            "    return result\n\n"
            "# intersect([1, 2, 3, 4], [2, 4, 6])  →  [2, 4]"
        ),
    },
    {
        "title": "Reverse a String",
        "difficulty": "Easy",
        "language": "Python",
        "description": "Reverse a string using a loop — no built-in reverse or slicing.",
        "starter_code": (
            "def reverse_string(s):\n"
            "    result = ''\n"
            "    # Your code here\n"
            "    return result\n\n"
            "# reverse_string('hello')  →  'olleh'"
        ),
    },
    {
        "title": "Count Word Frequency",
        "difficulty": "Easy",
        "language": "Python",
        "description": (
            "Given a sentence, return a dict mapping each word to its occurrence count. "
            "Ignore punctuation; treat words as lowercase."
        ),
        "starter_code": (
            "def word_frequency(sentence):\n"
            "    counts = {}\n"
            "    # Your code here\n"
            "    return counts\n\n"
            "# word_frequency('the cat sat on the mat')  →  {'the': 2, 'cat': 1, ...}"
        ),
    },
    {
        "title": "FizzBuzz",
        "difficulty": "Easy",
        "language": "Python",
        "description": (
            "Return a list of strings for numbers 1 to n. "
            "Use 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, "
            "'FizzBuzz' for both, and the number as a string otherwise."
        ),
        "starter_code": (
            "def fizzbuzz(n):\n"
            "    result = []\n"
            "    # Your code here\n"
            "    return result\n\n"
            "# fizzbuzz(15)[-1]  →  'FizzBuzz'"
        ),
    },
    {
        "title": "Valid Parentheses",
        "difficulty": "Medium",
        "language": "Python",
        "description": (
            "Given a string of brackets '(', ')', '{', '}', '[', ']', "
            "return True if every opening bracket has a matching closing bracket in the correct order."
        ),
        "starter_code": (
            "def is_valid(s):\n"
            "    # Your code here\n"
            "    pass\n\n"
            "# is_valid('({[]})') → True\n"
            "# is_valid('([)]')  → False"
        ),
    },
]
