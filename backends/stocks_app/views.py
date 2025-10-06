from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import yfinance as yf
import numpy as np
import requests
import os
import json


import pandas as pd
#for converting into hours and min
from datetime import datetime

# alpha vantage API Key (set this securely)
STOCK_API_TOKEN = settings.STOCK_API_TOKEN # store in env vars

@api_view(['GET'])
def sma_trade(request):
    # ticker = request.GET.get('ticker', 'AAPL')

    '''url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={STOCK_API_TOKEN}'
    r = requests.get(url)
    data = r.json() #converts to python dict
    return data '''

    ticker = request.GET.get('ticker', 'AAPL')
    

    data = yf.download(ticker, start="2023-01-01",auto_adjust=True)
    #[('CLOSE','APPL'),('HIGH','APPL') ... ]
    #PREV data was multi-index so fix the level 1 so that we can access just the level 0
    

    data = data.xs(ticker,axis=1,level= 'Ticker')
    data.reset_index(inplace= True)
    data.columns = data.columns.str.lower()
    # print(data.columns) #Index(['close', 'high', 'low', 'open', 'volume'], dtype='object', name='Price')

    data['sma_50'] = data['close'].rolling(window=50).mean()
    data['sma_200'] = data['close'].rolling(window=200).mean()

    # Signal: 1 for buy, -1 for sell, 0 otherwise
    data['signal'] = 0

    # Calculate the signal only for the valid range
    signal_values = np.where(
        data['sma_50'][50:] > data['sma_200'][50:], 1, -1
    )
    data.iloc[50:, data.columns.get_loc('signal')] = signal_values
     # Generate buy/sell points only on crossovers
    data['position'] = data['signal'].diff()
    #last 500 entries
    data = data.tail(500)
    #use jsonify to convert into json array
    
    #to replace NAN to None
    clean_data = data.replace({np.nan: None})
    return JsonResponse(clean_data.to_dict(orient='records'),safe=False)
    # print( data.tail() )



    # o/p = [ {'close': 12.'high':555,..} ,{}]
    
#calculate rsi 
def calculate_rsi(series, period=14):
    delta = series.diff()
    # clip values lower than 0 and make it 0
    gain = delta.clip(lower=0)
    # clip values higher than 0 and make it 0

    # -1 makes negative diff positive
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


@api_view(['GET'])
def rsi_trade(request):
    ticker = 'AAPL'  
    data = yf.download(ticker, start="2023-01-01", auto_adjust=True)
    data = data.xs('AAPL', axis=1, level='Ticker')
    data.reset_index(inplace=True)
    data.columns = data.columns.str.lower()

    #rsi strategy
    data['rsi'] = calculate_rsi(data['close'], 14)

    # Generate buy/sell signals
    # Buy when RSI < 30, Sell when RSI > 70, else hold (0)
    data['position'] = 0
    data.loc[data['rsi'] < 30, 'position'] = 1  # buy
    data.loc[data['rsi'] > 70, 'position'] = -1  # sell
    # print(data.tail())

    #to replace NAN to None
    clean_data = data.replace({np.nan: None})
    return JsonResponse(clean_data.to_dict(orient='records'), safe=False)

    # print(data)
    # output includes list of dict [{'close', 'high', 'low', 'open', 'volumn', 'rsi',  'position'}]
    


   


    

