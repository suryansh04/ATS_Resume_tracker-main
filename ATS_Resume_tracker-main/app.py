import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
from constants import GOOGLE_API_KEY  # Import API key from constants file

# Configure Gemini AI
if not GOOGLE_API_KEY:
    st.error("Google API Key not found in constants.py")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error initializing Gemini model: {str(e)}")
    st.stop()

def get_gemini_response(user_input, pdf_content, prompt):
    try:
        # Combine the job description and prompt
        full_prompt = f"""
        Job Description: {user_input}
        
        {prompt}
        """
        
        # Generate response using the vision model
        response = model.generate_content([
            full_prompt,
            pdf_content[0],
        ])
        
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def input_pdf_setup(upload_file):
    try:
        images = pdf2image.convert_from_bytes(upload_file.read())
        first_page = images[0]
        
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

# Streamlit UI setup
st.set_page_config(page_title="ATS Resume Xpert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])

submit1 = st.button("Tell me about the resume")
submit2 = st.button("How can I improve my skills?")
submit3 = st.button("Percentage match")

input_prompt1 = """
"Analyze the uploaded resume and extract key information, including the candidate's skills, professional experience, education background, certifications, and notable achievements. Summarize this information in an organized and structured manner for a quick overview."
"""
input_prompt2 = """
"Review the resume to identify the candidate's current skills and qualifications. Based on this analysis, suggest areas where the candidate can improve, such as learning new skills, completing relevant certifications, gaining experience in a specific domain, or refining existing capabilities. Tailor the recommendations to align with common industry standards and the candidate's target role or career goals."
"""
input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. Provide the percentage of match if the resume matches
the job description. First, output the percentage match, followed by missing keywords, and finally, your overall thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt1)
            if response:
                st.subheader("The response is:")
                st.write(response)
    else:
        st.write("Please upload the file.")

elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt2)
            if response:
                st.subheader("The response is:")
                st.write(response)
    else:
        st.write("Please upload the file.")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_text, pdf_content, input_prompt3)
            if response:
                st.subheader("The response is:")
                st.write(response)
    else:
        st.write("Please upload the file.")