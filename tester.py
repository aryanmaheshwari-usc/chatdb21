import streamlit as st
import pymysql
import mysql.connector
import psycopg2
from psycopg2 import connect
from pymongo import MongoClient
from pprint import pprint
import re

# MongoDB Connection
def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['market_data']
    return db

# MySQL Connection
def connect_mysql():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Pinnacle232',
        database='market_data'
    )
    return conn

# PostgreSQL Connection
def connect_postgresql():
    conn = connect(
        dbname="market_data", 
        user="aryanmaheshwari", 
        password="260302", 
        host="localhost"
    )
    return conn

# Function to handle MySQL queries
def handle_mysql_query(query):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Exception as e:
        result = f"Error executing MySQL query: {e}"
    finally:
        cursor.close()
        conn.close()
    return result

# Function to handle PostgreSQL queries
def handle_postgresql_query(query):
    conn = connect_postgresql()
    cursor = conn.cursor()
    # Replace table names to use PostgreSQL names:
    if "market_data" in query.lower():
        query = query.replace("market_data", "market_information")
    if "market_symbol" in query.lower():
        query = query.replace("market_symbol", "market_tickers")
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Exception as e:
        result = f"Error executing PostgreSQL query: {e}"
    finally:
        cursor.close()
        conn.close()
    return result

# Function to handle MongoDB queries
def handle_mongo_query(query):
    db = connect_mongo()
    # Attempt to parse a symbol from the query.
    symbol = None
    match = re.search(r"symbol\s*['=]\s*'([^']+)'", query, re.IGNORECASE)
    if match:
        symbol = match.group(1)
    if symbol:
        try:
            result = list(db.market_news.find({'symbol': symbol}))
        except Exception as e:
            result = f"Error executing MongoDB query: {e}"
    else:
        result = "Could not parse symbol from query. Ensure your query includes something like symbol='AAPL'."
    return result

# Streamlit app
def main():
    st.title("Database Query Interface")
    db_choice = st.radio("Select Database Service:", ["MySQL", "PostgreSQL", "MongoDB"])
    query = st.text_area("Enter your query:")
    
    if st.button("Submit"):
        if db_choice == "MySQL":
            result = handle_mysql_query(query)
            st.write("MySQL Query Result:")
            st.write(result)
        elif db_choice == "PostgreSQL":
            result = handle_postgresql_query(query)
            st.write("PostgreSQL Query Result:")
            st.write(result)
        elif db_choice == "MongoDB":
            result = handle_mongo_query(query)
            st.write("MongoDB Query Result:")
            pprint(result)
            st.write(result)
        else:
            st.write("Invalid database selection.")

if __name__ == "__main__":
    main()
