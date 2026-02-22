import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryPart
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from tavily import TavilyClient
from crawl4ai import AsyncWebCrawler

load_dotenv()

# 1. Structured Output
class CandidateReport(BaseModel):
    candidate_name: str
    relevance_score: int = Field(description="1-10 score on role fit")
    key_findings: list[str] = Field(description="Top 3 verified facts")
    resume_discrepancies: list[str] = Field(description="Claims in PDF that don't match web data")
    summary: str

# 2. Provider & Model (using the stable 2026 preview)
provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY"))
model = GoogleModel('gemini-3-flash-preview', provider=provider)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 3. The Agent with Multi-Tool & Multimodal Instructions
recruiter_agent = Agent(
    model,
    output_type=CandidateReport,
    system_prompt=(
        "You are a Senior Technical Recruiter. "
        "You will be given a candidate's name, role, and a PDF Resume. "
        "STEP 1: Use 'search_web' to find their online presence. "
        "STEP 2: Use 'scrape_website' to verify specific claims from their resume. "
        "STEP 3: Compare the PDF content with what you found online and report gaps."
    )
)

@recruiter_agent.tool_plain
async def search_web(name: str, role: str) -> str:
    """Find URLs for a candidate."""
    print(f"🔍 Searching Web: {name}...")
    return str(tavily.search(query=f"{name} {role} professional history", search_depth="advanced"))

@recruiter_agent.tool_plain
async def scrape_website(url: str) -> str:
    """Deep-read a specific site (GitHub, Portfolio)."""
    print(f"📖 Scraping: {url}...")
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown[:5000]

# 4. Resilient Processing with Retry Logic
async def process_candidate(name: str, role: str, resume_path: str):
    print(f"🚀 Processing: {name}")
    
    # Read PDF as Binary
    try:
        with open(resume_path, "rb") as f:
            pdf_bytes = f.read()
    except FileNotFoundError:
        print(f"⚠️ Resume not found for {name}. Skipping PDF analysis.")
        pdf_bytes = None

    # Retry loop for 503/429 errors
    for attempt in range(3):
        try:
            prompt = [f"Research {name} for {role} and compare with this resume."]
            if pdf_bytes:
                prompt.append(BinaryPart(data=pdf_bytes, mime_type="application/pdf"))
            
            result = await recruiter_agent.run(prompt)
            return result.output.model_dump()
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                wait = (attempt + 1) * 10
                print(f"⏳ Server busy. Retrying {name} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"❌ Error: {e}")
                break
    return {"candidate_name": name, "summary": "Failed after retries", "relevance_score": 0}

async def main():
    # Load your list
    df = pd.read_csv("candidates.csv") # Must have 'name', 'role', 'resume_file' columns
    
    tasks = [
        process_candidate(row['name'], row['role'], row.get('resume_file', 'resume.pdf')) 
        for _, row in df.iterrows()
    ]
    
    print(f"⚙️ Starting Batch Analysis...")
    results = await asyncio.gather(*tasks)
    
    # Save to CSV
    pd.DataFrame(results).to_csv("final_recruitment_audit.csv", index=False)
    print("\n✅ Final Audit Complete: final_recruitment_audit.csv")

if __name__ == "__main__":
    asyncio.run(main())