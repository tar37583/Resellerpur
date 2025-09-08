# Price negotiation
curl -X POST http://127.0.0.1:8000/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Mobile",
    "brand": "Apple",
    "condition": "Good",
    "age_months": 24,
    "asking_price": 34000,
    "location": "Mumbai",
    "title": "iPhone 12"
}'

# Moderation
curl -X POST http://127.0.0.1:8000/moderate \
  -H "Content-Type: application/json" \
  -d '{ "message": "This is stupid. Call me at +91 9876543210" }'
