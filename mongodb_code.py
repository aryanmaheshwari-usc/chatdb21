import pymongo
import requests
from datetime import datetime

# MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"

# Database and collection names
DB_NAME = "market_data"
NEWS_COLLECTION = "market_news"
SENTIMENT_COLLECTION = "market_sentiment"
TRANSCRIPT_COLLECTION = "earnings_transcripts"

# Connect to MongoDB
def connect_mongo():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

# Fetch market news
def fetch_market_news(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'apikey': 'YPOTFHH8QC9SOT9K'
    }
    response = requests.get(url, params=params)
    data = response.json()
    print("Raw News API Response:", data)
    return data.get('feed', [])

# Insert market news
def insert_market_news(symbol, news_data, db):
    news_collection = db[NEWS_COLLECTION]
    for news in news_data:
        title = news.get('title', 'No title available')
        summary = news.get('summary', 'No summary available')
        url = news.get('url', 'No URL available')
        time_str = news.get('time_published')

        if time_str:
            try:
                published_date = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            except Exception:
                published_date = datetime.now()
        else:
            published_date = datetime.now()

        news_collection.update_one(
            {'url': url},
            {'$set': {
                'symbol': symbol,
                'headline': title,
                'date': published_date,
                'summary': summary
            }},
            upsert=True
        )

# Insert sentiment data
def insert_market_sentiment(symbol, news_data, db):
    sentiment_collection = db[SENTIMENT_COLLECTION]
    for news in news_data:
        url = news.get('url', 'No URL available')
        sentiment = news.get('sentiment', 'unknown')
        sentiment_score = news.get('sentiment_score', None)

        sentiment_collection.update_one(
            {'news_url': url},
            {'$set': {
                'symbol': symbol,
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'timestamp': datetime.now()
            }},
            upsert=True
        )

# Fetch earnings transcript
def fetch_earnings_transcript(symbol, quarter):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "EARNINGS_CALL_TRANSCRIPT",
        "symbol": symbol,
        "quarter": quarter,
        "apikey": "YPOTFHH8QC9SOT9K"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print("Raw Earnings Transcript Response:", data)
    return data

# Insert earnings transcript
def insert_earnings_transcript(symbol, quarter, transcript_data, db):
    transcript_collection = db[TRANSCRIPT_COLLECTION]
    transcript_text = transcript_data.get("transcript", "Transcript not available")
    sentiment_summary = transcript_data.get("sentiment_summary", {})
    call_date = transcript_data.get("fiscalDateEnding", datetime.now().isoformat())

    transcript_doc = {
        "symbol": symbol,
        "quarter": quarter,
        "call_date": call_date,
        "transcript": transcript_text,
        "sentiment_summary": sentiment_summary,
        "timestamp": datetime.now()
    }

    transcript_collection.update_one(
        {"symbol": symbol, "quarter": quarter},
        {"$set": transcript_doc},
        upsert=True
    )

# Run everything
def main():
    symbol = "AAPL"
    quarter = "2024Q1"

    db = connect_mongo()

    # News and sentiment
    news_data = fetch_market_news(symbol)
    insert_market_news(symbol, news_data, db)
    insert_market_sentiment(symbol, news_data, db)

    # Earnings transcript
    transcript_data = fetch_earnings_transcript(symbol, quarter)
    insert_earnings_transcript(symbol, quarter, transcript_data, db)

    print(f"Done: News, Sentiment, and Transcript data inserted for {symbol} ({quarter})")

if __name__ == '__main__':
    main()
