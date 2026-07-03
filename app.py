import json
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PyPDF2 import PdfReader
from google import genai

def load_css():
    with open("style/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configure Gemini Client
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])


# -----------------------------
# Gemini Response Function
# -----------------------------
def get_gemini_response(job_description, resume_text, prompt):

    full_prompt = f"""
    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Prompt:
    {prompt}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )

    return response.text


# -----------------------------
# Extract Text From PDF
# -----------------------------
def extract_text_from_pdf(uploaded_file):

    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:

        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text

    return text

def display_result(title, response):

    st.markdown(f"## {title}")

    with st.container(border=True):
        st.markdown(response)

# ATS Score Gauge
# -----------------------------
def show_ats_score(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,

        title={"text": "ATS Score"},

        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#16A34A"},
            "steps": [
                {"range": [0, 40], "color": "#FEE2E2"},
                {"range": [40, 70], "color": "#FEF3C7"},
                {"range": [70, 100], "color": "#DCFCE7"}
            ]
        }
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)



# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css()

st.markdown("""
<div style="
background: linear-gradient(135deg,#4F8BF9,#7C4DFF);
padding:45px;
border-radius:20px;
text-align:center;
color:white;
margin-bottom:35px;
box-shadow:0px 8px 25px rgba(0,0,0,0.15);
">

<h1 style="margin-bottom:10px;font-size:48px;">
🚀 ATS Resume Analyzer
</h1>

<h3 style="margin-top:0;">
AI-Powered Resume Screening & Job Description Matching
</h3>

<p style="font-size:18px;">
Upload your resume, compare it with a job description,
and receive an AI-powered ATS report within seconds.
</p>

</div>
""", unsafe_allow_html=True)


col1, col2 = st.columns([1.4, 1], gap="large")

# ==========================
# Job Description
# ==========================
with col1:
    with st.container(border=True):

        st.subheader("💼 Job Description")
        st.caption("Paste the complete job description below.")

        input_text = st.text_area(
            label="",
            height=320,
            placeholder="Paste the complete job description here..."
        )

# ==========================
# Upload Resume
# ==========================
with col2:
    with st.container(border=True):

        st.subheader("📄 Upload Resume")
        st.caption("Upload your resume in PDF format.")

        uploaded_file = st.file_uploader(
            label="Choose Resume",
            type=["pdf"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            st.success("✅ Resume Uploaded Successfully")
# Buttons
st.markdown("<br>", unsafe_allow_html=True)

btn1, btn2 = st.columns(2)

with btn1:
    submit1 = st.button("📝 Resume Review", use_container_width=True)

with btn2:
    submit2 = st.button("🎯 ATS Match", use_container_width=True)

# Prompts
prompt1 = """
You are an experienced HR Manager.

Analyze the resume professionally.

Return ONLY valid JSON.

{
    "summary":"Short professional summary",
    "strengths":[
        "Strength 1",
        "Strength 2",
        "Strength 3"
    ],
    "weaknesses":[
        "Weakness 1",
        "Weakness 2"
    ],
    "missing_skills":[
        "Skill 1",
        "Skill 2"
    ],
    "suggestions":[
        "Suggestion 1",
        "Suggestion 2",
        "Suggestion 3"
    ],
    "final_evaluation":"Final HR evaluation."
}

Return only JSON.
Do not use markdown.
Do not add explanations.
"""
prompt2 = """
You are an expert ATS Resume Analyzer.

Analyze the resume against the job description.

Return ONLY valid JSON.

{
  "ats_score": 88,
  "summary": "Short summary",
  "strengths": [
    "Strong Python",
    "Good Projects",
    "Good Education"
  ],
  "missing_keywords": [
    "Docker",
    "AWS",
    "CI/CD"
  ],
  "suggestions": [
    "Add Docker project",
    "Mention quantified achievements",
    "Improve technical keywords"
  ],
  "final_verdict": "Good match for this role."
}

Return only JSON.
Do not include markdown.
Do not include explanation.
"""

# -----------------------------
# Resume Review
# -----------------------------
if submit1:

    if uploaded_file is not None:

        with st.spinner("Analyzing Resume..."):

            resume_text = extract_text_from_pdf(uploaded_file)

            response = get_gemini_response(
                input_text,
                resume_text,
                prompt1
            )

        try:

            clean_response = (
                response.replace("```json", "")
                        .replace("```", "")
                        .strip()
            )

            result = json.loads(clean_response)

            st.success(result["summary"])

            col1, col2 = st.columns(2)

            # Left Column
            with col1:

                st.subheader("✅ Strengths")

                for strength in result["strengths"]:
                    st.success(strength)

                st.subheader("❌ Weaknesses")

                for weakness in result["weaknesses"]:
                    st.error(weakness)

            # Right Column
            with col2:

                st.subheader("📌 Missing Skills")

                for skill in result["missing_skills"]:
                    st.warning(skill)

                st.subheader("💡 Suggestions")

                for suggestion in result["suggestions"]:
                    st.info(suggestion)

            st.markdown("### ⭐ Final Evaluation")
            st.success(result["final_evaluation"])

        except Exception:

            st.error("Unable to parse Gemini response.")

            st.code(response)

    else:
        st.error("Please upload a resume.")


# -----------------------------
# ATS Match
# -----------------------------
if submit2:

    if uploaded_file is not None:

        with st.spinner("Calculating ATS Match..."):

            resume_text = extract_text_from_pdf(uploaded_file)

            response = get_gemini_response(
                input_text,
                resume_text,
                prompt2
            )

        try:
            # Clean Gemini response
            clean_response = (
                response.replace("```json", "")
                        .replace("```", "")
                        .strip()
            )

            # Convert JSON string to Python dictionary
            result = json.loads(clean_response)

            # Show ATS Gauge
            show_ats_score(result["ats_score"])

            # Summary
            st.success(result["summary"])

            # Create two columns
            col1, col2 = st.columns(2)

            # Left Column
            with col1:

                st.subheader("✅ Strengths")

                for strength in result["strengths"]:
                    st.success(strength)

                st.subheader("💡 Suggestions")

                for suggestion in result["suggestions"]:
                    st.info(suggestion)

            # Right Column
            with col2:

                st.subheader("❌ Missing Keywords")

                for keyword in result["missing_keywords"]:
                    st.error(keyword)

                st.subheader("📌 Final Verdict")

                st.warning(result["final_verdict"])

        except Exception as e:

            st.error("Unable to parse Gemini response.")

            st.code(response)

    else:
        st.error("Please upload a resume.")
