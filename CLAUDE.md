# CLAUDE.md — Gulf SWF Filing Intelligence Agent
## Web Data UNLOCKED Hackathon | Bright Data × lablab.ai | May 2026

---

## PROJECT OVERVIEW

Build a production-ready AI agent that monitors SEC EDGAR 13D/13G filings from five
major Gulf Sovereign Wealth Funds (SWFs) in real-time. The agent uses Bright Data's
MCP Server to bypass EDGAR's rate limits and bot detection, stores structured filing
data in MongoDB Atlas, generates institutional-grade investment intelligence via
Gemini 2.0 Flash, and displays everything on a live Next.js/Vercel dashboard.

**Hackathon Track:** Track 2 — Finance & Market Intelligence
**Submission Deadline:** May 30, 2026, 10:00 PM Pakistan Standard Time
**Solo Participant:** Zulfiqar Ali Mir, Black Iron Quantum AI (Private) Limited

---

## THE PROBLEM THIS SOLVES

Gulf SWFs — ADIA, PIF, QIA, Mubadala, ADQ — manage over $4 trillion in assets.
When they file SC 13D/13G with the SEC, it signals a major investment move.
But SEC EDGAR rate-limits scrapers (max 10 req/sec per IP), blocks bots, and
returns stale cached data. AI agents trying to monitor these filings hit the wall.

**Bright Data MCP unlocks this:** bypasses rate limits, solves CAPTCHAs, rotates
IPs automatically — making real-time SWF filing intelligence possible for the
first time without enterprise data vendor subscriptions.

---

## TECH STACK

| Layer | Technology |
|---|---|
| Web Scraping | Bright Data MCP Server (SSE) |
| AI Agent Framework | LangChain + LangGraph |
| LLM | Google Gemini 2.0 Flash |
| Database | MongoDB Atlas |
| Backend API | Python FastAPI |
| Frontend | Next.js 14 + Tailwind CSS |
| Deployment | Vercel (frontend) + local Python agent |
| Language | Python 3.11 (backend), TypeScript (frontend) |

---

## ENVIRONMENT VARIABLES

Create a `.env` file in the project root with these values:

```env
# Bright Data
BRIGHT_DATA_MCP_URL=https://mcp.brightdata.com/sse?token=<YOUR_BRIGHT_DATA_TOKEN>&groups=advanced_scraping
BRIGHT_DATA_API_TOKEN=<YOUR_BRIGHT_DATA_TOKEN>

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# MongoDB Atlas
MONGODB_URI=your_mongodb_atlas_connection_string_here
MONGODB_DB=gulf_swf_agent

# App
PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## PROJECT STRUCTURE

Build this exact folder structure:

```
gulf-swf-agent/
├── CLAUDE.md                    # This file
├── .env                         # Environment variables (never commit)
├── .gitignore                   # Include .env, __pycache__, node_modules
├── README.md                    # Project description for judges
├── requirements.txt             # Python dependencies
│
├── agent/                       # Python AI Agent
│   ├── __init__.py
│   ├── main.py                  # Entry point — runs the agent loop
│   ├── edgar_scraper.py         # Bright Data MCP scraping logic
│   ├── filing_parser.py         # Parse SC 13D/13G filing content
│   ├── intelligence.py          # Gemini analysis layer
│   ├── database.py              # MongoDB Atlas operations
│   └── swf_config.py            # SWF CIK numbers and metadata
│
├── api/                         # FastAPI backend
│   ├── __init__.py
│   └── server.py                # REST endpoints for dashboard
│
└── dashboard/                   # Next.js frontend
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    └── app/
        ├── page.tsx             # Main dashboard page
        ├── layout.tsx
        └── components/
            ├── FilingsTable.tsx  # Latest filings table
            ├── SWFCard.tsx       # Per-SWF activity card
            └── IntelCard.tsx     # Gemini intelligence card
```

---

## FILE 1: requirements.txt

```
langchain>=0.2.0
langchain-google-genai>=1.0.0
langgraph>=0.1.0
langchain-mcp-adapters>=0.1.0
pymongo>=4.6.0
fastapi>=0.110.0
uvicorn>=0.27.0
python-dotenv>=1.0.0
httpx>=0.27.0
beautifulsoup4>=4.12.0
mcp>=1.0.0
```

---

## FILE 2: agent/swf_config.py

Define the five Gulf SWFs with their SEC EDGAR CIK numbers:

```python
SWF_CONFIG = {
    "ADIA": {
        "name": "Abu Dhabi Investment Authority",
        "cik": "0001496957",
        "country": "UAE",
        "aum_trillion": 1.1,
        "emoji": "🇦🇪"
    },
    "PIF": {
        "name": "Public Investment Fund (Saudi Arabia)",
        "cik": "0001619212",
        "country": "Saudi Arabia",
        "aum_trillion": 0.9,
        "emoji": "🇸🇦"
    },
    "QIA": {
        "name": "Qatar Investment Authority",
        "cik": "0001346980",
        "country": "Qatar",
        "aum_trillion": 0.5,
        "emoji": "🇶🇦"
    },
    "Mubadala": {
        "name": "Mubadala Investment Company",
        "cik": "0001401966",
        "country": "UAE",
        "aum_trillion": 0.3,
        "emoji": "🇦🇪"
    },
    "ADQ": {
        "name": "Abu Dhabi Developmental Holding Company",
        "cik": "0001831868",
        "country": "UAE",
        "aum_trillion": 0.2,
        "emoji": "🇦🇪"
    }
}

EDGAR_BASE_URL = "https://www.sec.gov"
FILING_TYPES = ["SC 13D", "SC 13G", "SC 13G/A", "SC 13D/A"]
```

---

## FILE 3: agent/edgar_scraper.py

Use Bright Data MCP to scrape SEC EDGAR. Use the SSE MCP URL from .env.

```python
"""
EDGAR scraper using Bright Data MCP Server.
Uses 'scrape_as_markdown' tool to fetch EDGAR pages without being blocked.
"""

import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MCP_URL = os.getenv("BRIGHT_DATA_MCP_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


async def scrape_edgar_filings(cik: str, swf_name: str) -> str:
    """
    Use Bright Data MCP to fetch EDGAR filings page for a given CIK.
    Returns markdown content of the filings page.
    """
    edgar_url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar"
        f"?action=getcompany&CIK={cik}&type=SC+13"
        f"&dateb=&owner=include&count=10&search_text="
    )

    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # Use scrape_as_markdown tool from Bright Data MCP
            scrape_tool = next(
                (t for t in tools if "scrape" in t.name.lower()), None
            )

            if not scrape_tool:
                raise ValueError("Bright Data scrape tool not found in MCP tools")

            model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=GEMINI_API_KEY
            )

            agent = create_react_agent(model, tools)

            result = await agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Use the scrape_as_markdown tool to fetch this URL and "
                        f"return the full page content: {edgar_url}"
                    )
                }]
            })

            return result["messages"][-1].content


async def get_filing_document(filing_url: str) -> str:
    """
    Fetch a specific filing document using Bright Data MCP.
    """
    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=GEMINI_API_KEY
            )

            agent = create_react_agent(model, tools)

            result = await agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Use the scrape_as_markdown tool to fetch this SEC filing "
                        f"document and return its full content: {filing_url}"
                    )
                }]
            })

            return result["messages"][-1].content
```

---

## FILE 4: agent/filing_parser.py

Parse the markdown content returned by Bright Data MCP to extract structured
filing data. Use Python string parsing and regex — no external HTML parser needed
since Bright Data already returns clean markdown.

Extract these fields from each filing:
- `filing_date` (string, format: YYYY-MM-DD)
- `filing_type` (string: "SC 13D", "SC 13G", etc.)
- `company_name` (string: the company the SWF invested in)
- `company_ticker` (string or None)
- `shares_owned` (integer or None)
- `ownership_percent` (float or None)
- `filing_url` (string: full SEC URL to the filing document)
- `swf_name` (string: which SWF filed this)
- `swf_cik` (string)

Return a list of dicts, one per filing found on the page.
Handle cases where fields are missing gracefully — use None.

---

## FILE 5: agent/intelligence.py

Use Gemini 2.0 Flash to generate investment intelligence from each parsed filing.

```python
"""
Gemini intelligence layer — generates institutional-grade analysis
from parsed SEC filing data.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)


def generate_filing_intelligence(filing: dict) -> dict:
    """
    Takes a parsed filing dict and returns enriched intelligence.
    """
    prompt = f"""
You are an institutional investment analyst specializing in Sovereign Wealth Fund activity.

Analyze this SEC filing and provide structured intelligence:

Filing Data:
- SWF: {filing.get('swf_name')}
- Filing Type: {filing.get('filing_type')}
- Target Company: {filing.get('company_name')}
- Ticker: {filing.get('company_ticker', 'Unknown')}
- Shares Owned: {filing.get('shares_owned', 'Unknown')}
- Ownership %: {filing.get('ownership_percent', 'Unknown')}%
- Filing Date: {filing.get('filing_date')}

Provide a JSON response with these exact fields:
{{
  "signal": "BULLISH" | "BEARISH" | "NEUTRAL",
  "action": "NEW_POSITION" | "INCREASE" | "DECREASE" | "EXIT" | "MAINTAIN",
  "sector": "the industry sector of the target company",
  "summary": "2-3 sentence institutional-grade analysis of what this filing means",
  "significance": "HIGH" | "MEDIUM" | "LOW",
  "key_insight": "one sentence — the single most important takeaway for investors"
}}

Return ONLY valid JSON. No markdown, no explanation.
"""

    response = llm.invoke(prompt)

    import json
    try:
        intelligence = json.loads(response.content)
    except Exception:
        intelligence = {
            "signal": "NEUTRAL",
            "action": "MAINTAIN",
            "sector": "Unknown",
            "summary": response.content[:300],
            "significance": "LOW",
            "key_insight": "Unable to parse structured intelligence."
        }

    return {**filing, **intelligence}
```

---

## FILE 6: agent/database.py

MongoDB Atlas operations. Collection name: `filings`.

Implement these functions:

```python
def save_filing(filing: dict) -> str:
    """Save a filing to MongoDB. Return inserted_id as string."""

def get_latest_filings(limit: int = 20) -> list:
    """Return latest N filings sorted by filing_date descending."""

def get_filings_by_swf(swf_name: str, limit: int = 10) -> list:
    """Return filings for a specific SWF."""

def filing_exists(filing_url: str) -> bool:
    """Check if a filing URL already exists in DB to avoid duplicates."""

def get_swf_summary() -> list:
    """Return summary stats per SWF — count of filings, latest date."""
```

Use `pymongo` with the `MONGODB_URI` from `.env`.
Add a unique index on `filing_url` to prevent duplicates.
Convert MongoDB `_id` ObjectId to string when returning data.

---

## FILE 7: agent/main.py

Main agent loop. This is what runs the monitoring agent.

```python
"""
Main agent loop — monitors all 5 Gulf SWFs for new SEC filings.
Run this script to start the monitoring agent.
"""

import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

from swf_config import SWF_CONFIG
from edgar_scraper import scrape_edgar_filings
from filing_parser import parse_filings_from_markdown
from intelligence import generate_filing_intelligence
from database import save_filing, filing_exists, get_latest_filings

load_dotenv()


async def monitor_swf(swf_key: str, swf_data: dict):
    """Monitor one SWF for new filings."""
    print(f"\n{swf_data['emoji']} Checking {swf_data['name']}...")

    try:
        # Step 1: Scrape EDGAR via Bright Data MCP
        markdown_content = await scrape_edgar_filings(
            swf_data['cik'], swf_key
        )
        print(f"  ✅ Bright Data MCP fetched EDGAR page ({len(markdown_content)} chars)")

        # Step 2: Parse filings from markdown
        filings = parse_filings_from_markdown(markdown_content, swf_key, swf_data['cik'])
        print(f"  📄 Found {len(filings)} filings")

        # Step 3: Process new filings only
        new_count = 0
        for filing in filings:
            if not filing_exists(filing.get('filing_url', '')):
                # Step 4: Generate Gemini intelligence
                enriched = generate_filing_intelligence(filing)
                enriched['swf_emoji'] = swf_data['emoji']
                enriched['swf_country'] = swf_data['country']
                enriched['processed_at'] = datetime.utcnow().isoformat()

                # Step 5: Save to MongoDB
                save_filing(enriched)
                new_count += 1
                print(f"  💾 Saved: {filing.get('company_name')} — {filing.get('filing_type')}")

        print(f"  ✨ {new_count} new filings processed for {swf_key}")

    except Exception as e:
        print(f"  ❌ Error monitoring {swf_key}: {e}")


async def run_agent():
    """Run one complete monitoring cycle across all 5 SWFs."""
    print("\n" + "="*60)
    print("🏦 Gulf SWF Filing Intelligence Agent")
    print("⚡ Powered by Bright Data MCP + Gemini 2.0 Flash")
    print(f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("="*60)

    # Monitor all 5 SWFs
    tasks = [
        monitor_swf(key, data)
        for key, data in SWF_CONFIG.items()
    ]
    await asyncio.gather(*tasks)

    # Show summary
    latest = get_latest_filings(5)
    print(f"\n📊 Latest 5 filings in database:")
    for f in latest:
        print(f"  • {f.get('swf_name')} → {f.get('company_name')} ({f.get('filing_type')})")

    print("\n✅ Monitoring cycle complete.")


if __name__ == "__main__":
    asyncio.run(run_agent())
```

---

## FILE 8: api/server.py

FastAPI backend serving data to the Next.js dashboard.

Build these endpoints:

```
GET /api/filings          — latest 20 filings (query param: ?limit=20)
GET /api/filings/{swf}    — filings for specific SWF
GET /api/summary          — per-SWF stats summary
GET /api/health           — health check
POST /api/trigger         — manually trigger one monitoring cycle
```

Enable CORS for localhost:3000 and the Vercel domain.
Return all responses as JSON.
Import database functions from agent/database.py.
Run with: `uvicorn api.server:app --reload --port 8000`

---

## FILE 9: dashboard/app/page.tsx

Main dashboard page. Show:

1. **Header** — "Gulf SWF Filing Intelligence" with live status badge
2. **Summary Cards** — one card per SWF showing filing count + latest date
3. **Intelligence Feed** — scrollable list of latest filings with:
   - SWF name + emoji + country flag
   - Target company name + ticker
   - Filing type badge (SC 13D / SC 13G)
   - Signal badge (BULLISH=green / BEARISH=red / NEUTRAL=gray)
   - Gemini key insight text
   - Filing date
4. **Auto-refresh** — poll `/api/filings` every 60 seconds

Use Tailwind CSS for styling. Dark theme preferred.
Use `fetch` to call the FastAPI backend at `NEXT_PUBLIC_API_URL`.

---

## FILE 10: README.md

Write a compelling README for hackathon judges covering:

1. **Project Title** — Gulf SWF Filing Intelligence Agent
2. **The Problem** — EDGAR rate limits + bot detection blocking real-time SWF monitoring
3. **The Solution** — Bright Data MCP bypasses all barriers
4. **Architecture Diagram** (ASCII art)
5. **Bright Data Tools Used** — MCP Server, Scrape as Markdown, Search Engine
6. **Hackathon Track** — Track 2: Finance & Market Intelligence
7. **Setup Instructions** — step by step
8. **Demo Screenshot** placeholder
9. **Team** — Zulfiqar Ali Mir, Black Iron Quantum AI

---

## IMPLEMENTATION SEQUENCE

Claude Code must follow this exact order:

1. Create project folder structure
2. Write `requirements.txt`
3. Write `agent/swf_config.py`
4. Write `agent/database.py`
5. Write `agent/filing_parser.py`
6. Write `agent/edgar_scraper.py`
7. Write `agent/intelligence.py`
8. Write `agent/main.py`
9. Write `api/server.py`
10. Initialize Next.js dashboard: `npx create-next-app@latest dashboard --typescript --tailwind --app`
11. Write dashboard components
12. Write `README.md`
13. Write `.gitignore`
14. Run `pip install -r requirements.txt`
15. Test `agent/main.py` — confirm Bright Data MCP connects and returns data

---

## TESTING CHECKLIST

After building, verify:

- [ ] `python agent/main.py` runs without errors
- [ ] Bright Data MCP connects and fetches EDGAR page
- [ ] At least 1 filing is parsed and saved to MongoDB
- [ ] Gemini generates intelligence JSON for each filing
- [ ] `uvicorn api.server:app` starts on port 8000
- [ ] `GET /api/filings` returns JSON array
- [ ] Next.js dashboard loads and shows filings
- [ ] No API keys committed to git

---

## DEMO VIDEO SCRIPT (3 minutes)

Record in this order for maximum judge impact:

1. **(0:00-0:20)** Show the problem — plain Python request to EDGAR gets rate-limited
2. **(0:20-0:45)** Show Bright Data MCP bypassing the block — terminal output
3. **(0:45-1:30)** Run `python agent/main.py` live — show all 5 SWFs being monitored
4. **(1:30-2:00)** Show MongoDB Atlas — filings appearing in real-time
5. **(2:00-2:40)** Show Next.js dashboard — live intelligence feed
6. **(2:40-3:00)** Close with the pitch — "Real-time SWF intelligence, previously impossible"

---

## COST ESTIMATE

| Operation | Cost | Calls for Hackathon |
|---|---|---|
| Bright Data MCP (free tier) | $0 | 5,000 free/month |
| Gemini 2.0 Flash | ~$0.001/filing | ~100 filings = $0.10 |
| MongoDB Atlas | Free tier | Free |
| Vercel | Free tier | Free |
| **Total** | **~$0.10** | Well within $252 budget |

---

## IMPORTANT NOTES FOR CLAUDE CODE

- Never hardcode API keys — always use `os.getenv()`
- Never commit `.env` to git
- The Bright Data MCP URL already contains the auth token — treat it as a secret
- SEC EDGAR is a US government public website — scraping public filings is legal
- Use `asyncio.gather()` to monitor all 5 SWFs in parallel for speed
- MongoDB `_id` fields must be converted to strings before JSON serialization
- All dates should be stored as ISO format strings for JSON compatibility
- If a filing field cannot be parsed, use `None` — never crash on missing data
