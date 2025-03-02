import streamlit as st
import pymysql
import psycopg2
from pymongo import MongoClient
from pprint import pprint

# Function to connect to MySQL database
def connect_mysql():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='market_data',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Function to connect to PostgreSQL database
def connect_postgres():
    connection = psycopg2.connect(
        host="localhost",
        database="market_data",
        user="",
        password=""
    )
    return connection

# Function to connect to MongoDB
def connect_mongo():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['market_data']
    return db

# Function to handle MySQL queries
def handle_mysql_query(query):
    db_connection = connect_mysql()
    cursor = db_connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    db_connection.close()
    return result

# Function to handle PostgreSQL queries
def handle_postgres_query(query):
    db_connection = connect_postgres()
    cursor = db_connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    db_connection.close()
    return result

# Function to handle MongoDB queries
def handle_mongo_query(query):
    db = connect_mongo()
    symbol = query.split('symbol')[-1].strip()  # Simple parsing for 'symbol'
    result = db.market_news.find({'symbol': symbol})
    return list(result)

# Streamlit app
def main():
    st.title("Database Query Interface")
    query = st.text_area("Enter your query:")

    if st.button("Submit"):
        if query.lower().startswith('select'):
            if "mysql" in query.lower():
                result = handle_mysql_query(query)
                st.write("MySQL Query Result:")
                st.write(result)
            elif "postgres" in query.lower():
                result = handle_postgres_query(query)
                st.write("PostgreSQL Query Result:")
                st.write(result)
            else:
                st.write("Invalid database type in the query.")
        elif "symbol" in query.lower():
            result = handle_mongo_query(query)
            st.write("MongoDB Query Result:")
            pprint(result)
            st.write(result)
        else:
            st.write("Invalid query format. Please check your query.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
