"""
Gemini intelligence layer — generates institutional-grade analysis
from parsed SEC filing data.
"""

import json
import os
import re
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Primary model; fallback to 1.5-flash if quota is exhausted on 2.0-flash
_llm_primary = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
    max_retries=0,
)
_llm_fallback = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
    max_retries=0,
)

_PROMPT_TEMPLATE = """
You are an institutional investment analyst specializing in Sovereign Wealth Fund activity.

Analyze this SEC filing and provide structured intelligence:

Filing Data:
- SWF: {swf_name}
- Filing Type: {filing_type}
- Target Company: {company_name}
- Ticker: {company_ticker}
- Shares Owned: {shares_owned}
- Ownership %: {ownership_percent}%
- Filing Date: {filing_date}

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

_FALLBACK_INTEL = {
    "signal": "NEUTRAL",
    "action": "MAINTAIN",
    "sector": "Unknown",
    "summary": "Intelligence generation temporarily unavailable due to API quota.",
    "significance": "LOW",
    "key_insight": "Gemini API quota exceeded — re-run the agent later for full analysis.",
}


def _call_llm(prompt: str, max_retries: int = 1) -> str:
    """Try primary model then fallback; retry on 429; never raise."""
    models = [("gemini-2.5-flash", _llm_primary), ("gemini-2.0-flash-lite", _llm_fallback)]
    delay = 15

    for model_name, llm in models:
        for attempt in range(max_retries):
            try:
                return llm.invoke(prompt).content
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    if attempt < max_retries - 1:
                        print(f"    [Gemini 429 on {model_name} — waiting {delay}s, retry {attempt + 2}/{max_retries}]")
                        time.sleep(delay)
                        delay *= 2
                    continue
                # Any other error (404, 403, etc.) — skip this model entirely
                print(f"    [Gemini {model_name} error: {err[:120]}]")
                break
        print(f"    [Switching from {model_name} to next model]")
        delay = 15

    return None  # All models failed — caller uses fallback intelligence


def generate_filing_intelligence(filing: dict) -> dict:
    """Takes a parsed filing dict and returns enriched intelligence."""
    prompt = _PROMPT_TEMPLATE.format(
        swf_name=filing.get("swf_name", "Unknown"),
        filing_type=filing.get("filing_type", "Unknown"),
        company_name=filing.get("company_name", "Unknown"),
        company_ticker=filing.get("company_ticker", "Unknown"),
        shares_owned=filing.get("shares_owned", "Unknown"),
        ownership_percent=filing.get("ownership_percent", "Unknown"),
        filing_date=filing.get("filing_date", "Unknown"),
    )

    raw = _call_llm(prompt)

    if raw is None:
        return {**filing, **_FALLBACK_INTEL}

    try:
        content = raw.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        intelligence = json.loads(content)
    except Exception:
        intelligence = {**_FALLBACK_INTEL, "summary": raw[:300]}

    return {**filing, **intelligence}
