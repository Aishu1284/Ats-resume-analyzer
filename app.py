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

col1, col2 = st.columns(2)
with col1:

    st.markdown("""
    <div class="section-card">
        <h2>💼 Job Description</h2>
        <p style="color:gray;">
        Paste the complete job description below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    input_text = st.text_area(
        "",
        height=300,
        placeholder="Paste the complete job description here..."
    )
with col2:

    st.markdown("""
    <div class="section-card">
        <h2>📄 Upload Resume</h2>
        <p style="color:gray;">
        Upload your resume in PDF format.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "",
        type=["pdf"]
    )

    if uploaded_file is not None:
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

Review the resume against the job description.

Provide:
1. Strengths
2. Weaknesses
3. Missing Skills
4. Final Evaluation
"""

prompt2 = """
You are an ATS scanner.

Compare the resume with the job description.

Return:
1. ATS Match Percentage
2. Missing Keywords
3. Skills Analysis
4. Final Thoughts
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

        st.subheader("Resume Review")
        st.write(response)

    else:
        st.error("Please upload a resume")


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

        st.subheader("ATS Match Result")
        st.write(response)

    else:
        st.error("Please upload a resume")
