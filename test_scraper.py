import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    print("🌐 Initializing Test Scraper...")
    async with AsyncWebCrawler() as crawler:
        # We'll test it on a high-quality site like NBC News or a portfolio
        url = "https://www.nbcnews.com/business"
        print(f"🕵️ Attempting to scrape: {url}")
        
        result = await crawler.arun(url=url)
        
        if result.success:
            print("\n✅ SCRAPE SUCCESS!")
            print(f"📊 Characters captured: {len(result.markdown)}")
            print("-" * 30)
            print("📄 PREVIEW OF DATA:")
            print(result.markdown[:500]) # Show the first 500 chars
            print("-" * 30)
        else:
            print(f"❌ SCRAPE FAILED: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())