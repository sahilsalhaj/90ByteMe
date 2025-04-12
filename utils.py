import json

def clean_query(text):
    return text.lower().strip()

def format_fund_result(fund):
    return {
        "name": fund.get("name", ""),
        "category": fund.get("category", ""),
        "sector": fund.get("sector", ""),
        "industry": fund.get("industry", ""),
        "score": round(fund.get("score", 0.0), 4)
    }

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)  # For regular JSON file (object or array)
        except json.JSONDecodeError:
            # Try line-delimited JSON fallback
            f.seek(0)
            return [json.loads(line) for line in f if line.strip()]
