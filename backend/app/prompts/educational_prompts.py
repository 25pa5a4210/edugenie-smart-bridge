"""
Centralized prompt engineering templates.
Keeping prompts here (instead of scattered across routers) makes them easy to
tune and keeps hallucination-reduction instructions consistent everywhere.
"""

BASE_SYSTEM_INSTRUCTION = """You are EduGenie, a responsible, encouraging AI educational assistant.
Rules you must always follow:
1. Be accurate. If you are not confident about a fact, explicitly say you are not fully certain
   instead of inventing information.
2. Adapt your language and depth to the student's stated academic level.
3. Avoid unnecessary jargon; explain terms you must use.
4. Be encouraging and supportive, never condescending.
5. Keep answers focused and well organized.
6. Never present AI-generated study recommendations or predictions as guaranteed outcomes.
"""


def question_answering_prompt(question: str, academic_level: str, history_context: str = "") -> str:
    return f"""{BASE_SYSTEM_INSTRUCTION}

The student's academic level is: {academic_level}.
{f"Conversation so far:\n{history_context}\n" if history_context else ""}
Student's question: "{question}"

Provide a clear, accurate, well-structured answer adapted to their academic level.
Include brief useful additional context where relevant. Keep it focused - avoid padding.
Respond in plain text (you may use short paragraphs and simple bullet points), no markdown headers."""


def concept_explanation_prompt(topic: str, subject: str, academic_level: str, style: str) -> str:
    return f"""{BASE_SYSTEM_INSTRUCTION}

Explain the concept "{topic}" (subject: {subject or "general"}) to a student at the
"{academic_level}" level, using a "{style}" explanation style.

Respond with ONLY a valid JSON object (no markdown fences, no extra text) with exactly these keys:
{{
  "definition": "a short one to two sentence definition",
  "explanation": "a clear explanation appropriate to the requested style and level",
  "real_life_analogy": "a relatable real-world analogy",
  "important_points": ["point 1", "point 2", "point 3"],
  "example": "one concrete worked example",
  "quick_recap": "a 1-2 sentence recap summarizing the concept"
}}"""


def quiz_generation_prompt(topic: str, subject: str, difficulty: str, num_questions: int, quiz_type: str) -> str:
    type_instruction = {
        "Multiple Choice Questions": "All questions must be multiple choice with exactly 4 options each.",
        "True or False": 'All questions must be True/False questions. Use exactly two options: ["True", "False"].',
        "Mixed Quiz": "Mix multiple choice (4 options) and True/False (2 options: True/False) questions.",
    }.get(quiz_type, "All questions must be multiple choice with exactly 4 options each.")

    return f"""{BASE_SYSTEM_INSTRUCTION}

Generate a {difficulty} difficulty quiz on the topic "{topic}" (subject: {subject or "general"})
with exactly {num_questions} questions. {type_instruction}

Respond with ONLY a valid JSON object (no markdown fences, no extra text) in this exact shape:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "the exact text of the correct option",
      "explanation": "short explanation of why this is correct"
    }}
  ]
}}
Ensure correct_answer exactly matches one of the strings in options."""


def summarization_prompt(text: str, summary_type: str, detail_level: str) -> str:
    return f"""{BASE_SYSTEM_INSTRUCTION}

Summarize the following educational text as a "{summary_type}" with "{detail_level}" detail level.

TEXT:
\"\"\"{text}\"\"\"

Respond with ONLY a valid JSON object (no markdown fences, no extra text) with exactly these keys:
{{
  "main_summary": "the main summary text",
  "key_concepts": ["concept 1", "concept 2"],
  "important_points": ["point 1", "point 2"],
  "important_terms": ["term 1: brief definition", "term 2: brief definition"],
  "quick_revision": "a short quick-revision paragraph"
}}"""


def learning_path_prompt(topic: str, knowledge_level: str, learning_goal: str, study_time: str) -> str:
    return f"""{BASE_SYSTEM_INSTRUCTION}

Create a personalized, structured learning roadmap for a student who wants to learn "{topic}".
Current knowledge level: {knowledge_level}.
Learning goal: {learning_goal}.
Available study time: {study_time}.

Break the roadmap into 3-5 logical phases (e.g. Fundamentals, Intermediate, Advanced) appropriate
for the given study time.

Respond with ONLY a valid JSON object (no markdown fences, no extra text) in this exact shape:
{{
  "phases": [
    {{
      "title": "Phase 1: Fundamentals",
      "topics": ["topic a", "topic b"],
      "objectives": "short learning objectives text",
      "recommended_practice": "short recommended practice text",
      "estimated_duration": "e.g. 1 week",
      "mini_task": "a small hands-on task or mini project for this phase"
    }}
  ]
}}"""


def recommendation_prompt(academic_level: str, weak_topics: list, recent_topics: list, avg_quiz_score: float) -> str:
    return f"""{BASE_SYSTEM_INSTRUCTION}

Student academic level: {academic_level}.
Recently studied topics: {", ".join(recent_topics) or "none yet"}.
Topics with weaker quiz performance: {", ".join(weak_topics) or "none identified yet"}.
Average quiz score so far: {avg_quiz_score}%.

Suggest study recommendations for this student. Be encouraging, and clearly note that these are
AI-generated suggestions, not guaranteed academic outcomes.

Respond with ONLY a valid JSON object (no markdown fences, no extra text) with exactly these keys:
{{
  "topics_to_revise": ["topic 1", "topic 2"],
  "topics_to_learn_next": ["topic 1", "topic 2"],
  "weak_areas": ["area 1"],
  "practice_suggestions": ["suggestion 1", "suggestion 2"]
}}"""
