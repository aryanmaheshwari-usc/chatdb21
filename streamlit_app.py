import streamlit as st
import pymysql
import psycopg2
from psycopg2 import connect
from pymongo import MongoClient
import openai
from openai import OpenAI
from pprint import pprint
import re
import logging
import traceback

# ——— Set up logging ———
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# Set OpenAI API Key (replace with your actual key)
openai.api_key = ''

# MongoDB Connection
def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['market_data']
    return db

# MySQL Connection
def connect_mysql():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='market_data',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to handle MySQL queries
def handle_mysql_query(query):
    logger.debug(f"Attempting MySQL query: {query}")
    conn = None
    try:
        conn = connect_mysql()
        cursor = conn.cursor()
        cursor.execute(query)
        # If it's a SELECT, fetch results; otherwise commit
        if query.strip().lower().startswith('select'):
            rows = cursor.fetchall()
            logger.debug(f"Fetched {len(rows)} rows")
            result = rows
        else:
            conn.commit()
            affected = cursor.rowcount
            logger.debug(f"Query affected {affected} rows")
            result = [{"affected_rows": affected}]
    except Exception as e:
        logger.error("Error executing MySQL query", exc_info=True)
        result = f"Error executing MySQL query: {e}"
    finally:
        if conn:
            conn.close()
    return result

# Function to handle MongoDB queries
def handle_mongo_query(query):
    db = connect_mongo()
    match = re.search(r"find\(\s*{\s*'symbol'\s*:\s*'([^']+)'\s*}\s*\)", query, re.IGNORECASE)
    if match:
        symbol = match.group(1)
        try:
            logger.debug(f"Running MongoDB find for symbol: {symbol}")
            result = list(db.market_news.find({'symbol': symbol}))
            logger.debug(f"MongoDB returned {len(result)} documents")
        except Exception as e:
            logger.error("Error executing MongoDB query", exc_info=True)
            result = f"Error executing MongoDB query: {e}"
    else:
        result = "Could not parse symbol from query. Ensure your query includes something like {'symbol': 'AAPL'}."
    return result

# Function to use OpenAI GPT to convert natural language into database query
def generate_database_query(natural_language_query: str, db_type: str):
    client = OpenAI(api_key=openai.api_key)
    
    if db_type == "MySQL":
        schema_context = (
            "You are a helpful assistant that generates valid SQL queries for MySQL. "
            "The schema is as follows:\n\n"
            "1) Table `market_symbol`:\n"
            "   • `symbol` VARCHAR(10) PRIMARY KEY\n"
            "   • `company_name` VARCHAR(255)\n"
            "   • `sector` VARCHAR(255)\n"
            "   • `industry` VARCHAR(255)\n\n"
            "2) Table `market_data`:\n"
            "   • `symbol` VARCHAR(10)\n"
            "   • `date` DATE\n"
            "   • `open_price`, `high_price`, `low_price`, `close_price` DECIMAL(10,2)\n"
            "   • `volume` BIGINT\n"
            "   • PRIMARY KEY(symbol, date)\n"
            "   • FOREIGN KEY(symbol) REFERENCES market_symbol(symbol)\n\n"
            "3) Table `technical_indicators`:\n"
            "   • `symbol` VARCHAR(10)\n"
            "   • `date` DATE\n"
            "   • `indicator_type` VARCHAR(20)  -- e.g. 'SMA','EMA','WMA','DEMA'\n"
            "   • `indicator_value` DECIMAL(12,6)\n"
            "   • PRIMARY KEY(symbol, date, indicator_type)\n"
            "   • FOREIGN KEY(symbol) REFERENCES market_symbol(symbol)\n\n"
            "Guidelines:\n"
            "- When you need price history, query `market_data`.\n"
            "- For company metadata, join to `market_symbol`:\n"
            "    e.g. `JOIN market_symbol m ON m.symbol = d.symbol`\n"
            "- For indicator queries, join to `technical_indicators` on symbol+date.\n"
            "- Always filter by the ticker (e.g. WHERE symbol = 'AAPL'), not by numeric ID.\n"
            "- Use `CURDATE()` and `INTERVAL` for date math.\n"
            "- Return ONLY the SQL query (no explanation or commentary)."
        )
    elif db_type == "MongoDB":
        schema_context = (
        "You are a helpful assistant that generates valid MongoDB queries. "
        "Collections:\n"
        "- `market_news`       (_id, url, date, headline, summary, symbol)\n"
        "- `market_sentiment`  (_id, news_url, sentiment, sentiment_score, symbol, timestamp)\n"
        "- `earnings_transcripts` (_id, symbol, quarter, call_date, transcript, sentiment_summary, timestamp)\n"
        "Return only a `db.market_news.find({...})`, `db.market_sentiment.find({...})`, or `db.earnings_transcripts.find({...})` string."
    )

    else:
        schema_context = "Invalid database type provided."
    
    messages = [
        {"role": "system",  "content": schema_context},
        {"role": "user",    "content": f"Convert the following request into a valid query: {natural_language_query}"}
    ]
    
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    return completion.choices[0].message.content.strip()

# Streamlit app with LLM integration and radio buttons
def main():
    st.title("Database Query Interface with LLM")
    st.write("Select a database service and enter your natural language query below:")
    
    db_choice = st.radio("Select Database Service:", ["MySQL", "PostgreSQL", "MongoDB"])
    query_input = st.text_area("Enter your query:")
    
    if st.button("Submit"):
        if not query_input:
            st.write("Please enter a query.")
            return

        generated_query = generate_database_query(query_input, db_choice)
        st.write(f"Generated Query: {generated_query}")
        
        if db_choice == "MySQL":
            result = handle_mysql_query(generated_query)
            st.write("MySQL Query Result:")
            st.write(result)
        elif db_choice == "MongoDB":
            result = handle_mongo_query(generated_query)
            st.write("MongoDB Query Result:")
            st.write(result)
        else:
            st.write("Invalid database selection.")

if __name__ == "__main__":
    main()
