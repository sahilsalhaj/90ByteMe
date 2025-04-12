import numpy as np
import json
from embedder import get_embedding
from indexer import MultiDatasetIndexer
from utils import clean_query
from query_classifier import classify_query
from itertools import permutations
from rapidfuzz import fuzz

# Load the configuration and secondary dataset
with open("config.json") as f:
    config = json.load(f)

# Function to load additional data source (holding details)
def load_additional_data(filename="data/mfh_cleaned.json"):
    with open(filename, 'r') as f:
        return [json.loads(line) for line in f]

mutual_holdings_data = load_additional_data()  # Load additional fund data

# Initialize indexer
indexer = MultiDatasetIndexer()
indexer.build_or_load_all()

def search_fund(user_query):
    print("🧠 Using Mistral to classify query...")
    parsed = classify_query(user_query)

    if not parsed:
        return []

    if parsed["type"] == "entity_query":
        entity = parsed.get("entity", user_query)
        return search_by_entity(entity)

    elif parsed["type"] in {"sector_query", "performance_query", "tax_query", "holding_query", "attribute_query"}:
        filters = parsed.get("filters", {})
        return search_by_metadata(filters)

    return []

def generate_query_variants(query):
    words = query.strip().lower().split()
    variants = set()

    variants.add(query)

    if 2 <= len(words) <= 3:
        for p in permutations(words):
            variants.add(" ".join(p))

    variants.update(words)

    if len(words) > 1:
        variants.add("".join(words))

    return list(variants)

def search_by_entity(query):
    variants = generate_query_variants(query)
    all_results = []

    # Search across all indices, focusing on the 'name' field for mutual funds
    for dataset_key in indexer.indices.keys():
        index = indexer.indices[dataset_key]
        metadata = indexer.metadatas[dataset_key]

        for v in variants:
            emb = get_embedding(v).astype("float32")
            D, I = index.search(np.array([emb]), config["top_k"])
            for idx in I[0]:
                # Check if it's a mutual fund record (check for 'name' field)
                if 'name' in metadata[idx]:
                    all_results.append(metadata[idx])

    unique_results = {r["name"]: r for r in all_results}.values()
    reranked = rerank_results(list(unique_results), query)
    return reranked[:5]


def search_by_metadata(filters):
    results = []

    for metadata in indexer.metadatas.values():
        for fund in metadata:
            matched = True
            for key, val in filters.items():
                fund_val = fund.get(key, "")
                if isinstance(val, str) and isinstance(fund_val, str):
                    if val.lower() not in fund_val.lower():
                        matched = False
                        break
                elif isinstance(val, (int, float)) and isinstance(fund_val, (int, float)):
                    if key.endswith("_min") and fund_val < val:
                        matched = False
                        break
                    if key.endswith("_max") and fund_val > val:
                        matched = False
                        break
                else:
                    matched = False
                    break

            if matched:
                # Enrich each matched fund with additional metadata from mutual_holdings_data
                enriched_fund = enrich_with_additional_metadata(fund)
                results.append(enriched_fund)

    filter_text = " ".join(str(v) for v in filters.values())
    reranked = rerank_results(results, filter_text)
    return reranked[:5]

def rerank_results(results, query):
    query = clean_query(query)
    query_tokens = set(query.split())
    is_name_query = len(query_tokens) <= 3

    # Unified metadata weights across datasets
    weights = {
        "name": 0.4,                    # common identifier
        "category": 0.15,               # common to all
        "sector": 0.15,                 # common to all
        "industry": 0.1,                # common to all
        "shortName": 0.1,               # helpful in stock & MF holdings
        "assetType": 0.05,              # useful in MF holdings
        "fundPrimarySector": 0.05       # unique to mutual funds, still useful
    }

    reranked = []
    for item in results:
        score = 0.0
        print(f"\n--- Scoring item: {item.get('name', 'UNKNOWN')} ---")

        for field, weight in weights.items():
            value = item.get(field, "")
            if not isinstance(value, str):
                continue
            value = value.lower()
            matches = sum(1 for token in query_tokens if token in value)
            partial_score = weight * (matches / len(query_tokens)) if query_tokens else 0.0
            print(f"  {field}: match score = {partial_score:.3f}")
            score += partial_score

        if is_name_query and "name" in item:
            fuzzy_score = fuzz.partial_ratio(query.lower(), item["name"].lower()) / 100
            print(f"  ➤ Fuzzy score for name: {fuzzy_score:.3f}")
            score = score * 0.7 + fuzzy_score * 0.3

        item["score"] = round(score, 4)
        reranked.append(item)

    reranked_sorted = sorted(reranked, key=lambda x: x["score"], reverse=True)
    print("\n🏁 Final reranked results:")
    for r in reranked_sorted[:5]:
        print(f"  - {r.get('name', 'UNKNOWN')} (Score: {r['score']})")

    return reranked_sorted

def format_fund_result(result):
    return {
        "name": result.get("name") or "N/A",  # Ensure the fund name is correctly displayed
        "category": result.get("category", "N/A"),
        "subcategory": result.get("subcategory", "N/A"),
        "fund_type": result.get("fund_type") or result.get("instrument_type") or "N/A",
        "sector": result.get("sector") or result.get("industry") or "N/A",
        "industry": result.get("industry") or result.get("sector") or "N/A",
        "amc": result.get("amc") or result.get("company_name") or result.get("issuer_name") or "N/A",
        "source": result.get("source", "unknown")
    }

# Function to enrich matched fund with extra details from mutual_holdings_data
def enrich_with_additional_metadata(matched_fund):
    # Example: Enrich the fund with additional data, if needed
    # This can be customized further based on what extra info you need
    enriched_fund = matched_fund.copy()
    # For example, adding more info from mutual_holdings_data
    for holding in mutual_holdings_data:
        if holding.get("fund_name") == matched_fund.get("name"):
            enriched_fund.update(holding)
    return enriched_fund
