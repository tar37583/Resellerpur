
# Resellpur Marketplace Agents

Two small agents for the internship assessment: a **Price Suggestor** and a **Chat Moderation** microservice, exposed via FastAPI.

> Built to match the problem statement (agents, dataset, JSON I/O, optional API) and to be practical & easy to extend.


## Features

- **Agent 1 – Price Suggestor**: Given product details, suggests a fair market **price range** with **reasoning** and **comparables**.
- **Agent 2 – Chat Moderation**: Classifies a message as `safe`, `abusive`, `spam`, or `contains_phone` with highlighted spans.
- **FastAPI** endpoints: `/negotiate` and `/moderate`.
- Lightweight, no external model dependency by default; designed so you can plug in an LLM later if you want.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app:app --reload
```

It will start at: `http://127.0.0.1:8000`

- Docs: `http://127.0.0.1:8000/docs`
- Health: `GET /health`

## Endpoints

### POST /negotiate

**Body**

```json
{
  "category": "Mobile",
  "brand": "Apple",
  "condition": "Good",
  "age_months": 24,
  "asking_price": 34000,
  "location": "Mumbai",
  "title": "iPhone 12"
}
```

**Response (example)**

```json
{
  "input": { ... },
  "suggestion": {
    "suggested_min": 30000,
    "suggested_max": 36000,
    "central_price": 32900.0,
    "method": "ensemble(comps+baseline)",
    "reasoning": "Category='Mobile' ...",
    "comps_used": [{ "id": 1, "title": "iPhone 12", ... }]
  }
}
```

### POST /moderate

**Body**

```json
{ "message": "This is stupid. Call me at +91 9876543210" }
```

**Response (example)**

```json
{
  "input": "This is stupid. Call me at +91 9876543210",
  "result": {
    "label": "abusive",
    "reasons": ["contains a phone number", "contains abusive language"],
    "spans": [
      {"type":"phone","match":"+91 9876543210"},
      {"type":"abusive","match":"stupid"}
    ]
  }
}
```

## How price suggestion works

1. **Nearest Comparables (k=5)** within the same category using a simple distance over age, condition, brand, and location.
2. **Baseline Formula** using exponential depreciation (category-wise rate), condition multiplier, and brand retention factor.
3. **Ensemble**: Weighted blend of comparables and baseline; range is centered around the ensemble price with spread from comp volatility.
4. **Transparent JSON**: Includes reasoning and the comps it used.

This is robust on small datasets and behaves sensibly when comps are scarce.

## Data

The file `data/listings.csv` reproduces the sample dataset from the assessment handout.

## Extend / Bonus ideas

- Wire a live comps fetcher (OLX/Cashify scraping or API) and blend with the local dataset.
- Plug an LLM (Groq / HF Inference) to:
  - Generate richer reasoning.
  - Explain negotiation tactics or counter-offers.
- Add **fraud detection** (e.g., mismatched specs vs title, suspicious pricing).
- Add **multi-agent negotiation** (buyer offers, seller counters).

## Tests (quick)

Run a quick sanity test without the server:

```bash
python - <<'PY'
from agents.price_suggestor import PriceSuggestor
from agents.chat_moderation import ChatModerator

ps = PriceSuggestor.from_csv("data/listings.csv")
item = {
    "category": "Mobile", "brand":"Apple", "condition":"Good",
    "age_months":24, "asking_price":35000, "location":"Mumbai", "title":"iPhone 12"
}
print(ps.suggest(item))

cm = ChatModerator()
print(cm.moderate("This is stupid. Call me at +91 98765 43210. Visit http://spam.me now!!!"))
PY
```

## Notes

- Python 3.10+ recommended.
- No private keys required to run the default agents.
- Code is typed and documented for readability.
