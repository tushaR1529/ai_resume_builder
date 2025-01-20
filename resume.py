import streamlit as st
import requests
from fpdf import FPDF

# Your Gemini API Key (replace with actual key)
api_key = 'your-gemini-api-key'

# API endpoint for generating resume content (this would vary based on your chosen API)
endpoint = "https://api.gemini.com/v1/generate_resume"

def generate_resume_content(data):
    """Send data to Gemini API to generate resume content"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.post(endpoint, json=data, headers=headers)
    return response.json()

def generate_pdf_resume(user_data, resume_content):
    """Generate a downloadable PDF resume"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"{user_data['name']} - Resume", ln=True, align='C')

    # Personal Information
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Email: {user_data['email']}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {user_data['phone']}", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Objective", ln=True)
    pdf.multi_cell(0, 10, txt=resume_content.get("objective", ""))
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Experience", ln=True)
    for exp in resume_content.get("experience", []):
        pdf.multi_cell(0, 10, txt=f"{exp['title']} at {exp['company']} ({exp['date_range']})\n{exp['description']}")
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Education", ln=True)
    for edu in resume_content.get("education", []):
        pdf.multi_cell(0, 10, txt=f"{edu['degree']} from {edu['school']} ({edu['graduation_year']})")
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Skills", ln=True)
    pdf.multi_cell(0, 10, txt=", ".join(resume_content.get("skills", [])))

    return pdf

# Streamlit UI
st.title("AI-Powered Resume Builder")

# Collecting user input
name = st.text_input("Full Name")
email = st.text_input("Email Address")
phone = st.text_input("Phone Number")

# Sections for user to fill out
skills = st.text_area("Skills (comma-separated)")
experience = st.text_area("Job Experience (comma-separated, e.g., job title, company, date range, description)")
education = st.text_area("Education (comma-separated, e.g., degree, school, graduation year)")

if st.button("Generate Resume"):
    # Prepare data to send to Gemini API
    resume_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills.split(","),
        "experience": [
            {"title": exp.split(",")[0], "company": exp.split(",")[1], "date_range": exp.split(",")[2], "description": exp.split(",")[3]}
            for exp in experience.split("\n") if exp
        ],
        "education": [
            {"degree": edu.split(",")[0], "school": edu.split(",")[1], "graduation_year": edu.split(",")[2]}
            for edu in education.split("\n") if edu
        ]
    }

    # Generate resume content using Gemini API
    resume_content = generate_resume_content(resume_data)
    
    if resume_content.get("success"):
        st.write("Your resume has been generated successfully!")

        # Show the resume content to the user
        st.subheader("Preview")
        st.write(f"Name: {name}")
        st.write(f"Email: {email}")
        st.write(f"Phone: {phone}")
        st.write("Skills:", ", ".join(resume_content.get("skills", [])))
        st.write("Experience:", "\n".join([f"{exp['title']} at {exp['company']}" for exp in resume_content.get("experience", [])]))
        st.write("Education:", "\n".join([f"{edu['degree']} from {edu['school']}" for edu in resume_content.get("education", [])]))

        # Generate and allow download of PDF
        pdf = generate_pdf_resume(resume_data, resume_content)
        pdf_output = pdf.output(dest='S').encode('latin1')
        st.download_button(label="Download Resume (PDF)", data=pdf_output, file_name="resume.pdf", mime="application/pdf")
    else:
        st.error("An error occurred while generating your resume.")
