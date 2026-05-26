"""
Parses filing data from two possible sources:
  1. EDGAR EFTS JSON hits (structured — preferred)
  2. Bright Data search_engine JSON (fallback)
"""

import re
import json
from swf_config import SWF_CONFIG, EDGAR_BASE_URL, FILING_TYPES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_ticker(text: str):
    if not text:
        return None
    m = re.search(r'\(([A-Z]{1,5})\)', text)
    if m:
        candidate = m.group(1)
        if candidate not in {"SC", "SEC", "LLC", "LTD", "INC", "NA", "CIK"}:
            return candidate
    return None


def _clean_display_name(name: str) -> str:
    """Strip CIK annotation and ticker from a display_name string."""
    name = re.sub(r'\s*\(CIK\s+\d+\)', '', name)
    name = re.sub(r'\s{2,}', ' ', name)
    return name.strip()


def _build_filing_url(adsh: str, subject_cik: str) -> str:
    """Build an EDGAR filing index URL from accession number + subject CIK."""
    adsh_clean = adsh.replace('-', '')
    cik_clean = subject_cik.lstrip('0') if subject_cik else ''
    return f"{EDGAR_BASE_URL}/Archives/edgar/data/{cik_clean}/{adsh_clean}/{adsh}-index.htm"


# ---------------------------------------------------------------------------
# Parse EDGAR EFTS hits (primary path)
# ---------------------------------------------------------------------------

def _parse_efts_hits(hits: list, swf_key: str, swf_cik: str) -> list:
    swf_data = SWF_CONFIG.get(swf_key, {})
    swf_name = swf_data.get("name", swf_key)
    search_term = swf_data.get("search_term", swf_name).lower()

    filings = []
    for hit in hits:
        src = hit.get("_source", {})

        filing_type = src.get("form", src.get("file_type", ""))
        if not filing_type:
            continue

        adsh = src.get("adsh", "")
        filing_date = src.get("file_date")

        # Separate SWF (filer) from subject company
        display_names = src.get("display_names", [])
        ciks = src.get("ciks", [])

        company_name = None
        company_ticker = None
        company_cik = None
        resolved_swf_cik = swf_cik

        for dn in display_names:
            cik_match = re.search(r'\(CIK\s+(\d+)\)', dn)
            dn_cik = cik_match.group(1) if cik_match else None
            dn_clean = _clean_display_name(dn)

            if search_term in dn.lower():
                # This entry IS the SWF
                if dn_cik:
                    resolved_swf_cik = dn_cik
            else:
                # This entry is the subject/investee company
                company_cik = dn_cik
                company_ticker = _extract_ticker(dn)
                company_name = re.sub(r'\s*\([A-Z]{1,5}\)\s*', ' ', dn_clean).strip()

        if not company_name and display_names:
            # Only one entity listed — it's both filer and subject
            company_name = _clean_display_name(display_names[0])

        filing_url = _build_filing_url(adsh, company_cik or resolved_swf_cik)

        filings.append({
            "filing_date": filing_date,
            "filing_type": filing_type,
            "company_name": company_name or "Unknown",
            "company_ticker": company_ticker,
            "shares_owned": None,
            "ownership_percent": None,
            "filing_url": filing_url,
            "swf_name": swf_name,
            "swf_cik": resolved_swf_cik,
        })

    return filings


# ---------------------------------------------------------------------------
# Parse Bright Data search_engine results (fallback path)
# ---------------------------------------------------------------------------

def _parse_brightdata_search(content: str, swf_key: str, swf_cik: str) -> list:
    """Extract SEC filing URLs from Bright Data search_engine JSON output."""
    swf_data = SWF_CONFIG.get(swf_key, {})
    swf_name = swf_data.get("name", swf_key)

    filings = []
    try:
        data = json.loads(content)
        organic = data.get("organic", [])
    except Exception:
        return filings

    for item in organic:
        link = item.get("link", "")
        title = item.get("title", "")
        desc = item.get("description", "")

        if "sec.gov" not in link:
            continue

        # Detect filing type from title/description
        filing_type = None
        for ft in FILING_TYPES:
            if ft in title.upper() or ft in desc.upper():
                filing_type = ft
                break
        if not filing_type:
            continue

        # Extract date
        date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', desc + title)
        filing_date = date_match.group(1) if date_match else None

        filings.append({
            "filing_date": filing_date,
            "filing_type": filing_type,
            "company_name": title[:100] or "Unknown",
            "company_ticker": _extract_ticker(title),
            "shares_owned": None,
            "ownership_percent": None,
            "filing_url": link,
            "swf_name": swf_name,
            "swf_cik": swf_cik,
        })

    return filings


# ---------------------------------------------------------------------------
# Public entry point — called by main.py
# ---------------------------------------------------------------------------

def parse_filings_from_markdown(raw: str, swf_key: str, swf_cik: str) -> list:
    """
    Dispatch to the right parser based on the JSON envelope from edgar_scraper.
    """
    try:
        envelope = json.loads(raw)
        source = envelope.get("source")

        if source == "edgar_efts":
            hits = envelope.get("hits", [])
            return _parse_efts_hits(hits, swf_key, swf_cik)

        if source == "brightdata_search":
            content = envelope.get("content", "")
            return _parse_brightdata_search(content, swf_key, swf_cik)

    except (json.JSONDecodeError, AttributeError):
        pass

    # Legacy: plain markdown fallback (kept for compatibility)
    return _parse_markdown_legacy(raw, swf_key, swf_cik)


# ---------------------------------------------------------------------------
# Legacy markdown parser (kept as last-resort fallback)
# ---------------------------------------------------------------------------

def _parse_markdown_legacy(markdown: str, swf_key: str, swf_cik: str) -> list:
    swf_data = SWF_CONFIG.get(swf_key, {})
    swf_name = swf_data.get("name", swf_key)
    filings = []

    for line in markdown.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 2:
            continue
        row_text = " ".join(cells)

        filing_type = next(
            (ft for ft in FILING_TYPES if ft in row_text.upper()), None
        )
        if not filing_type:
            continue

        date_m = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', row_text)
        url_m = re.search(r'(https?://(?:www\.)?sec\.gov\S+)', row_text)
        pct_m = re.search(r'(\d+\.?\d*)\s*%', row_text)
        pct = float(pct_m.group(1)) if pct_m else None
        url = url_m.group(1).rstrip('.,)') if url_m else None

        filings.append({
            "filing_date": date_m.group(1) if date_m else None,
            "filing_type": filing_type,
            "company_name": None,
            "company_ticker": None,
            "shares_owned": None,
            "ownership_percent": pct,
            "filing_url": url,
            "swf_name": swf_name,
            "swf_cik": swf_cik,
        })

    return filings
