import json
import os
import binance_con
import strategy

import_path = 'settings.json'

#import settings
def get_settings(import_path):
    if os.path.exists(import_path):
        file = open(import_path, 'r')
        project_settings = json.load(file)
        file.close()
        return project_settings
    else:
        return ImportError

def execute_analysis_and_trade(sell_or_buy):
    project_settings = get_settings(import_path)
    api_key = project_settings['BinanceKeys']['API_Key']
    secret_key = project_settings['BinanceKeys']['Secret_Key']

    ETH = project_settings['Token']['ETH']
    BTCB = project_settings['Token']['BTCB']
    BUSD = project_settings['Token']['BUSD']

    account = binance_con.query_account(api_key, secret_key)
    if account['canTrade']:
        print('Your account is ready to trade')

        #Caculate the current ratio
        reference_ratio = strategy.check_pair_relation(ETH, BTCB, 'bsc')
        current_ratio = strategy.check_pair_relation(BUSD, BTCB, 'bsc')

        print(f'Reference ratio: {reference_ratio}')
        print(f'Current ratio: {current_ratio}')

        #Caculate the diff between ratios
        check = strategy.check_ratio_ralation(current_ratio, reference_ratio)
        asset_list = binance_con.query_quote_asset_list('BTC')
        eth_pair = asset_list.loc[asset_list['symbol'] == 'ETHBTC']
        symbol = eth_pair['symbol'].values[0]
        if check and sell_or_buy == 'buy':
            print('Buying time: ')
            analysis = strategy.analyze_symbols(eth_pair, '1h', 0.000001, 'buy')
            if analysis:
                print('buying ETH')
                params = strategy.caculate_buy_params(symbol, eth_pair, '1h')
                response = binance_con.make_trade_with_params(
                    params, project_settings
                )
                print(response)
            else:
                print('Not buying ETH')
                print(f'The analysis is {analysis}')
        else:
            if sell_or_buy == 'sell':
                print('Selling time:')
                analysis = strategy.analyze_symbols(eth_pair, '1h', 0.000001, 'sell')
                if analysis:
                    print('selling ETH')
                    params = strategy.caculate_sell_params(symbol, eth_pair, '1h')
                    response = binance_con.make_trade_with_params(
                        params, project_settings
                    )
                    print(response)
                else:
                    print('Not selling ETH')
                    print(f'The analysis is {analysis}')


