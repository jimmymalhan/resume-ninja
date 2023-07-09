import re
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="./templates"), name="static")
templates = Jinja2Templates(directory="./templates")

# Create connection to SQLite database
conn = sqlite3.connect('resume.db')

# Create table if not exists
conn.execute('''
    CREATE TABLE IF NOT EXISTS resume_table (
        id INTEGER PRIMARY KEY,
        resume_text TEXT
    )
''')

def extract_details(resume_text):
    details = {}

    # Extract name and LinkedIn URL
    name_regex = r"^(.*)\n"
    linkedin_regex = r"linkedin\.com/in/(\S+)"
    name_match = re.search(name_regex, resume_text, re.MULTILINE)
    linkedin_match = re.search(linkedin_regex, resume_text, re.MULTILINE)
    if name_match:
        details['name'] = name_match.group(1)
    if linkedin_match:
        details['linkedin'] = "https://www.linkedin.com/in/" + linkedin_match.group(1)

    # Extract skills
    skills_regex = r"Skills: (.+)"
    skills_match = re.search(skills_regex, resume_text, re.MULTILINE)
    if skills_match:
        details['skills'] = [skill.strip() for skill in skills_match.group(1).split(",")]

    # Extract leadership and accomplishments
    accomplishments_regex = r"Leadership and Accomplishments\n(.+?)\n\n"
    accomplishments_match = re.search(accomplishments_regex, resume_text, re.DOTALL)
    if accomplishments_match:
        details['accomplishments'] = [accomplishment.strip() for accomplishment in accomplishments_match.group(1).split("\n•")]

    # Extract experience
    experience_regex = r"Experience\n(.*?)\n\n"
    experience_matches = re.finditer(experience_regex, resume_text, re.DOTALL)
    details['experience'] = []
    for match in experience_matches:
        experience = {}
        lines = match.group(1).split("\n")
        experience['company'] = lines[0]
        experience['location'] = lines[1]
        experience['duration'] = lines[2]
        experience['position'] = lines[3]
        experience['responsibilities'] = [responsibility.strip() for responsibility in lines[4:]]
        details['experience'].append(experience)

    # Extract education
    education_regex = r"Education\n(.*?)(?=\n{2}|\n\w)"
    education_match = re.search(education_regex, resume_text, re.DOTALL)
    if education_match:
        education_lines = education_match.group(1).split("\n")
        details['education'] = {}

        for line in education_lines:
            line = line.strip()
            if line.startswith("AWS Solutions Architect Certi"):
                details['education']['certification'] = line
            elif line.startswith("Master’s degree"):
                details['education']['master_degree'] = line
            elif line.startswith("Bachelor’s degree"):
                details['education']['bachelor_degree'] = line
            else:
                details['education']['college'] = line

    return details


def save_resume_text(resume_text):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO resume_table (resume_text) VALUES (?)", (resume_text,))
        conn.commit()
        cursor.close()
        return True
    except (sqlite3.Error, Exception) as e:
        print(f"Error saving resume text to the database: {e}")
        return False


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/submit')
async def submit_resume(request: Request):
    form_data = await request.form()
    resume_text = form_data.get('resume_text')
    if resume_text:
        if save_resume_text(resume_text):
            return {"message": "Resume details submitted successfully!"}
        else:
            return {"message": "Failed to submit resume details. Please try again later."}
    else:
        return {"message": "Invalid request. Please provide resume text."}

# Close the connection to the SQLite database when the application shuts down
@app.on_event("shutdown")
def shutdown_event():
    conn.close()
