import pandas as pd

df = pd.read_csv("equity_feed.csv", parse_dates=["date"])

# 1. dedupe (I found 12 XOM dups in SQL)
df = df.drop_duplicates()

# 2. sort so pct_change is chronological within each ticker
df = df.sort_values(by=['ticker', 'date'], ascending=[True, True])
print(df.head(20))

# 3. compute per-ticker daily return
df['ret'] = df.groupby('ticker')['close'].pct_change()
print(df.head(20))

# 4. surface the anomalies
flagged = df[df['ret'].abs() > 0.6]
print(flagged.sort_values(['ticker', 'date'])[['date', 'ticker', 'close', 'ret']])
print(df[(df['date'] > '2023-03-19') & (df['date'] < '2023-03-24') & (df['ticker'] == 'XOM')][['date', 'ticker', 'close', 'ret']])
print(df[(df['date'] > '2023-08-02') & (df['date'] < '2023-08-09') & (df['ticker'] == 'XOM')][['date', 'ticker', 'close', 'ret']])