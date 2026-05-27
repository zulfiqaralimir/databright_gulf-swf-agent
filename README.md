---
title: Gulf SWF Filing Intelligence API
emoji: 🏦
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---

# Gulf SWF Filing Intelligence Agent

> Real-time SC 13D/13G monitoring for Gulf Sovereign Wealth Funds — powered by Bright Data MCP + Gemini 2.0 Flash

**Hackathon:** Web Data UNLOCKED — Bright Data × lablab.ai | May 2026
**Track:** Track 2 — Finance & Market Intelligence
**Submitted by:** Zulfiqar Ali Mir, Black Iron Quantum AI (Private) Limited

---

## The Problem

Gulf Sovereign Wealth Funds — ADIA, PIF, QIA, Mubadala, ADQ — collectively manage over **$4 trillion** in assets. When they file an SC 13D or SC 13G with the SEC, it signals a major institutional investment move. Hedge funds and institutions pay six-figure subscriptions to data vendors to learn about these moves within hours.

**But SEC EDGAR blocks automated access:**
- Rate-limits scrapers to 10 requests/second per IP
- Actively detects and blocks bots
- Returns stale cached data under load

Any AI agent that tries to monitor these filings in real time hits a wall.

---

## The Solution

**Bright Data MCP Server bypasses every barrier:**
- Rotates IPs automatically — no rate-limit blocks
- Solves CAPTCHAs transparently
- Returns fresh, unblocked data every time
- Delivers clean markdown via `scrape_as_markdown` — no HTML parsing needed

This agent combines Bright Data's web infrastructure with Gemini 2.0 Flash's analytical intelligence to deliver institutional-grade SWF filing intelligence that was previously only available to hedge funds with enterprise data subscriptions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MONITORING AGENT                       │
│                   (agent/main.py)                        │
└──────────────┬──────────────────────────────────────────┘
               │ asyncio.gather() — 5 SWFs in parallel
               ▼
┌─────────────────────────────┐
│    Bright Data MCP Server   │  ← SSE connection
│    (edgar_scraper.py)       │  ← scrape_as_markdown tool
│                             │  ← IP rotation + CAPTCHA bypass
└──────────────┬──────────────┘
               │ Returns clean markdown
               ▼
┌─────────────────────────────┐
│    Filing Parser            │  ← regex + string parsing
│    (filing_parser.py)       │  ← extracts 9 structured fields
└──────────────┬──────────────┘
               │ structured filing dict
               ▼
┌─────────────────────────────┐
│    Gemini 2.0 Flash         │  ← LangChain + Google GenAI
│    (intelligence.py)        │  ← signal, action, sector, insight
└──────────────┬──────────────┘
               │ enriched filing dict
               ▼
┌─────────────────────────────┐
│    MongoDB Atlas            │  ← pymongo, unique index on URL
│    (database.py)            │  ← deduplication built-in
└──────────────┬──────────────┘
               │ stored
               ▼
┌─────────────────────────────┐    ┌──────────────────────┐
│    FastAPI Server           │◄───│  Next.js Dashboard   │
│    (api/server.py)          │    │  (dashboard/)        │
│    port 8000                │    │  Tailwind dark theme │
└─────────────────────────────┘    └──────────────────────┘
```

---

## Bright Data Tools Used

| Tool | How Used |
|---|---|
| **MCP Server (SSE)** | Long-lived streaming connection to Bright Data infrastructure |
| **scrape_as_markdown** | Fetches EDGAR filing pages as clean markdown — no HTML parsing |
| **IP Rotation** | Automatic — bypasses EDGAR's per-IP rate limits |
| **Bot Detection Bypass** | Transparent — no CAPTCHA failures on EDGAR pages |

---

## Five Gulf SWFs Monitored

| SWF | Country | AUM | SEC CIK |
|---|---|---|---|
| ADIA — Abu Dhabi Investment Authority | 🇦🇪 UAE | $1.1T | 0001496957 |
| PIF — Public Investment Fund | 🇸🇦 Saudi Arabia | $0.9T | 0001619212 |
| QIA — Qatar Investment Authority | 🇶🇦 Qatar | $0.5T | 0001346980 |
| Mubadala Investment Company | 🇦🇪 UAE | $0.3T | 0001401966 |
| ADQ — Abu Dhabi Developmental Holding | 🇦🇪 UAE | $0.2T | 0001831868 |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier works)
- Google Gemini API key

### 1. Clone and configure

```bash
git clone <repo-url>
cd gulf-swf-agent
```

Edit `.env` with your credentials (template already in repo).

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the monitoring agent

```bash
cd agent
python main.py
```

This scrapes all 5 SWFs in parallel, generates Gemini intelligence for each filing, and saves to MongoDB.

### 4. Start the FastAPI server

```bash
uvicorn api.server:app --reload --port 8000
```

### 5. Start the Next.js dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/filings` | Latest 20 filings (`?limit=N`) |
| GET | `/api/filings/{swf}` | Filings for ADIA, PIF, QIA, Mubadala, ADQ |
| GET | `/api/summary` | Per-SWF stats |
| GET | `/api/health` | Health check |
| POST | `/api/trigger` | Trigger a monitoring cycle |

---

## Intelligence Output (per filing)

Gemini 2.0 Flash enriches every filing with:

```json
{
  "signal": "BULLISH",
  "action": "NEW_POSITION",
  "sector": "Technology",
  "significance": "HIGH",
  "summary": "ADIA's acquisition of a 5.2% stake...",
  "key_insight": "Gulf SWF entry signals long-term confidence in AI infrastructure build-out."
}
```

---

## Demo Screenshot

*(Run the agent and add screenshot here before submission)*

---

## Cost Estimate

| Service | Cost |
|---|---|
| Bright Data MCP | $0 (free tier — 5,000 req/month) |
| Gemini 2.0 Flash | ~$0.10 for 100 filings |
| MongoDB Atlas | $0 (free tier) |
| Vercel | $0 (free tier) |
| **Total** | **~$0.10** |

---

## Team

**Zulfiqar Ali Mir**
Black Iron Quantum AI (Private) Limited
manager.equity.finance@gmail.com

*Solo submission — Web Data UNLOCKED Hackathon, May 2026*
