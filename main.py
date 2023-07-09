import re
import psycopg2
from fastapi.staticfiles import StaticFiles, FastAPI, Request
from fastapi.responses import FileResponse
from starlette.routing import Request, Route
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="./templates")

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


def get_resume_text():
    try:
        conn = psycopg2.connect(
            host="DB_HOST",
            database="DB_NAME",
            user="DB_USER",
            password="DB_PASSWORD"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT resume_text FROM resume_table WHERE id = 1")
        resume_text = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return resume_text
    except (psycopg2.Error, Exception) as e:
        print(f"Error retrieving resume text from the database: {e}")
        return None


@app.get('/')
async def index(request: Request):
    resume_text = get_resume_text()
    if resume_text is not None:
        resume_details = extract_details(resume_text)
        return templates.TemplateResponse('index.html', {'request': request, 'resume': resume_details})
    else:
        return {"message": "Failed to retrieve resume details. Please try again later."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
