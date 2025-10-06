import yfinance as yf

ticker = 'AAPL'
data = yf.download(ticker, period='1d', interval='1m')

print(data.head())
print(data.info())
