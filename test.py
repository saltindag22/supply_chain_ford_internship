import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # 🌟 Bu önemli!

mongo_uri = os.getenv("MONGO_URI")
print("MONGO_URI:", mongo_uri)  # Test için yazdır

client = MongoClient(mongo_uri)

try:
    client.admin.command('ping')
    print("✅ MongoDB bağlantısı başarılı.")
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")


"""- First, wait for autocomplete suggestions to appear.
    - If relevant suggestions are shown (e.g., contain location-specific or contextually enriched terms like "near me", "in Turkey"), **click the most appropriate suggestion** instead of pressing Enter.
    - If suggestions are not clickable or do not appear, **press Enter** to submit the query.
    - As a final fallback, click the “Google Search” button if it's available."""