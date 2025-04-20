import requests
import pymysql
from datetime import datetime

# MySQL credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "market_data"

# Alpha Vantage API Key
API_KEY = 'YPOTFHH8QC9SOT9K'

def connect_mysql():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

def create_tables():
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS market_symbol (
            symbol VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            sector        VARCHAR(255) NOT NULL,
            industry      VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS market_data (
            symbol     VARCHAR(10),
            date       DATE,
            open_price  DECIMAL(10,2),
            high_price  DECIMAL(10,2),
            low_price   DECIMAL(10,2),
            close_price DECIMAL(10,2),
            volume      BIGINT,
            PRIMARY KEY(symbol, date),
            FOREIGN KEY(symbol) REFERENCES market_symbol(symbol)
        );
        """
    ]
    conn = connect_mysql()
    cur = conn.cursor()
    for q in ddl:
        cur.execute(q)
    conn.commit()
    cur.close()
    conn.close()

def fetch_stock_data(symbol):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY
    }
    response = requests.get(url, params=params)
    json_data = response.json()

    if 'Time Series (Daily)' not in json_data:
        print("❌ Error in API response:", json_data.get("Note") or json_data.get("Error Message") or "Unknown error")
        return {}

    print(f"✅ Successfully fetched data for {symbol}")
    return json_data['Time Series (Daily)']

def upsert_market_symbol(symbol, company_name, sector, industry, conn):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO market_symbol(symbol, company_name, sector, industry)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          company_name=VALUES(company_name),
          sector=VALUES(sector),
          industry=VALUES(industry)
    """, (symbol, company_name, sector, industry))
    conn.commit()
    cur.close()

def insert_market_data(ts_data, symbol, conn):
    cur = conn.cursor()
    inserted, skipped = 0, 0

    for date_str, stats in ts_data.items():
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d').date()
            cur.execute("""
                INSERT INTO market_data(symbol, date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  open_price=VALUES(open_price),
                  high_price=VALUES(high_price),
                  low_price=VALUES(low_price),
                  close_price=VALUES(close_price),
                  volume=VALUES(volume)
            """, (
                symbol, dt,
                float(stats['1. open']), float(stats['2. high']),
                float(stats['3. low']), float(stats['4. close']),
                int(stats['5. volume'])  # Fix: '5. volume', not '6. volume'
            ))
            inserted += 1
        except Exception as e:
            skipped += 1
            print(f"❌ Error on date {date_str}: {e}")

    conn.commit()
    cur.close()
    print(f"📥 Inserted {inserted} rows, Skipped {skipped} rows.")

def main():
    create_tables()

    # Example stock info
    symbol       = 'AAPL'
    company_name = 'Apple Inc.'
    sector       = 'Technology'
    industry     = 'Consumer Electronics'

    conn = connect_mysql()

    # Insert symbol into market_symbol table
    upsert_market_symbol(symbol, company_name, sector, industry, conn)

    # Fetch and insert daily data
    ts_data = fetch_stock_data(symbol)
    if ts_data:
        print(f"🔢 Fetched {len(ts_data)} days of data for {symbol}")
        insert_market_data(ts_data, symbol, conn)

    conn.close()
    print("✅ Done. Check your MySQL database!")

if __name__ == '__main__':
    main()
