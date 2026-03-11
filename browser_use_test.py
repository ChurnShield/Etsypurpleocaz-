import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, BrowserProfile, BrowserSession
from browser_use.llm import ChatAnthropic

load_dotenv('/root/NEW-AI-PROJECT/.env')

async def main():
    profile = BrowserProfile(
        headless=True,
        user_data_dir='/root/NEW-AI-PROJECT/browser_profile',
        chromium_sandbox=False,
    )
    session = BrowserSession(browser_profile=profile)
    llm = ChatAnthropic(model='claude-sonnet-4-20250514')
    
    agent = Agent(
        task="Go to https://www.canva.com and describe the homepage layout and all visible UI elements in detail. Do NOT log in or click anything — just observe and describe what you see including navigation, buttons, hero section, featured content, and footer if visible.",
        llm=llm,
        browser_session=session
    )
    
    result = await agent.run()
    print("\n=== RESULT ===")
    print(result)

asyncio.run(main())
