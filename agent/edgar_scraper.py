"""
EDGAR scraper using EDGAR EFTS full-text search API + Bright Data MCP search_engine.

Primary:  EDGAR EFTS JSON API (data.sec.gov) — structured, no rate-limit issues.
Fallback: Bright Data search_engine — finds filings via Google when EFTS is slow.
"""

import os
import json
import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

MCP_URL = os.getenv("BRIGHT_DATA_MCP_URL")

EDGAR_HEADERS = {
    "User-Agent": "Gulf SWF Agent manager.equity.finance@gmail.com",
    "Accept": "application/json",
}

EFTS_URL = "https://efts.sec.gov/LATEST/search-index"


async def scrape_edgar_filings(cik: str, swf_name: str) -> str:
    """
    Fetch SC 13D/13G filings for a SWF.
    Uses EDGAR EFTS API first; falls back to Bright Data search_engine.
    Returns a JSON string consumed by filing_parser.parse_filings_from_markdown().
    """
    from swf_config import SWF_CONFIG, FILING_TYPES

    # Resolve search term from config
    swf_entry = next(
        (v for v in SWF_CONFIG.values() if v["name"] == swf_name),
        None,
    )
    search_term = swf_entry["search_term"] if swf_entry else swf_name

    # --- Primary: EDGAR EFTS full-text search API ---
    try:
        params = {
            "q": f'"{search_term}"',
            "forms": "SC 13G,SC 13D,SC 13G/A,SC 13D/A",
            "dateRange": "custom",
            "startdt": "2018-01-01",
            "enddt": "2026-12-31",
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(
                EFTS_URL, params=params, headers=EDGAR_HEADERS, timeout=30
            )
            r.raise_for_status()
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
            return json.dumps({"source": "edgar_efts", "search_term": search_term, "hits": hits})

    except Exception as efts_err:
        print(f"    [EDGAR EFTS failed: {efts_err}] — trying Bright Data search_engine")

    # --- Fallback: Bright Data search_engine ---
    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "search_engine",
                {
                    "query": f'"{search_term}" SEC "SC 13" filing site:sec.gov',
                    "engine": "google",
                },
            )
            text = "".join(
                b.text for b in result.content if hasattr(b, "text")
            )
            return json.dumps({"source": "brightdata_search", "content": text})


async def get_filing_document(filing_url: str) -> str:
    """
    Fetch a specific SEC filing document via Bright Data MCP scrape_as_markdown.
    """
    async with sse_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("scrape_as_markdown", {"url": filing_url})
            return "".join(b.text for b in result.content if hasattr(b, "text"))
