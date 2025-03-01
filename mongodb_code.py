import pymongo
import requests
from datetime import datetime

# MongoDB connection string (using default localhost and port)
MONGO_URI = "mongodb://localhost:27017/"

# MongoDB database and collection names
DB_NAME = "market_data"
NEWS_COLLECTION = "market_news"
SENTIMENT_COLLECTION = "market_sentiment"

# Connect to MongoDB
def connect_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

# Fetch market news (example)
def fetch_market_news(symbol):
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,  # Example stock symbol (e.g., 'AAPL')
        'apikey': ''  # Replace with your API key
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Print the raw response to inspect its structure
    print(data)  # Inspect the raw response (optional)
    return data.get('feed', [])

# Insert market news into MongoDB collection
def insert_market_news(symbol, news_data, db):
    collection = db[NEWS_COLLECTION]
    for news in news_data:
        # Extract relevant data from the news entry
        title = news.get('title', 'No title available')  # Default if missing
        summary = news.get('summary', 'No summary available')  # Default if missing
        url = news.get('url', 'No URL available')  # Default if missing

        # Insert the news article into the collection
        collection.update_one(
            {'url': url},  # Ensure the URL is unique
            {'$set': {'symbol': symbol, 'headline': title, 'date': datetime.now(), 'summary': summary}},
            upsert=True
        )

# Example main function to fetch and insert news into MongoDB
def main():
    symbol = 'AAPL'  # Example stock symbol
    news_data = fetch_market_news(symbol)

    # Connect to MongoDB
    db = connect_mongo()

    # Insert fetched market news into MongoDB
    insert_market_news(symbol, news_data, db)

    print(f"Inserted {len(news_data)} news articles for {symbol}")

if __name__ == '__main__':
    main()
