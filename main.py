import re
from fastapi.staticfiles import StaticFiles
from starlette.routing import Request, Route
from starlette.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse


app = FastAPI()
templates = Jinja2Templates(directory="./templates")

resume_text = """
Jimmy Malhan
Tarzana, CA, 9135Led6
Python, Java, Node.js, Shell Terraform, Go
jimmymalhan999@gmail.com

Leadership and Accomplishments
Exhibited 15+ YOE in software architecture design, building microservices, & leading application modernization & infrastructure migration projects. Fostered strong relationships with up to 300,000 concurrent stakeholder’s connections.
Demonstrated 5 + years of experience in leadership experience by building, coaching, & managing teams of up to 10 members across retail & healthcare projects.

Experience
HealthJoy 		      Los Angeles, CA			Aug 2022 to Present
Engineering Manager Advisory at HealthJoy
Coached a team of 8 engineers in building, integrating, & managing backend, Full-stack, & mobile engineering projects.
Led and actively participated in architecting systems and conducting code reviews to scale systems while meeting user needs efficiently.
Pioneered and orchestrated the initiatives for MVP in 3 months for SDK and API using gRPC, swiftly implemented them into production, and fine-tuned them based on user feedback, surpassing all MVP goals.
Collaborated with cross-functional teams, including product managers, project managers, designers, security, compliance, and Go-to-Market teams, to execute the product roadmap, ensuring timely and successful product releases while anticipating and proactively resolving any potential launch delays.
Initiated a transformative process within the organization, actively establishing clear career paths for engineers and managers, and nurturing a culture of growth and development that propelled our team to unprecedented heights.

Skills: Leadership, Python, Node.js, Shell, Swift, Kotlin, CI/CD, Terraform, Kubernetes, Distributed Systems, OOP, SQL, NoSQL, Redis.

Amazon Web Services 		      Los Angeles, CA			Jan 2019 to Present
Engineering Manager II
Engineering Manager		
					  		                            
Coached a team of 10 engineers in building, integrating, & managing backend, platform, & mobile engineering projects.
Introduced an e-commerce platform for exclusive items on Amazon's retail website using a microservices architecture with Python, Java & Node.js, successfully overcoming disaster recovery challenges by RTO & RPO.
Established an ETL pipeline to streamline vendor integration, reducing onboarding time from 7 weeks to 2 weeks.
Scaled the e-commerce platform from handling 1 million requests per 10 minutes to 1 million requests per second year over year by using techniques such as load balancing & tools such as Kubernetes to improve performance.

Skills: Leadership, Python, Java, Node.js, Shell, CI/CD, Terraform, Kubernetes, Distributed Systems, OOP, SQL, NoSQL, Redis.

Skechers  			                  Los Angeles, CA		            Oct 2016 to Dec 2018 
Engineering Manager
Sr. Software Engineer 			 		
Led a team of 4 engineers in the leadership of retail POS systems on on-premises servers & in the AWS cloud for 100 retail stores nationwide, achieving 99.998% uptime.
Rolled out migration on transaction data to AWS using an asynchronous model & technologies such as Amazon Simple Queue Service (SQS), resulting in a 30% reduction in redundancy.
Successfully deployed a backend system for ACH transfers across 100 retail stores in the USA, overcoming challenges such as coordinating with multiple stakeholders & ensuring data security during the transition. 
Migrated the on-premises software architecture to AWS using a serverless architecture & databases such as Amazon RDS & Amazon DynamoDB to reduce maintenance costs.

Skills: Leadership, Python, Node.js, Shell, CI/CD, Kubernetes, Distributed Systems, OOP, SQL, NoSQL, Redis

Sarpanch International                           Ludhiana, Punjab                     Aug 2008 to Sep 2016 
Sr. Software Engineer
Software Engineer	
Software Engineer Intern						           	 		
Redesigned RESTful APIs in Django, resulting in a 25% increase in reporting speed for the internal analytics team. 
Applied software engineering best practices during the development of new features & enhancements, including code review & unit testing, resulting in improved user experience through faster loading times & increased stability.
Implemented agile methodology as a convincing scrum master during a 2-week sprint session, resulting in shorter development cycles by creating smaller, more manageable modules.
Skills: Python, Java, CI/CD, Distributed Systems, OOP, SQL, NoSQL

Education
AWS Solutions Architect Certiﬁed, 2020 
Master’s degree in Information Technology Management 
California Lutheran University, Thousand Oaks, CA 
Bachelor’s degree in Business Administration
Punjab College of Technical Education, Punjab, India
"""

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

# Mount the static files directory
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get('/')
async def index(request: Request):
    resume_details = extract_details(resume_text)
    return templates.TemplateResponse('index.html', {'request': request, 'resume': resume_details})

# @app.route('/', methods=['GET'])
# async def index(request: Request):
#     return templates.TemplateResponse('index.html', {'request': request, 'resume': resume_details})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)