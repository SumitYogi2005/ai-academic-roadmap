"""
Prompt templates for all AI workflows.
"""
from __future__ import annotations


def syllabus_analysis_prompt(text: str) -> str:
    return f"""You are an expert academic curriculum analyst.

Analyse the following syllabus text and extract its structured content.

SYLLABUS TEXT:
{text[:12000]}

Return a JSON object with this exact structure:
{{
  "subject": "Subject or course name",
  "units": [
    {{
      "id": "unit1",
      "name": "Unit name",
      "description": "Brief description",
      "sequence": 1,
      "topics": [
        {{
          "id": "unit1_topic1",
          "name": "Topic name",
          "description": "What this topic covers",
          "duration_hours": 2.0,
          "objectives": ["Learning objective 1", "Learning objective 2"]
        }}
      ]
    }}
  ],
  "warnings": ["Any concerns about the extraction, e.g. missing sections"]
}}

Rules:
- Extract all units, chapters, or modules as top-level units
- Extract all topics, subtopics within each unit
- Estimate realistic duration_hours per topic based on complexity (0.5 to 8 hours)
- Keep warnings array empty if extraction looks complete
- Do NOT invent topics not present in the source text
- Use sequential IDs: unit1, unit2 and unit1_topic1, unit1_topic2, etc."""


def academic_roadmap_prompt(syllabus_data: dict) -> str:
    units_summary = ""
    for unit in syllabus_data.get("units", []):
        units_summary += f"\nUnit: {unit['name']}\n"
        for topic in unit.get("topics", []):
            units_summary += f"  - {topic['name']}: {topic.get('description', '')}\n"

    return f"""You are a learning design expert creating an academic roadmap.

Based on this syllabus structure, generate a roadmap with learning nodes.

SUBJECT: {syllabus_data.get('subject', 'Unknown')}
UNITS AND TOPICS:
{units_summary}

Return a JSON object:
{{
  "nodes": [
    {{
      "source_topic_id": "unit1_topic1",
      "title": "Node title",
      "description": "What students will learn and do in this node",
      "type": "concept",
      "duration_hours": 2.0,
      "difficulty": "beginner",
      "position_x": 100,
      "position_y": 100
    }}
  ],
  "edges": [
    {{
      "source_topic_id": "unit1_topic1",
      "target_topic_id": "unit1_topic2",
      "relationship_type": "prerequisite"
    }}
  ]
}}

Rules:
- type must be one of: concept, practice, project, assessment
- difficulty must be: beginner, intermediate, or advanced
- Add prerequisite edges where topics build on each other
- Keep positions spaced (200px apart minimum); arrange in a logical flow
- Each unit's topics should generally prerequisite the next
- Assessment nodes should come at the end of each unit"""


def skill_roadmap_prompt(skill: str, level: str, goal: str, timeframe_weeks: int) -> str:
    return f"""You are a learning design expert creating a skill development roadmap.

Skill: {skill}
Current Level: {level}
Goal: {goal}
Timeframe: {timeframe_weeks} weeks

Generate a comprehensive learning roadmap. Return JSON:
{{
  "nodes": [
    {{
      "title": "Node title",
      "description": "Detailed description of what to learn/do",
      "type": "concept",
      "duration_hours": 3.0,
      "difficulty": "beginner",
      "position_x": 100,
      "position_y": 100
    }}
  ],
  "edges": [
    {{
      "source_index": 0,
      "target_index": 1,
      "relationship_type": "prerequisite"
    }}
  ]
}}

Progression:
1. Foundation concepts (beginner)
2. Core skills (intermediate)
3. Practice exercises and small projects
4. Advanced topics
5. Capstone project
6. Assessment

Use source_index/target_index (0-based) to define prerequisite edges.
Make the roadmap achievable within {timeframe_weeks} weeks."""


def explain_topic_prompt(topic_title: str, topic_description: str, user_question: str, context: str = "") -> str:
    ctx_section = f"\nSyllabus context:\n{context}\n" if context else ""
    return f"""You are a knowledgeable tutor helping a student understand a topic.

Topic: {topic_title}
Description: {topic_description}
{ctx_section}
Student's question: {user_question}

Provide a clear, educational explanation. Use examples where helpful.
Structure your answer with brief sections if needed. Keep it focused and practical."""


def generate_quiz_prompt(topic_title: str, topic_description: str, difficulty: str = "medium", num_questions: int = 5) -> str:
    return f"""Generate a quiz for a student studying the following topic.

Topic: {topic_title}
Description: {topic_description}
Difficulty: {difficulty}
Number of questions: {num_questions}

Return JSON:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct"
    }}
  ]
}}

correct_answer is the 0-based index of the correct option.
Make questions diverse: conceptual understanding, application, analysis."""


def generate_notes_prompt(topic_title: str, topic_description: str, objectives: list[str]) -> str:
    obj_text = "\n".join(f"- {o}" for o in objectives) if objectives else "- Understand the core concepts"
    return f"""Create concise, well-structured study notes for a student.

Topic: {topic_title}
Description: {topic_description}
Learning Objectives:
{obj_text}

Return JSON:
{{
  "title": "{topic_title}",
  "summary": "One-paragraph summary",
  "key_concepts": [
    {{"term": "Term name", "definition": "Clear definition"}}
  ],
  "main_points": ["Key point 1", "Key point 2"],
  "examples": ["Concrete example 1"],
  "review_questions": ["Question to test understanding?"]
}}"""


def suggest_resources_prompt(topic_title: str, learning_goal: str) -> str:
    return f"""Suggest learning resources for a student studying the following.

Topic: {topic_title}
Learning Goal: {learning_goal}

Return JSON:
{{
  "resources": [
    {{
      "title": "Resource title",
      "type": "video|article|book|course|documentation",
      "description": "What this resource covers and why it's useful",
      "url": "https://example.com or null if not available"
    }}
  ]
}}

Suggest 4-6 high-quality resources. Include a mix of types (video, article, documentation)."""
