"""
Regenerate Gemini intelligence for all filings that have the fallback quota message.
Run from the agent/ directory.
"""

import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'), override=True)

from database import get_db
from intelligence import generate_filing_intelligence

FALLBACK_MARKER = "Intelligence generation temporarily unavailable"


def regenerate():
    db = get_db()
    collection = db["filings"]

    # Find all filings with the fallback summary
    query = {"summary": {"$regex": FALLBACK_MARKER}}
    filings = list(collection.find(query))
    total = len(filings)

    print(f"Found {total} filings with fallback intelligence. Regenerating...")
    print("=" * 60)

    success = 0
    failed = 0

    for i, filing in enumerate(filings, 1):
        filing_id = filing["_id"]
        company = filing.get("company_name", "Unknown")
        swf = filing.get("swf_name", "Unknown")
        ftype = filing.get("filing_type", "Unknown")

        print(f"\n[{i}/{total}] {swf} -> {company} ({ftype})")

        # Remove MongoDB _id before passing to intelligence
        filing_data = {k: v for k, v in filing.items() if k != "_id"}

        enriched = generate_filing_intelligence(filing_data)

        new_summary = enriched.get("summary", "")
        if FALLBACK_MARKER in new_summary:
            print(f"  FAILED — still getting fallback. Skipping update.")
            failed += 1
        else:
            # Update the filing in MongoDB
            update_fields = {
                "signal": enriched.get("signal"),
                "action": enriched.get("action"),
                "sector": enriched.get("sector"),
                "summary": enriched.get("summary"),
                "significance": enriched.get("significance"),
                "key_insight": enriched.get("key_insight"),
            }
            collection.update_one({"_id": filing_id}, {"$set": update_fields})

            print(f"  Signal: {enriched.get('signal')} | Action: {enriched.get('action')} | Significance: {enriched.get('significance')}")
            print(f"  Sector: {enriched.get('sector')}")
            print(f"  Insight: {enriched.get('key_insight', '')[:120]}")
            success += 1

        # Always throttle — applies to both success and failure
        time.sleep(90)

    print("\n" + "=" * 60)
    print(f"Done. Updated: {success} | Failed: {failed} | Total: {total}")


if __name__ == "__main__":
    regenerate()
