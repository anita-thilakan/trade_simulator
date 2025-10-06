from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import yfinance as yf
import requests
import os
import json

import pandas as pd
#for converting into hours and min
from datetime import datetime

# alpha vantage API Key (set this securely)
STOCK_API_TOKEN = settings.STOCK_API_TOKEN # store in env vars


def sma_trade(request):
    # ticker = request.GET.get('ticker', 'AAPL')

    '''url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={STOCK_API_TOKEN}'
    r = requests.get(url)
    data = r.json() #converts to python dict
    return data '''

    ticker = request.GET.get('ticker', 'AAPL')
    period = int(request.GET.get('period', 20))  # SMA period

    data = yf.download(ticker, period='3mo', interval='1d',auto_adjust=True)
    if data.empty:
        return Response({'error': 'No data found'}, status=404)

    # data['SMA'] = data['Close'].rolling(window=period).mean()
    # data['Signal'] = 0

    # Convert DataFrame index to string (e.g., date), then to dict
    data.reset_index(inplace=True)  # Convert index (DateTime) to column
    data_dict = data.to_dict(orient='records')  # List of dicts

    return json.dumps(data_dict)

    # data.loc[data['Close'] > data['SMA'], 'Signal'] = 1  # Buy
    # data.loc[data['Close'] < data['SMA'], 'Signal'] = -1  # Sell

    # result = data[['Close', 'SMA', 'Signal']].dropna().reset_index()
    # result['Date'] = result['Date'].astype(str)

    # return Response(result.to_dict(orient='records'))



    

