import os
import uuid
import logging
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from config import GEMINI_API_KEY
from gcs_storage import upload_to_gcs
from workflow import build_resume_graph

# ----------------------------
# 1️⃣ Logging
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# 2️⃣ FastAPI Setup
# ----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 3️⃣ Main Endpoint
# ----------------------------
@app.post("/optimize_resume/")
async def optimize_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    job_url: str = Form(None)  # Optional: if user provides JD URL
):
    try:
        # Save resume temporarily
        file_ext = os.path.splitext(resume.filename)[-1].lower()
        temp_filename = f"temp_{uuid.uuid4().hex}{file_ext}"
        with open(temp_filename, "wb") as f:
            f.write(await resume.read())

        # Upload to GCS
        gcs_path = upload_to_gcs(temp_filename, resume.filename)

        # Build LangGraph
        graph = build_resume_graph()

        # Prepare initial state
        initial_state = {
            "resume_gcs_uri": gcs_path,
            "job_description_text": job_description if not job_url else None,
            "job_description_url": job_url if job_url else None
        }

        # Run LangGraph
        final_state = graph.invoke(initial_state)

        # Structure response
        return {
    "status": "success",
    "data": {
        "skills_missing": final_state.get("comparison_result", {}).get("skills_missing", []),
        "experience_gap": final_state.get("comparison_result", {}).get("experience_gap", []),
        "suggestions": final_state.get("suggestions", []),
        "score": final_state.get("comparison_result", {}).get("score", 0),
        "feedback": final_state.get("comparison_result", {}).get("feedback", "No feedback generated")
    }
}


    
    except Exception as e:
        logging.error(f"Error in /optimize_resume/: {e}")
        return {"status": "error", "message": str(e)}
