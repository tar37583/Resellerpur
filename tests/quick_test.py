
from agents.price_suggestor import PriceSuggestor
from agents.chat_moderation import ChatModerator
from agents.llm_utils import search_online_prices

ps = PriceSuggestor.from_csv("data/listings.csv")
item = {
    "category": "Mobile",
    "brand":"Apple",
    "condition":"Good",
    "age_months":30,
    "asking_price":55000,
    "location":"Mumbai",
    "title":"Iphone 13"
}
print("Price Suggestion:\n", ps.suggest(item))

cm = ChatModerator()
print("\nModeration:\n", cm.moderate("Great deal bro!! WhatsApp me at 98765-43210, click here: http://bit.ly/deal"))

