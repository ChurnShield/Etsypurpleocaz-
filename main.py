from dotenv import load_dotenv
import os
import anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("ANTHROPIC_API_KEY not set in .env")
    raise SystemExit(1)

client = anthropic.Client(api_key=api_key)

prompt = "Write a short friendly greeting in English."
resp = client.completions.create(
    model="claude-2.1",
    prompt=anthropic.HUMAN_PROMPT + prompt + anthropic.AI_PROMPT,
    max_tokens_to_sample=200,
)
print(resp.completion)
