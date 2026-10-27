import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_suggestions(comparison_result: dict) -> list:
    prompt = f"""
You are a resume improvement expert.

Based on the following analysis, generate rewrite-level suggestions to improve the resume. Focus on actionable changes like phrasing, formatting, and content additions.

Analysis:
{comparison_result}

Respond with a list of suggestions only. Do not include any explanation or formatting.

Example:
- Add more quantifiable achievements under work experience.
- Include certifications relevant to the job description.
- Improve clarity in the summary section.

Suggestions:
"""

    try:
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            raw_text = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            raw_text = response.candidates[0].content.parts[0].text.strip()
        else:
            raw_text = ""

        # Split into list
        suggestions = [line.strip("-• ").strip() for line in raw_text.splitlines() if line.strip()]
        return suggestions

    except Exception as e:
        return [f"⚠️ Failed to generate suggestions: {e}"]
