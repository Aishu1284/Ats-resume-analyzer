from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from PyPDF2 import PdfReader
from google import genai

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
st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    padding-left:3rem;
    padding-right:3rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""

<h1 style='text-align:center; color:#4F8BF9;'>
🚀 ATS Resume Analyzer
</h1>

<h4 style='text-align:center; color:gray;'>
AI-Powered Resume Screening & Job Description Matching
</h4>

<p style='text-align:center; font-size:18px;'>
Upload your resume, paste a job description, and get an AI-powered ATS analysis in seconds.
</p>

<hr>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* Main App Background */
.stApp {
    background: #F5F7FB;
}

/* Text Area */
textarea {
    border-radius: 12px !important;
    border: 2px solid #D1D5DB !important;
    font-size: 16px !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #4F8BF9;
    border-radius: 15px;
    background: white;
    padding: 15px;
}

/* Success Message */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Green Buttons */
div.stButton > button {
    background-color: #16a34a;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 17px;
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Hover */
div.stButton > button:hover {
    background-color: #15803d;
    color: white;
}

/* Click */
div.stButton > button:active {
    background-color: #166534;
    color: white;
}

</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    with st.container():
        st.subheader("💼 Job Description")

        input_text = st.text_area(
            "",
            height=300,
            placeholder="Paste the complete job description here..."
        )
with col2:
    with st.container():
        st.subheader("📄 Upload Resume")

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
