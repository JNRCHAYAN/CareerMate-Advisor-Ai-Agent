import os
import json
import asyncio
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled

# Load environment variables
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError("Please set BASE_URL, API_KEY, and MODEL_NAME.")

client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)

# --- Output Models ---
class SkillGapAnalysis(BaseModel):
    missing_skills: List[str]
    reason: str

class JobMatch(BaseModel):
    title: str
    company: str
    location: str
    match_reason: str

class CourseSuggestion(BaseModel):
    skill: str
    title: str
    platform: str
    link: str

# --- Tools ---
@function_tool
def get_missing_skills(user_skills: List[str], target_job: str) -> List[str]:
    job_skill_map = {
        "data scientist": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"],
        "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "data analyst": ["SQL", "Excel", "Data Visualization", "Python", "Statistics"],
    }
    required_skills = job_skill_map.get(target_job.lower(), [])
    return [skill for skill in required_skills if skill not in user_skills]

@function_tool
def find_jobs(user_skills: List[str], location: Optional[str] = None) -> List[dict]:
    dummy_jobs = [
        {"title": "Data Scientist", "company": "TechCorp", "location": "New York", "skills": ["Python", "SQL", "Machine Learning"]},
        {"title": "Web Developer", "company": "WebWorks", "location": "Remote", "skills": ["HTML", "CSS", "JavaScript"]},
        {"title": "Data Analyst", "company": "DataInc", "location": "Chicago", "skills": ["SQL", "Excel", "Python"]},
    ]
    matched = []
    for job in dummy_jobs:
        if all(skill in user_skills for skill in job["skills"]):
            if location is None or location.lower() in job["location"].lower():
                matched.append(job)
    return matched

@function_tool
def recommend_courses(missing_skills: List[str]) -> List[dict]:
    course_data = {
        "Python": [{"title": "Intro to Python", "platform": "Coursera", "link": "http://course.link/python"}],
        "SQL": [{"title": "SQL for Beginners", "platform": "Udemy", "link": "http://course.link/sql"}],
        "React": [{"title": "React Crash Course", "platform": "edX", "link": "http://course.link/react"}],
        "Machine Learning": [{"title": "ML Foundations", "platform": "Coursera", "link": "http://course.link/ml"}],
    }
    recommendations = []
    for skill in missing_skills:
        for course in course_data.get(skill, []):
            recommendations.append({"skill": skill, **course})
    return recommendations

# --- Specialist Agents ---
skill_gap_agent = Agent(
    name="Skill Gap Agent",
    handoff_description="Analyzes the user's skills vs. target job requirements",
    instructions="""
    You help identify missing skills for a desired job role based on the user's current skill set.
    Use get_missing_skills to compare and explain the results clearly.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_missing_skills],
    output_type=SkillGapAnalysis
)

job_finder_agent = Agent(
    name="Job Finder Agent",
    handoff_description="Finds job opportunities based on user skills and location",
    instructions="""
    You suggest jobs that match the user's current skills.
    Use find_jobs to pull matching job listings.
    Provide job details and explain why they fit.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[find_jobs],
    output_type=JobMatch
)

course_recommender_agent = Agent(
    name="Course Recommender Agent",
    handoff_description="Recommends courses to fill skill gaps",
    instructions="""
    You suggest online courses for skills the user needs to learn.
    Use recommend_courses to suggest resources.
    Include course name, platform, and link.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[recommend_courses],
    output_type=CourseSuggestion
)

# --- Conversation Agent ---
conversation_agent = Agent(
    name="CareerMate Controller",
    instructions="""
    You are a career assistant that helps users with job planning.
    Detect whether the user's request is about skill gaps, job search, or learning.
    Route the query to the correct specialist agent.

    Examples:
    - "I want to become a data analyst" → Skill Gap Agent
    - "What jobs can I apply for with React and JS?" → Job Finder Agent
    - "How do I learn SQL?" → Course Recommender Agent

    Show clear logs of which agent was used.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    handoffs=[skill_gap_agent, job_finder_agent, course_recommender_agent]
)

# --- Runner ---
async def main():
    queries = [
        "I want to be a data scientist but I only know Python and Excel",
        "What jobs can I get if I know HTML, CSS, and JavaScript?",
        "How do I learn React and Machine Learning?"
    ]

    for query in queries:
        print("\n" + "="*50)
        print(f"QUERY: {query}")

        result = await Runner.run(conversation_agent, query)

        print("\nFINAL RESPONSE:")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
