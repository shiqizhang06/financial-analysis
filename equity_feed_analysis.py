# pip install duckdb

import duckdb

print("DuckDB version:", duckdb.__version__)

# Connect to DuckDB
con = duckdb.connect()

# Load the CSV file into DuckDB
csv_file_path = "equity_feed.csv"  # Update this path to your CSV file
con.execute(""" 
    CREATE TABLE feed AS
    SELECT * FROM read_csv_auto('equity_feed.csv')
""")

# Sanity check: Show the first few rows of the table
result = con.execute("SELECT * FROM feed LIMIT 5").fetchdf()
print(result)

print(con.execute("SELECT COUNT(*) FROM feed").fetchdf())


# Helper so I don't retype the boilerplate
def q(sql):
    return con.execute(sql).fetchdf()


# Profiling checklist — write a query for each:

# Coverage per ticker — start date, end date, row count, per ticker. (One query exposes FALN's delisting, the FB→META handoff, and any short series at once.)
# Duplicates — any (ticker, date) appearing more than once?
# NULLs — count missing close per ticker.
# Sign violations — any row with a non-positive price?
# OHLC integrity — any row where open or close falls outside [low, high], or high < low?
# Name/entity scan — distinct company_name per ticker, and distinct tickers per company_name.

# 1. Coverage per ticker
coverage_query = q(
    "SELECT ticker, MIN(date) AS start_date, MAX(date) AS end_date, COUNT(*) AS days FROM feed GROUP BY ticker"
)
print(coverage_query)

# 2. Duplicates
duplicate_query = q(
    "SELECT ticker, date, COUNT(*) AS frequency FROM feed GROUP BY ticker, date HAVING COUNT(*) > 1"
)
print(duplicate_query)

# 3. NULLs
null_query = q(
    "SELECT ticker, COUNT(*) - COUNT(close) AS nulls FROM feed GROUP BY ticker"
)
print(null_query)

# 4. Non-positive price
nonpos_query = q(
    "SELECT date, ticker, close, open, high, low FROM feed WHERE close <= 0 OR open <= 0 OR high <= 0 OR low <= 0"
)
print(nonpos_query)

# 5. OHLC integrity
ohlc_query = q(
    "SELECT date, ticker, close, open, high, low FROM feed WHERE close NOT BETWEEN low AND high OR open NOT BETWEEN low AND high OR low > high"
)
print(ohlc_query)

# 6. Name/entity scan
name_query = q(
    "SELECT ticker, COUNT(DISTINCT company_name) AS distinct_company_name, STRING_AGG(DISTINCT company_name, ', ') AS details FROM feed GROUP BY ticker HAVING COUNT(DISTINCT company_name) > 1"
)
print(name_query)

entity_query = q(
    "SELECT company_name, COUNT(DISTINCT ticker) AS distinct_ticker, STRING_AGG(DISTINCT ticker, ', ') AS details FROM feed GROUP BY company_name HAVING COUNT(DISTINCT ticker) > 1"
)
print(entity_query)
