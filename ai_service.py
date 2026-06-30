import json
import os
import re
from datetime import date


def _extract_json_array(text):
    match = re.search(r"\[[\s\S]*\]", text or "")
    if not match:
        return []
    return json.loads(match.group(0))


def _candidate_model_names():
    configured_model = os.getenv("GEMINI_MODEL")
    model_names = [
        configured_model,
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    return [name for index, name in enumerate(model_names) if name and name not in model_names[:index]]


def suggest_tasks(goal, existing_tasks=None):
    try:
        import google.generativeai as genai
    except ImportError as error:
        raise RuntimeError("Install google-generativeai to use AI suggestions.") from error

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Add a GEMINI_API_KEY or GOOGLE_API_KEY environment variable to use AI suggestions.")

    existing_tasks = existing_tasks or []
    genai.configure(api_key=api_key)

    prompt = f"""
You are helping a user plan work inside a task manager.
Today's date is {date.today().isoformat()}.

Goal:
{goal}

Existing tasks:
{json.dumps(existing_tasks, ensure_ascii=True)}

Return only a JSON array with 3 to 6 task objects.
Each object must use this exact shape:
{{
  "name": "short action-oriented task name",
  "description": "one helpful sentence",
  "priority": "High, Medium, or Low",
  "due_date": "YYYY-MM-DD or empty string"
}}

Avoid duplicate tasks. Keep names under 80 characters.
"""

    last_error = None
    response = None
    for model_name in _candidate_model_names():
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            break
        except Exception as error:
            last_error = error

    if response is None:
        raise RuntimeError(
            "Gemini model is not available for this API key. Try setting GEMINI_MODEL=gemini-2.5-flash."
        ) from last_error

    raw_tasks = _extract_json_array(getattr(response, "text", ""))
    suggestions = []

    for item in raw_tasks:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        priority = str(item.get("priority", "Medium")).strip().title()
        if priority not in {"High", "Medium", "Low"}:
            priority = "Medium"
        suggestions.append(
            {
                "name": name[:200],
                "description": str(item.get("description", "")).strip()[:500],
                "priority": priority,
                "due_date": str(item.get("due_date", "")).strip()[:50],
            }
        )

    return suggestions[:6]
