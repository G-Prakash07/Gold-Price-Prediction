import yfinance as yf
import pandas as pd

# Define ticker symbols
gold_ticker = 'GC=F'      # Gold Futures (in USD)
gbp_usd_ticker = 'GBPUSD=X'  # GBP to USD exchange rate

# Define the date range
end_date = pd.Timestamp.today()
start_date = end_date - pd.DateOffset(months=6)

# Download gold prices in USD
gold_data = yf.download(gold_ticker, start=start_date, end=end_date)['Close']

# Download GBP/USD exchange rate (we'll invert it to get USD to GBP)
exchange_data = yf.download(gbp_usd_ticker, start=start_date, end=end_date)['Close']

# Align the indices
combined = pd.concat([gold_data, exchange_data], axis=1)
combined.columns = ['Gold_USD', 'GBP_to_USD']
combined.dropna(inplace=True)

# Convert gold price from USD to GBP
combined['Gold_GBP'] = combined['Gold_USD'] / combined['GBP_to_USD']

# Print last few rows
print(combined.tail())

# Optional: Save to CSV
combined.to_csv('gold_prices_uk_6months.csv')