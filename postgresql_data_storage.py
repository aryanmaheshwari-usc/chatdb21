import requests
import psycopg2
from datetime import datetime

# PostgreSQL credentials
POSTGRES_HOST = "localhost"
POSTGRES_USER = "aryanmaheshwari"
POSTGRES_PASSWORD = "260302"  # Replace with your password
POSTGRES_DB = "market_data"

# Alpha Vantage API Key
API_KEY = 'YPOTFHH8QC9SOT9K'

# Connect to PostgreSQL
def connect_postgresql():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB
    )

# Fetch stock time series data (daily)
def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('Time Series (Daily)', {})

# Insert data into market_symbol table
def insert_market_symbol(symbol, company_name, sector, industry, connection):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO market_symbol (symbol, company_name, sector, industry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE 
        SET company_name = EXCLUDED.company_name, sector = EXCLUDED.sector, industry = EXCLUDED.industry
    """, (symbol, company_name, sector, industry))
    connection.commit()

    # Get the symbol_id for the inserted/updated symbol
    cursor.execute("SELECT id FROM market_symbol WHERE symbol = %s", (symbol,))
    symbol_id = cursor.fetchone()[0]
    return symbol_id

# Insert data into market_data table
def insert_market_data(data, symbol_id, connection):
    cursor = connection.cursor()
    for date, stats in data.items():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        cursor.execute("""
            INSERT INTO market_data (symbol_id, date, open_price, high_price, low_price, close_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (symbol_id, date_obj, stats['1. open'], stats['2. high'], stats['3. low'], stats['4. close'], stats['5. volume']))
    connection.commit()

# Main function to fetch and insert stock data
def main():
    symbol = 'AAPL'  # Change symbol as needed
    company_name = 'Apple Inc.'  # Example, modify if necessary
    sector = 'Technology'  # Example, modify if necessary
    industry = 'Consumer Electronics'  # Example, modify if necessary

    data = fetch_stock_data(symbol)

    # PostgreSQL connection
    postgres_connection = connect_postgresql()

    # Insert into market_symbol and get the symbol_id
    symbol_id = insert_market_symbol(symbol, company_name, sector, industry, postgres_connection)

    # Insert stock data into market_data
    insert_market_data(data, symbol_id, postgres_connection)

    postgres_connection.close()

if __name__ == '__main__':
    main()
