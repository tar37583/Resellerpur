# Resellpur AI Agents

This project implements **AI-powered agents** for a resale marketplace (Resellpur).  
It includes two main agents and one utility function:

1. **Price Suggestor** – suggests a fair price range for items using:
   - Dataset comparables (nearest neighbors),
   - Baseline depreciation formula,
   - Live **online search results** (`search_online_prices` via LLM),
   - LLM-generated reasoning.

2. **Chat Moderator** – uses an LLM to classify messages as:
   - `safe`, `abusive`, `spam`, or `contains_phone`,
   - Returns structured JSON with `status` and `reason`.

3. **`search_online_prices` helper** – defined in `llm_utils.py`,  
   queries OLX, Cashify, Quikr, etc. (via Grok/LLM) to fetch resale prices  
   and is used by the Price Suggestor.

---

## 🚀 Features
- FastAPI backend with interactive Swagger UI (`/docs`).
- Modular `agents/` folder with:
  - `price_suggestor.py`
  - `chat_moderation.py`
  - `llm_utils.py` (centralized LLM + web helpers)
- JSON outputs for assignment compliance:
  - **Price Suggestor:** `{ "fair_price_range": "...", "reasoning": "..." }`
  - **Chat Moderator:** `{ "status": "...", "reason": "..." }`
- `.env` support for API keys (secure, not in repo).

---

## 🛠️ Setup

### 1. Clone repo
```bash
git clone https://github.com/your-username/resellpur-agents.git
cd resellpur-agents
```

### 2. Create virtual environment
```bash
python -m venv ass
ass\Scripts\activate    # Windows
# or
source ass/bin/activate # Linux / Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Create a `.env` file in the project root:

```
GROK_API_KEY=your_api_key_here
```

---

## ▶️ Running the Server

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📡 API Endpoints

### 1. Price Suggestion
`POST /negotiate`

Request:
```json
{
  "title": "iPhone 12",
  "category": "Mobile",
  "brand": "Apple",
  "condition": "Good",
  "age_months": 24,
  "asking_price": 35000,
  "location": "Mumbai"
}
```

Response:
```json
{
  "fair_price_range": "22800 – 33700",
  "reasoning": "Your iPhone 12 (Apple, Good, 24 months old) was valued using dataset comparables, depreciation baseline, and online market prices. Web comparables: olx.in: ₹32,000, cashify.in: ₹30,500 – ₹33,000. The blended central price is ~₹28,200, so a reasonable range is ₹22,800 – ₹33,700."
}
```

---

### 2. Chat Moderation
`POST /moderate`

Request:
```json
{
  "message": "This is stupid. Call me at +91 9876543210"
}
```

Response:
```json
{
  "status": "abusive",
  "reason": "The message contains abusive language ('stupid') and shares a phone number."
}
```

---

## 🧩 Project Structure
```
resellpur-agents/
├── agents/
│ ├── price_suggestor.py
│ ├── chat_moderation.py
│ ├── llm_utils.py # contains search_online_prices() and LLM helpers
├── data/
│ └── resellpur_data.csv # dataset for comparables
├── quick_test/
│ └── test_requests.py # scripts/notebooks for quick API testing
├── app.py # FastAPI entrypoint
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```


---

## 👨‍💻 Author
*Developed by Tarang* — for the **AI Intern Project Assessment (Resellpur)**.
