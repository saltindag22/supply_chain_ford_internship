import asyncio
import os
import sys
from browser_use.llm import ChatGoogle
from browser_use import Agent
from dotenv import load_dotenv

load_dotenv()

async def main():
    if len(sys.argv) > 1:
        task_prompt = sys.argv[1]
    else:
        print("Uyarı: Komut satırı argümanı bulunamadı. Varsayılan test görevi kullanılıyor.", file=sys.stderr)
        task_prompt = "find company name and contact email for 3 alternative European suppliers of automotive grade steel"
    print(f"🤖 Browser Agent görevi başlattı: '{task_prompt}'")

    
    llm = ChatGoogle(model='gemini-1.5-flash') 
    
    extend_system_message = """
    - ALWAYS open first a new tab.
    - First, wait for autocomplete suggestions to appear.
    - If relevant suggestions are shown (e.g., contain location-specific or contextually enriched terms like "near me", "in Turkey"), **click the most appropriate suggestion** instead of pressing Enter.
    - If suggestions are not clickable or do not appear, **press Enter** to submit the query.
    - As a final fallback, click the “Google Search” button if it's available.
    - If a page serves you cookies to accept or reject, reject and continue.
    - If visible content is insufficient, perform scroll_down actions as needed.
    - Always consider scrolling if the current browser content does not contain relevant elements.
    - After scrolling, re-evaluate the updated elements before making further decisions.
    - If a page takes too long to load or remains blank, refresh the page once. If still inaccessible, skip to the next result.
    """
    message_context= """
        You are a web automation agent specialized in supplier research. 
        Your main goal is to find valid and professional suppliers for specific materials or services, typically requested in the task_prompt.
        You should extract:
        - The company name (preferably from the company website or business directory)
        - A contact email (preferably direct sales or info emails, not generic spammy ones)
        Skip irrelevant or suspicious-looking pages.
    """

    agent = Agent(
        task=task_prompt,
        llm=llm,
        extend_system_message=extend_system_message,
        message_context=message_context,
        max_steps=12,
        use_vision=True,
        generate_gif=True
    )
    result = await agent.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())