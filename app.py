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
st.set_page_config(page_title="ATS Resume Expert")

st.header("ATS Resume Tracking System")

input_text = st.text_area(
    "Enter Job Description"
)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("Resume Uploaded Successfully")


# Buttons
submit1 = st.button("Resume Review")
submit2 = st.button("ATS Match")


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
