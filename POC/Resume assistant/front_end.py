import streamlit as st
import requests

# Page config
st.set_page_config(page_title="Resume Assistant Project", layout="wide")

# Header
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'> Resume Assistant</h1>", unsafe_allow_html=True)
st.caption("Built with Streamlit Framework by Nimmy and Abdus")

# Toggle input mode
use_url = st.toggle("🔄 Switch to URL input", value=False)

# Form
with st.form("resume_form", clear_on_submit=False):
    st.markdown("### 📄 Upload Resume")
    resume_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

    st.markdown("### Job Description")
    if not use_url:
        jd_text = st.text_area("✍️ Paste Job Description Text", height=120)
    else:
        jd_url = st.text_input("🔗 Provide Job Description URL", placeholder="https://example.com/job-posting")
        jd_text = jd_url

    submitted = st.form_submit_button("🔍 Analyze Resume", use_container_width=True)

# Handle submission
if submitted:
    if not resume_file:
        st.error("⚠️ Please upload a resume file")
    elif not jd_text.strip():
        st.error("⚠️ Please provide a job description")
    else:
        with st.spinner("Processing, please wait a min you will see result..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/optimize_resume/",
                    files={"resume": (resume_file.name, resume_file, resume_file.type)},
                    data={
                        "job_description": jd_text if not use_url else "",
                        "job_url": jd_text if use_url else ""
                    }
                )

                if response.status_code == 200:
                    result = response.json()

                    if result.get("status") == "success" and "data" in result:
                        data = result["data"]

                        # 🎯 Overall Score + Feedback
                        st.markdown("## 🎯 Overall Resume Score")
                        st.progress(data["score"] / 100)
                        st.success(f"**Score:** {data['score']} / 100")
                        st.info(f"💬 Feedback: {data['feedback']}")

                        # 🛠 Skills Missing
                        st.markdown("## 🛠 Skills Missing")
                        if data.get("skills_missing"):
                            st.warning("\n".join([f"- {skill}" for skill in data["skills_missing"]]))
                        else:
                            st.success("✅ No major skills missing")

                        # 📉 Experience Gaps
                        st.markdown("## 📉 Experience Gaps")
                        if data.get("experience_gap"):
                            st.warning("\n".join([f"- {gap}" for gap in data["experience_gap"]]))
                        else:
                            st.success("✅ No major experience gaps")

                        # ✨ Suggestions
                        st.markdown("## ✨ Suggestions for Improvement")
                        if data.get("suggestions"):
                            st.info("\n".join([f"- {suggestion}" for suggestion in data["suggestions"]]))
                        else:
                            st.success("✅ No additional suggestions")

                    else:
                        st.error(f"Backend Error: {result.get('message', 'Unknown error')}")
                else:
                    st.error(f"Backend HTTP Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"⚠️ Request failed: {e}")
