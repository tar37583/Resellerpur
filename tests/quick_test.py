
from agents.price_suggestor import PriceSuggestor
from agents.chat_moderation import ChatModerator

ps = PriceSuggestor.from_csv("data/listings.csv")
item = {
    "category": "Laptop",
    "brand":"Apple",
    "condition":"Good",
    "age_months":30,
    "asking_price":55000,
    "location":"Mumbai",
    "title":"MacBook Air 2020"
}
print("Price Suggestion:\n", ps.suggest(item))

cm = ChatModerator()
print("\nModeration:\n", cm.moderate("Great deal bro!! WhatsApp me at 98765-43210, click here: http://bit.ly/deal"))
