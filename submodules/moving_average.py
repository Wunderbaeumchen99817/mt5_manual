import pandas as pd

def sma(data, epochs):
    """returns SMA"""
    return data.low.rolling(epochs, min_periods= epochs).mean()

def ema(data, epochs):
    """returns EMA"""
    return data.close.ewm(span = epochs).mean()