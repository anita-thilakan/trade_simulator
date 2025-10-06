from django.urls import path
from .views import *

urlpatterns = [
    path('api/stock/sma/', sma_trade),
    path('api/stock/rsi/',rsi_trade),
]
