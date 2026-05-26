"""
Main agent loop — monitors all 5 Gulf SWFs for new SEC filings.
Run this script to start the monitoring agent.
"""

import sys
import asyncio
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Force UTF-8 output so emoji characters render on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

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
        traceback.print_exc()


async def run_agent():
    """Run one complete monitoring cycle across all 5 SWFs."""
    print("\n" + "=" * 60)
    print("🏦 Gulf SWF Filing Intelligence Agent")
    print("⚡ Powered by Bright Data MCP + Gemini 2.0 Flash")
    print(f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 60)

    # Run sequentially to avoid Gemini rate limits across 5 concurrent SWF calls
    for key, data in SWF_CONFIG.items():
        await monitor_swf(key, data)

    latest = get_latest_filings(5)
    print(f"\n📊 Latest 5 filings in database:")
    for f in latest:
        print(f"  • {f.get('swf_name')} → {f.get('company_name')} ({f.get('filing_type')})")

    print("\n✅ Monitoring cycle complete.")


if __name__ == "__main__":
    asyncio.run(run_agent())
