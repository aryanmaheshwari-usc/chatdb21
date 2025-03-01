import openai
import pymongo
import mysql.connector
from psycopg2 import connect
from datetime import datetime
from pprint import pprint

# MongoDB Connection
def connect_mongo():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['market_data']
    return db

# MySQL Connection
def connect_mysql():
    conn = mysql.connector.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database='your_database'
    )
    return conn

# PostgreSQL Connection
def connect_postgresql():
    conn = connect(
        dbname="your_dbname", 
        user="your_user", 
        password="your_password", 
        host="localhost"
    )
    return conn

# Set OpenAI API Key
openai.api_key = ''

# Function to handle the LLM processing of the query
def process_natural_language_query(query):
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=f"Convert this natural language query into a SQL or MongoDB query: {query}",
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Example function to interact with MongoDB (find news by symbol)
def handle_mongo_query(query):
    db = connect_mongo()
    symbol = query.split('symbol')[-1].strip()  # Example simple parsing for 'symbol'
    result = db.market_news.find({'symbol': symbol})
    
    # Using pprint to pretty-print the result
    return pprint(list(result))

# Example function to interact with MySQL (simple select query)
def handle_mysql_query(query):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

# Example function to interact with PostgreSQL (simple select query)
def handle_postgresql_query(query):
    conn = connect_postgresql()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

# Function to detect the database from the query
def detect_database(query):
    if "symbol" in query.lower() or "news" in query.lower():
        return "mongodb"
    elif "select" in query.lower() or "from" in query.lower():
        return "sql"
    else:
        return "unknown"

# Function to process a natural language query and route it to the appropriate database
def handle_query(query):
    db_type = detect_database(query)
    
    if db_type == "mongodb":
        return handle_mongo_query(query)
    elif db_type == "sql":
        sql_query = process_natural_language_query(query)
        # You can choose MySQL or PostgreSQL here, depending on your need
        # Example: you can also route based on keywords like "stock" for MySQL and "financial" for PostgreSQL
        return handle_mysql_query(sql_query)  # Or handle_postgresql_query(sql_query)
    else:
        return "Unknown database type in query"

# Example query interaction
def main():
    query = "Show me news articles related to symbol AAPL"
    response = handle_query(query)
    print(response)

if __name__ == '__main__':
    main()
