from pynput import keyboard
import MetaTrader5 as mt5
import pandas as pd
import submodules.moving_average as moving_average
import datetime
# module for trading manually
# 
# space = set sl to long MA
# - = buy
# * = sell

SYMBOL = '[DAX30]'
TRADE_RISK = 0.4
SMA = 50
TIMEFRAME = mt5.TIMEFRAME_M1
volume = 0.5

if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

point = mt5.symbol_info(SYMBOL).point

def buy():
    print("buy")
    request = {}
    active_order = mt5.positions_get(symbol = SYMBOL)

    if(len(active_order) != 0):  
        df=pd.DataFrame(list(active_order),columns=active_order[0]._asdict().keys())
        
        order_type = df["type"][0]

        if(order_type == 1):
            request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": int(df['ticket'][0]),
                    "type": mt5.ORDER_TYPE_BUY,
                    "symbol": SYMBOL,
                    "volume": float(df["volume"][0]),
                    "type_filling": mt5.ORDER_FILLING_IOC,
                    }
            print("closing position")
    else:
        request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "magic": 10,
                    "comment": "manual-trade",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
    if(bool(request)):
        mt5.order_send(request)
        print("opening order")

def sell():
    print("sell")
    request = {}
    active_order = mt5.positions_get(symbol = SYMBOL)

    if(len(active_order) != 0):  
        df=pd.DataFrame(list(active_order),columns=active_order[0]._asdict().keys())
        
        order_type = df["type"][0]

        if(order_type == 0):
            request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": int(df['ticket'][0]),
                    "type": mt5.ORDER_TYPE_SELL,
                    "symbol": SYMBOL,
                    "volume": float(df["volume"][0]),
                    "type_filling": mt5.ORDER_FILLING_IOC,
                    }
            print("closing position")
    else:
        request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": SYMBOL,
                    "volume": volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "magic": 10,
                    "comment": "manual-trade",
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
    if(bool(request)):
        mt5.order_send(request)
        print("opening order")

def sl():
    print("sl")

    active_order = mt5.positions_get(symbol = SYMBOL)
    if(len(active_order) != 0):
        df=pd.DataFrame(list(active_order),columns=active_order[0]._asdict().keys())

        now = datetime.datetime.now()
        rates = mt5.copy_rates_from(SYMBOL, TIMEFRAME, now + datetime.timedelta(hours=3), SMA*2)
        ticks_frame = pd.DataFrame(rates)
        #moving average berechnen und einfügen
        ticks_frame['sma'] = moving_average.sma(ticks_frame, SMA)

        new_sl = ticks_frame['sma'][SMA*2-1]

        request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": int(df['ticket'][0]),
                    "sl": float(new_sl),
                    "type_time": mt5.ORDER_FILLING_IOC,
                }
        mt5.order_send(request)

def vol_up():
    global volume
    volume += 0.1
    volume = round(volume,1)

    print("volume increased to: ", volume)

def vol_down():
    global volume
    volume -= 0.1
    volume = round(volume,1)
    
    print("volume decreased to: ", volume)

def on_press(key):
    try:
        #print('alphanumeric key {0} pressed'.format(
        #    key))
        
        if(str(key) == 'Key.up'):
            vol_up()
        elif(str(key) == 'Key.down'):
            vol_down()

        if(key.char == '*'):
            sell()
        elif(key.char == '-'):
            buy()        

    except AttributeError:
        pass
        
        

def on_release(key):
    if(str(key) == 'Key.space'):
            sl()
    if key == keyboard.Key.esc:
        # Stop listener
        return False

print("""Controls:
*: sell
-: buy
space: set sl to 50 SMA
arrow-up: increase volume by 0.1 (standard: 0.5)
arrow-down: decrease volume by 0.1
esc: exit the program""")

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()