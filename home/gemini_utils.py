from google import genai
import os

# Dynamically load from local .env file if it exists (pure Python implementation)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

client = None


def get_client():
    global client
    if client is None:
        try:
            client = genai.Client()
        except Exception as e:
            raise ValueError(
                "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable. "
                "For Windows PowerShell, run: [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your_key_here', 'User')"
            ) from e
    return client




def classify_questions(text):

    prompt = f"""
You are an expert ICSE/CBSE examiner.

Extract every question from the paper.

For each question identify:
1. Most relevant chapter
2. Question text

Return ONLY valid JSON.

Example:

[
    {{
        "chapter": "Force",
        "question": "Define force."
    }},
    {{
        "chapter": "Light",
        "question": "Define reflection."
    }}
]

Rules:
- Return only JSON
- No explanations
- No markdown
- No ```json
- No extra text

Paper:
{text}
"""

    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def get_explanation(question_text, subject="Physics"):
    prompt = f"""
You are an expert ICSE/CBSE tutor.
Provide a clear, step-by-step detailed solution and explanation for this {subject} question.
Use clear headings, steps, and formulas where applicable.

Question:
{question_text}

Format the output cleanly in HTML/Markdown format. Do not use complex layout symbols. Keep it readable.
"""
    try:
        response = get_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Could not connect to Gemini API. Here is a simulated explanation template for this topic:\n\n**Question:** {question_text}\n\n**Step 1 (Recall Formula):** Identify the governing principles.\n**Step 2 (Apply data):** Substitute values into the equation.\n**Step 3 (Solve):** Calculate the final result with proper units."


def generate_mock_test_questions(chapter_name, questions_list):
    questions_text = "\n".join([f"- {q}" for q in questions_list])
    prompt = f"""
You are an expert ICSE/CBSE Physics teacher.
Based on the following past year questions of the chapter "{chapter_name}", generate a mock test:
1. Generate 20 Multiple Choice Questions (MCQs) related to these concepts. For each MCQ, provide:
   - The question text
   - 4 options (A, B, C, D)
   - The correct option (A, B, C, or D)
   - A brief step-by-step explanation of the answer
2. Generate 5 high-yield expected short-answer questions. For each expected question, provide:
   - The question text
   - The model answer/solution

Return ONLY a valid JSON object.
Format:
{{
  "mcqs": [
    {{
      "question": "Question text here?",
      "options": {{"A": "Option A text", "B": "Option B text", "C": "Option C text", "D": "Option D text"}},
      "correct_option": "A",
      "explanation": "Explanation here..."
    }}
  ],
  "expected": [
    {{
      "question": "Expected question text here?",
      "answer": "Expected model answer here."
    }}
  ]
}}

Rules:
- Return ONLY raw JSON, no markdown blocks, no ```json, no extra text.
- Base the questions on the following concepts and past questions:
{questions_text}
"""
    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text