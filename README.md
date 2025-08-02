
# 🔎 LLM-Dorking
Google‑style **dorking adapted for Large‑Language Models** (ChatGPT, Claude, etc.).  
This repo shows how to craft “LLM dorks” (structured prompts) that replicate `intext:`, `site:`, `filetype:` and other classic Google operators while leveraging an LLM’s reasoning + web search API.

---

## 1 · Why LLM Dorking?
Google dorking = precision hacking of search syntax.  
LLM dorking = precision hacking of **prompts** + **search API parameters** so the model:
1. issues the right web query (SerpAPI, Brave, Bing, etc.)  
2. post‑processes results, filters, summarizes, scores.

Result ⇒ faster OSINT, grant‑hunting, leak discovery, M&A scouting, etc.

---

## 2 · Operator Cheat‑Sheet

| Google Dork      | LLM Prompt Snippet                                              |
|------------------|-----------------------------------------------------------------|
| `intext:`        | “Find text that contains **<kw>** …”                            |
| `intitle:`       | “Only return pages whose **title** includes **<kw>** …”         |
| `inurl:`         | “Look for URLs containing **<kw>** …”                           |
| `site:`          | “Search **site:domain.com** and list …”                         |
| `filetype:`      | “Restrict to **PDF/DOC/XLS** files mentioning …”                |
| `before:/after:` | “Only include documents published **after 2024‑01‑01** …”       |
| `~word`          | “Include synonyms for **<word>** (configure, set, change) …”    |

Combine just like boolean logic:  
`(site:facebook.com | site:twitter.com) & intext:"login"`

---

## 3 · Quick Start

1. **Clone**  
   ```bash
   git clone https://github.com/youruser/llm-dorking.git
   cd llm-dorking
   ```

2. **Install deps** (Python 3.9+)  
   ```bash
   pip install openai serpapi python-dotenv
   ```

3. **Set keys** in `.env`  
   ```env
   OPENAI_API_KEY=sk-...
   SERPAPI_API_KEY=...
   ```

4. **Run**  
   ```bash
   python scripts/run_query.py prompts/grants.txt
   ```

---

## 4 · Prompt Library (`/prompts`)
Each file = a copy‑paste ready prompt.

| File                  | Goal                                        |
|-----------------------|---------------------------------------------|
| `security.txt`        | Find exposed API keys & configs             |
| `grants.txt`          | Hunt Spanish & EU startup subsidies         |
| `mna_targets.txt`     | Detect distressed companies (buyout leads)  |
| `wildcard_dirs.txt`   | List “index of /” open directories          |

### Example – `prompts/grants.txt`
```
Act as an OSINT research bot.  
Search only on site:gva.es, site:boe.es, site:europa.eu  
for PDF or DOC files containing:
  - "subvención autónomos"
  - "startup ayuda"
Published after 2023‑01‑01.  
Return table:
  {title} | {publish_date} | {summary} | {download_link}
```

---

## 5 · Minimal Runner (`/scripts/run_query.py`)
<details><summary>Click to view code</summary>

```python
import os, sys, requests, openai
from dotenv import load_dotenv
load_dotenv()

prompt_path = sys.argv[1]
with open(prompt_path, "r", encoding="utf-8") as f:
    user_prompt = f.read()

# 1) Hit SerpAPI (swap for your search engine of choice)
params = {
    "q": " ".join([l.strip() for l in user_prompt.splitlines() if l]),
    "api_key": os.getenv("SERPAPI_API_KEY"),
    "engine": "google",
    "num": 10,
}
search_json = requests.get("https://serpapi.com/search", params=params).json()
links = [r["link"] for r in search_json.get("organic_results", [])]

# 2) Feed into GPT with context
openai.api_key = os.getenv("OPENAI_API_KEY")
system_msg = "You are a precise research analyst. Summarize and filter results."
content = user_prompt + "\n\nLinks:\n" + "\n".join(links)
resp = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": system_msg},
              {"role": "user", "content": content}],
    temperature=0.3,
)
print(resp.choices[0].message.content)
```
</details>

---

## 6 · Advanced Usage Ideas
- **n8n**: schedule recurring dorks → dump CSV → email daily digest.  
- **Langchain Agents**: auto‑loop keywords, push to Qdrant.  
- **Alerting**: Slack when new leak appears (`before:/after:` rolling window).  
- **Micro‑M&A Bot**: scrape local news for “se vende empresa”, feed GPT for valuation hints.

---

## 7 · More Example Prompts

<details>
<summary>OSINT / Credential Leak</summary>

```
Search pastebin.com AND github.com
for files containing any of:
  - "AWS_SECRET_ACCESS_KEY"
  - "DB_PASSWORD"
  - "api_key"
Return source_link | exposed_fragment | risk_assessment (high/med/low)
```
</details>

<details>
<summary>Distressed‑Company Radar (Spain‑Only, 2024‑→)</summary>

```
Search Spanish press releases, BORME filings, and blogs
for phrases:
  - "concurso de acreedores"  (bankruptcy filing)
  - "busca comprador"         (looking for buyer)
  - "reestructuración financiera"
Time filter: after 2024‑01‑01
Return table: Company | Context | Date | Link
```
</details>

<details>
<summary>Wildcard Directory Listing</summary>

```
Find open directories exposing media:
Query: ("index of /" | "parent directory") (mp3 | mp4 | flac | pdf)
Exclude: -html -php -jsp -cf -shtml
Return 10 freshest URLs + guess content type.
```
</details>

---

## 8 · License
MIT. Hack responsibly.

---

## 9 · Credits
Inspired by sundowndev’s google‑dorks‑cheatsheet.  
LLM adaptation by **Ozgur Ozdemircili** & contributors.
