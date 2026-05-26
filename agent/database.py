import os
from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(os.getenv("MONGODB_URI"))
        _db = _client[os.getenv("MONGODB_DB", "gulf_swf_agent")]
        _db.filings.create_index("filing_url", unique=True)
    return _db


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def save_filing(filing: dict) -> str:
    """Save a filing to MongoDB. Return inserted_id as string."""
    db = get_db()
    try:
        result = db.filings.insert_one(filing)
        return str(result.inserted_id)
    except DuplicateKeyError:
        return None


def get_latest_filings(limit: int = 20) -> list:
    """Return latest N filings sorted by filing_date descending."""
    db = get_db()
    docs = db.filings.find().sort("filing_date", DESCENDING).limit(limit)
    return [_serialize(dict(doc)) for doc in docs]


def get_filings_by_swf(swf_name: str, limit: int = 10) -> list:
    """Return filings for a specific SWF."""
    db = get_db()
    docs = (
        db.filings
        .find({"swf_name": swf_name})
        .sort("filing_date", DESCENDING)
        .limit(limit)
    )
    return [_serialize(dict(doc)) for doc in docs]


def filing_exists(filing_url: str) -> bool:
    """Check if a filing URL already exists in DB to avoid duplicates."""
    if not filing_url:
        return False
    db = get_db()
    return db.filings.count_documents({"filing_url": filing_url}) > 0


def get_swf_summary() -> list:
    """Return summary stats per SWF — count of filings, latest date."""
    db = get_db()
    pipeline = [
        {
            "$group": {
                "_id": "$swf_name",
                "count": {"$sum": 1},
                "latest_date": {"$max": "$filing_date"},
                "swf_emoji": {"$first": "$swf_emoji"},
                "swf_country": {"$first": "$swf_country"},
            }
        },
        {"$sort": {"count": -1}},
    ]
    results = list(db.filings.aggregate(pipeline))
    return [
        {
            "swf_name": r["_id"],
            "count": r["count"],
            "latest_date": r.get("latest_date", ""),
            "swf_emoji": r.get("swf_emoji", ""),
            "swf_country": r.get("swf_country", ""),
        }
        for r in results
    ]
