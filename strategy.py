import pandas as pd
import numpy as np
import binance_con
import time
import requests

#convert data from binance candlestick to dataframe
def get_and_transform_data(symbol, timeframe, numberr_of_candles):
    raw_data = binance_con.get_candlestick_data(
        symbol, timeframe, numberr_of_candles
    )

    df = pd.DataFrame(raw_data)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df['RedOrGreen'] = np.where((df['open'] < df['close']), 'Green', 'Red')
    print(df['RedOrGreen'])
    #return dataframe
    return df

#get token price
def get_token_price(address, chain):
    #make api call to get the price
    url = f'http://127.0.0.1:5002/getPrice?chain={chain}&address={address}'
    response = requests.get(url)
    data = response.json()

    #Extract the price
    usd_price = data['usdPrice']

    return usd_price

#check the pair relation
def check_pair_relation(address1, address2, chain):
    price1 = get_token_price(address1, chain)
    price2 = get_token_price(address2, chain)

    #Caculate ratio of the prices
    ratio = price1 / price2

    return ratio

def check_ratio_ralation(current_ratio, reference_ratio):
    #caculate the diff between the ratios
    #ratio 1 = token1 / token 3
    #ratio 2 = token 2 / token 3
    if current_ratio > reference_ratio:
        #The current ratio is overvalued relative to the reference ratio
        # Consider selling token1 for token 3
        return False
    elif current_ratio < reference_ratio:
        #the current ratio is undervalued relative to the reference ratio
        #Consider buying Token1 with Token 3
        return True

#Check the consecutive raise or decrease
def determine_trade_event(symbol, timeframe, percentage_change, candle_color):
    candlestick_data = get_and_transform_data(symbol, timeframe, 3)
    #Review if candles as the same color
    if(candlestick_data.loc[0, 'RedOrGreen'] == candle_color
            and candlestick_data.loc[1, 'RedOrGreen'] == candle_color
            and candlestick_data.loc[1, 'RedOrGreen'] == candle_color):
        #Determine thhe percentage change
        change_one = determine_percent_change(
            candlestick_data.loc[0, 'open'], candlestick_data.loc[0, 'close']
        )
        change_two = determine_percent_change(
            candlestick_data.loc[1, 'open'], candlestick_data.loc[1, 'close']
        )
        change_three = determine_percent_change(
            candlestick_data.loc[2, 'open'], candlestick_data.loc[2, 'close']
        )

        if candle_color == 'Red':
            print(f'First Drop: {change_one}')
            print(f'Second Drop: {change_two}')
            print(f'Third Drop: {change_three}')
        elif candle_color == 'Green':
            print(f'First Drop: {change_one}')
            print(f'Second Drop: {change_two}')
            print(f'Third Drop: {change_three}')

        #Compare the price changes agains stated percentage change

        #The minimun treshold of increase or decrease we want to see in the price
        #In order to make the sell/but decision worth it
        if (abs(change_one) >= percentage_change
                and abs(change_two) >= percentage_change
                and abs(change_three) >= percentage_change):
            #We can trade
            return True
        else:
            return False
    else:
        return False


def determine_percent_change(close_previous, close_current):
    return (close_current - close_previous) / close_previous

def analyze_symbols(symbol_dataframe, timeframe, percentage, type):
    #Iterate through all the symbols
    for index in symbol_dataframe.index:
        #Analyze symbol
        if type == 'buy':
            analysis = determine_trade_event(
                symbol_dataframe['symbol'][index],
                timeframe,
                percentage,
                'Green',
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive rises')
            else:
                print(f'{symbol_dataframe["symbol"][index]} dose not have 3 consecutive rises')

            time.sleep(1)

            return analysis
        elif type == 'sell':
            analysis = determine_trade_event(
                symbol_dataframe['symbol'][index],
                timeframe,
                percentage,
                'Red',
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive drop')
            else:
                print(f'{symbol_dataframe["symbol"][index]} dose not have 3 consecutive drop')

            time.sleep(1)

            return analysis

#Buying params func
def caculate_buy_params(symbol, pair, timeframe):
    #retrieve the candle data
    raw_data = binance_con.get_candlestick_data(symbol, timeframe, 1)
    #determine the precision
    precision = pair.iloc[0]['baseAssetPrecision']
    #Filters
    filters = pair.iloc[0]['filters']
    for f in filters:
        if f['filterType'] == 'LOT_SIZE':
            step_size = float(f['stepSize'])
            min_qty = float(f['minQty'])
        elif f['filterType'] == 'PRICE_FILTER':
            tick_size = float(f['tickSize'])

    #caculate close price
    close_price = raw_data[0]['close']
    print(f'The close price is {close_price}')
    #caculate the buy stop. this will be 1% of the previous closing price
    buy_stop = close_price * 1.01
    print(f'the sell stop price {buy_stop}')
    #round the buy stop price to the nearest valid tick size
    buy_stop = round(buy_stop / tick_size) * tick_size
    print(f'the round buy stop price {buy_stop}')
    #caculate the quantity. This will be the buy stop
    raw_quantity = 0.1 / buy_stop
    print(f'raw quantity is {raw_quantity}')
    #round
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    params = {
        'symbol': symbol,
        'side': 'BUY',
        'type': 'STOP_LOSS_LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': buy_stop,
        'trailingDelta': 100
    }

    return params

#Selling params func
def caculate_sell_params(symbol, pair, timeframe):
    #retrieve the candle data
    raw_data = binance_con.get_candlestick_data(symbol, timeframe, 1)
    #determine the precision
    precision = pair.iloc[0]['baseAssetPrecision']
    #Filters
    filters = pair.iloc[0]['filters']
    for f in filters:
        if f['filterType'] == 'LOT_SIZE':
            step_size = float(f['stepSize'])
            min_qty = float(f['minQty'])
            break

    #extract close price
    close_price = raw_data[0]['close']
    print(f'the close price {close_price}')
    #caculate the sell stop. this will be 0.99% of the previous closing price
    sell_stop = close_price * 0.99
    print(f'the sell stop price {sell_stop}')
    #caculate the quantity. This will be 100 /sell_stop
    raw_quantity = 0.1 / sell_stop
    print(f'raw quantity is {raw_quantity}')
    #round
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    print(f'the quantity is {quantity}')

    params = {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'STOP_LOSS_LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': close_price,
        'trailingDelta': 100
    }

    return params
