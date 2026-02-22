import os
import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent

# Load keys from local .env OR Streamlit Cloud Secrets
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")

# Initialize the Agent
# Note: Using 'google-gla:gemini-1.5-flash' for 2026 stability
recruiter_agent = Agent(
    'google-gla:gemini-1.5-flash-latest',
    system_prompt=(
        "You are an elite technical recruiter and investigator. "
        "Your task is to verify a candidate's background by comparing their resume "
        "against their digital footprint. Highlight any discrepancies or impressive achievements."
    )
)

async def audit_candidate(name, role, pdf_path=None):
    """
    Core function to research a candidate and analyze their PDF.
    """
    prompt = f"Perform a deep-dive audit for {name} applying for the {role} role."
    content = [prompt]
    
    # 1. Add Resume Content if it exists
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            # Using BinaryContent for stable PydanticAI multimodal support
            content.append(BinaryContent(data=f.read(), media_type="application/pdf"))
    
    # 2. Add Web Search context (Assuming the agent has search tools enabled)
    # If using Tavily, you would typically define a tool here.
    
    result = await recruiter_agent.run(content)
    return result.data