
import os, sys, requests, openai
from dotenv import load_dotenv
load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python run_query.py <prompt_file>")
    sys.exit(1)

prompt_path = sys.argv[1]
with open(prompt_path, "r", encoding="utf-8") as f:
    user_prompt = f.read()

# Build a simple Google query from prompt lines for SerpAPI
query = " ".join([line.strip() for line in user_prompt.splitlines() if line.strip()])
params = {
    "q": query,
    "api_key": os.getenv("SERPAPI_API_KEY"),
    "engine": "google",
    "num": 10,
}
resp = requests.get("https://serpapi.com/search", params=params).json()

links = [r.get("link") for r in resp.get("organic_results", []) if r.get("link")]

openai.api_key = os.getenv("OPENAI_API_KEY")
messages = [
    {"role": "system", "content": "You are a precise research analyst. Summarize and filter results."},
    {"role": "user", "content": user_prompt + "\n\nLinks:\n" + "\n".join(links)}
]
answer = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, temperature=0.3)
print(answer.choices[0].message.content)
