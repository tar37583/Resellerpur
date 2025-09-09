from groq import Groq
import re
import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv  
"""
LLM utility functions for generating natural language reasoning
for both PriceSuggestor and ChatModerator.

- By default, returns stub/fallback outputs so the system works offline.
- If you want real LLM integration, replace the stubs with OpenAI / HuggingFace calls.
"""



# ----------------------------
# Price Suggestor helper
# ----------------------------
GROK_API_KEY = os.getenv("GROK_API_KEY")
client = Groq(
        api_key=GROK_API_KEY,
    )

def generate_price_reasoning(
    item: Dict[str, Any],
    comps: List[Dict[str, Any]],
    baseline: float,
    final_price: float,
    min_price: float,
    max_price: float,
    web_results: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Generate a human-friendly reasoning string for a price suggestion.


    - This is a stub fallback that works offline and summarizes the inputs.
    - If you add an LLM later, call the model here and return its string.


    Parameters
    ----------
    item: dictionary of the queried product
    comps: list of comparables used by the distance-based comparator
    baseline: formula-based baseline price
    final_price: blended central price
    min_price, max_price: final suggested range (ints)
    web_results: optional list of web-scraped or API results (source/title/price)
    """


    title = item.get("title", "item")
    brand = item.get("brand", "")
    cond = item.get("condition", "")
    age = item.get("age_months", "?")


    # short summary of web results (if any)
    web_summary = ""
    if web_results:
        sources = {r.get("source") for r in web_results if r.get("source")}
        sample = []
        for r in web_results[:3]:
            p = r.get("price")
            sample.append(f"{r.get('source','web')}: {p}")
        web_summary = "Web comparables: " + ", ".join(sample) + ". "


    comp_count = len(comps) if comps is not None else 0


    return (
        f"Your {title} ({brand}, {cond}, {age} months old) was valued using {comp_count} "
        f"dataset comparables, a depreciation baseline (₹{baseline:,.0f}), and online market prices. "
        f"{web_summary}The blended market central price is approximately ₹{final_price:,.0f}, "
        f"so a reasonable negotiation range is ₹{min_price:,} – ₹{max_price:,}."
    )


# ----------------------------
# Chat Moderator helper
# ----------------------------
def moderate_message_with_llm(message: str):
    """
    Use an LLM to classify a chat message.
    Replace stub with actual LLM call if available.
    """
    prompt = f"""
    You are a chat moderator for an online resale marketplace.
    Analyze the following message and classify it into one of:
    - abusive
    - spam
    - contains_phone
    - safe

    Message: "{message}"

    Respond in a **single plain string** with this format:
    Status: <one of abusive/spam/contains_phone/safe> | Reason: <short explanation>
    """

    resp = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return resp.choices[0].message.content.strip()

# ----------------------------
# Web Search helper
# ----------------------------


def search_online_prices(query: str):
    """
    Online price search using LLM.
    Returns a list of dicts: [{source, title, price}, ...]
    """

    prompt = f"""
    Search the web for resale prices in INR for this query: "{query}".
    Return exactly 5 recent listings in strict JSON format as a list of objects.
    Each object must have:
    - source: website name (e.g., olx.in, cashify.in)
    - title: short description of the listing
    - price: price string in INR (e.g., "₹32,000" or "₹30,500 – ₹33,000")

    Example:
    [
      {{"source": "olx.in", "title": "iPhone 12 Good Condition", "price": "₹32,000"}},
      {{"source": "cashify.in", "title": "Apple iPhone 12 resale", "price": "₹30,500 – ₹33,000"}}
    ]
    Do not include any explanations or extra text.
    """

    response = client.chat.completions.create(
        model="groq/compound",  # or "gpt-4o-mini", etc.
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        response_format={"type": "json_object"}  # ensures JSON output if supported
    )

    # Parse safely
    try:
        data = response.choices[0].message.content.strip()
        # print("Raw LLM output:", data)
        return json.loads(data)
    except Exception as e:
        print(" Error parsing LLM output:", e)
        return []




