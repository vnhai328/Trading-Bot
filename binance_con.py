from binance.spot import Spot
import pandas

#get status
def query_binance_status():
    status = Spot().system_status()
    if status["status"] == 0:
        return True
    else:
        raise ConnectionError

#get price of symbol
def query_account(api_key, secret_key):
    return Spot(
        base_url='https://testnet.binance.vision',
        api_key=api_key,
        api_secret=secret_key,
    ).account()

#query test net
def query_testnet():
    client = Spot(base_url='https://testnet.binance.vision')
    print(client.time())

#query candlestick data
def get_candlestick_data(symbol, timeframe, qty):
    raw_data = Spot().klines(symbol=symbol, interval=timeframe, limit=qty)
    converted_data = []

    for candle in raw_data:
        converted_candle = {
            "time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "close_time": candle[6],
            "quote_asset_volume": float(candle[7]),
            "number_of_trades": int(candle[8]),
            "taker_buy_base_asset_volume": float(candle[9]),
            "taker_buy_quote_asset_volume": float(candle[10]),
        }
        #add the data
        converted_data.append(converted_candle)

    return converted_data

#query all symbols from base asset
def query_quote_asset_list(quote_asset_symbol):
    symbol_dictionary = Spot().exchange_info()
    #convert to dataframe
    symbol_dataframe = pandas.DataFrame(symbol_dictionary['symbols'])
    #extract all symbol with base asset pair
    quote_symbol_df = symbol_dataframe.loc[
        symbol_dataframe['quoteAsset'] == quote_asset_symbol
    ]
    quote_symbol_df = symbol_dataframe.loc[
        symbol_dataframe['status'] == 'TRADING'
    ]
    #ETHSHIBA
    return quote_symbol_df

#function make trade with params
def make_trade_with_params(params, project_settings):
    print("Making trade with params")
    #Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    #create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #make the trade
    try:
        response = client.new_order(**params)
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')

#query to trades
def query_open_trades(project_settings):
    # Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    # create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #get Trades
    try:
        response = client.get_open_orders()
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')

#cancel a trade
def cancel_order_by_symbol(symbol, project_settings):
    # Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    # create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #cancle trade
    try:
        response = client.cancel_open_orders(symbol=symbol)
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')

#place a limit order for symbol
def place_limit_order(symbol, side, quantity, price, project_settings):
    # Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    # create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #place the limit order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            timeInForce='GTC',
            quantity=quantity,
            price=price
        )
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')

def place_stop_loss_order(
        symbol, side, quantity, stop_price, limit_price, project_settings
):
    # Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    # create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #place stop loss order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type='STOP_LOSS_LIMIT',
            timeInForce='GTC',
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price
        )
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')


def place_take_profit_order(
        symbol, side, quantity, stop_price, limit_price, project_settings
):
    # Set API key
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']
    # create client
    client = Spot(
        api_key=api_key,
        secret_key=secret_key,
        base_url='https://testnet.binance.vision'
    )

    #place stop loss order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type='TAKE_PROFIT_LIMIT',
            timeInForce='GTC',
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price
        )
        return response
    except ConnectionRefusedError as error:
        print(f'Error: {error}')

