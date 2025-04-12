import re
import json
from ollama import chat

def classify_query(user_query):
    system_prompt = """
    You are a query classifier for a mutual fund search engine.

    Your job is to classify user queries into one of the following types:
    - "entity_query": if the query is about a specific named fund (e.g., "icici infra", "hdfc top 100").
    - "sector_query": if the query is about a sector (e.g., "tech funds", "pharma mutual funds").
    - "performance_query": if the query mentions returns or performance (e.g., "high return funds").
    - "tax_query": if the query is about tax-saving (e.g., "ELSS", "tax funds").
    - "holding_query": if the user mentions underlying holdings (e.g., "funds with hdfc").
    - "attribute_query": if the user gives numeric filters (e.g., "AUM > 1000cr", "expense ratio < 1%").

    Return ONLY a valid JSON in one line. Do not explain anything. Do not include <think> or other text.

    Examples:
    {"type": "entity_query", "entity": "hdfc infra", "filters": {}}
    {"type": "sector_query", "filters": {"sector": "technology"}}
    {"type": "performance_query", "filters": {"return": "high"}}
    {"type": "tax_query", "filters": {"category": "tax"}}
    {"type": "holding_query", "filters": {"holding": "hdfc"}}
    {"type": "attribute_query", "filters": {"aum_min": 1000}}
    """


    response = chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_query}
    ])

    content = response['message']['content']
    
    # 🧠 Try extracting the JSON using regex
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            cleaned = match.group(0).replace('\n', '').replace('\r', '')
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"❌ Couldn't parse cleaned JSON:\n{cleaned}")
            return None
    else:
        print("❌ No JSON found in response:\n", content)
        return None
