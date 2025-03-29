from fastapi import FastAPI, UploadFile, Form, File
import openai
import docx2txt
from dotenv import load_dotenv
import os

# Load API key from .env file (recommended for security)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# Create FastAPI instance
app = FastAPI()

@app.post("/optimize_resume/")
async def optimize_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    try:
        # Extract text from the uploaded resume (supports .docx files)
        resume_bytes = await resume.read()  # Read the file into memory
        with open("temp_resume.docx", "wb") as f:
            f.write(resume_bytes)  # Write it to a temp file

        resume_text = docx2txt.process("temp_resume.docx")  # Now process it

        
        # Construct the AI prompt
        prompt = f"""
    You are an expert resume writer. Rewrite the following resume so that it aligns with the job description while sounding natural and written by a human. 
    - Use **concise yet impactful bullet points**  
    - **Prioritize achievements over responsibilities**  
    - Use **action verbs** to describe accomplishments  
    - Ensure the resume is **ATS-friendly** but still readable  
    - Format it for a **one-page layout**  
    - Maintain a **professional but conversational** tone  
    - Make sure the resume follows a set order:  
    1️⃣ **Professional Experience** (Most recent job first)  
    2️⃣ **Education** (Include degree, university, and graduation year)  
    3️⃣ **Skills** (List technical & relevant soft skills)  
    - Return ONLY the json object with no additional explanations
    - Do not include extra formatting or markdowns in the response
    - ensure bullet points are short and impactful
    - Don't be verbose
    - Be very succeint in skills bullets (two to three words max). 
    - again I repeat, return ONLY the json object. not even a single character more.

    ### **Output Format Instructions**  
    Return the optimized resume in a structured JSON format like this:

        {{
    "name": "Full Name",
    "contact_info": "Email | Phone | Location",
    "experience": [
        {{
        "job_title": "Job Title",
        "company": "Company Name",
        "dates": "Start Date – End Date",
        "achievements": [
            "Achievement 1",
            "Achievement 2",
            "Achievement 3"
        ]
        }}
    ],
    "education": {{
        "university": "University"
        "degree": "Degree",
        "year": "Graduation Year"
    }},
    "skills": [
        "Skill 1",
        "Skill 2",
        "Skill 3"
    ]
    }}

        
        ### **Job Description:**
        {job_description}
        
        ### **Original Resume:**
        {resume_text}
        
        ### **Rewritten, Optimized Resume (make it human-like):**
        """
        
        # Call OpenAI API for resume rewriting
        from openai import OpenAI
        client = OpenAI(api_key = OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume optimizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000,
        )
        
        optimized_resume = response.choices[0].message.content
        return {"optimized_resume": optimized_resume}
    
    except Exception as e:
        return {"error": str(e)}
