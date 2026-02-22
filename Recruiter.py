import streamlit as st
import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.common_tools.tavily import tavily_search_tool

# 1. Access keys from Streamlit Secrets
# This works for both Local and Cloud as long as the format is correct
try:
    gemini_key = st.secrets.get("GOOGLE_API_KEY")
    tavily_key = st.secrets.get("TAVILY_API_KEY")
except Exception:
    gemini_key = None
    tavily_key = None

# 2. Key Guard: Stop the app if keys are missing
if not gemini_key or not tavily_key:
    st.error("🚨 API Keys are missing! Go to Streamlit Settings > Secrets and ensure they are added correctly.")
    st.info("Format: GOOGLE_API_KEY = 'your_key' and TAVILY_API_KEY = 'your_key'")
    st.stop()

# 3. Initialize Model
model = GeminiModel('google-gla:gemini-1.5-flash', api_key=gemini_key)

# 4. Setup Agent with Tavily Tool
recruiter_agent = Agent(
    model,
    tools=[tavily_search_tool(api_key=tavily_key)],
    system_prompt=(
        "You are an expert recruitment researcher. Use the search tool to verify "
        "employment history, company details, and project claims. Be professional but critical."
    ),
)

async def audit_candidate(name: str, role: str, resume_path: str):
    prompt = f"Audit the candidate {name} for the position of {role}. Resume file: {resume_path}"
    result = await recruiter_agent.run(prompt)
    return result.data