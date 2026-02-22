import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

load_dotenv()

# The 'google-gla:' prefix is the key to solving the 404 error
model = GeminiModel('google-gla:gemini-1.5-flash', api_key=os.getenv("GOOGLE_API_KEY"))

recruiter_agent = Agent(
    model,
    system_prompt=(
        "You are an expert recruitment researcher. Your job is to audit a candidate "
        "by comparing their resume against real-world data. Look for discrepancies "
        "in employment dates, skills, and company roles. Be professional but critical."
    ),
)

async def audit_candidate(name: str, role: str, resume_path: str):
    prompt = f"Audit the candidate {name} for the position of {role}. Resume file: {resume_path}"
    result = await recruiter_agent.run(prompt)
    return result.data