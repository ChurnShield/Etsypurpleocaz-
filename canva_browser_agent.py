import asyncio
from browser_use import Agent
from langchain_anthropic import ChatAnthropic

async def swap_canva_design(design_url, new_image_path):
    agent = Agent(
        task=f"Go to {design_url}, log in to Canva using Google, find the main image element and replace it with the image at {new_image_path}, then download the design as PNG",
        llm=ChatAnthropic(model="claude-sonnet-4-5"),
    )
    result = await agent.run()
    return result

asyncio.run(swap_canva_design(
    "https://www.canva.com/design/DAHD07F9MsY/edit",
    "/root/NEW-AI-PROJECT/outputs/tattoo-forms-v2/hero.png"
))
