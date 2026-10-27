import re
import json
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def compare_resume_with_jd(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an expert resume reviewer.
Compare the resume with the job description and respond ONLY in JSON.

Rules:
- DO NOT include explanations outside JSON.
- Always return all keys listed below.
- Use bullet points where applicable.
- Keep feedback concise but specific.

JSON format:
{{
  "skills_missing": ["skill1", "skill2"],
  "experience_gap": ["gap1", "gap2"],
  "suggestions": ["improvement1", "improvement2"],
  "score": 0,
  "feedback": "short summary"
}}

Job Description:
{job_description}

Resume:
{resume_text}
"""

    try:
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            raw_text = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            raw_text = response.candidates[0].content.parts[0].text.strip()
        else:
            raw_text = ""

        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            logging.info(f"Gemini comparison result:\n{json.dumps(parsed, indent=2)}")
            return parsed

    except Exception as e:
        logging.error(f"Gemini comparison failed: {e}")
        return {
            "skills_missing": [],
            "experience_gap": [],
            "suggestions": [f"⚠️ Gemini failed: {e}"],
            "score": 0,
            "feedback": "⚠️ No structured feedback generated"
        }
