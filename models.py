
import json
from datetime import datetime
import requests

def get_crypto_prices_usd():
    url = "https://min-api.cryptocompare.com/data/pricemulti"
    symbols = "BTC,ETH,SOL,ADA,XRP,LTC"
    params = {
        'fsyms': symbols,
        'tsyms': 'USD',
        'api_key': '441a7354c3d3c3d98631c057f30c39805b793f677e7a1a22892c9b8230377b14'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        formatted_data = {}
        for crypto, price_data in data.items():
            formatted_data[f'{crypto}/USD'] = price_data['USD']
        return formatted_data

    except requests.exceptions.RequestException as e:
        print(f"Chyba při získávání dat: {e}")
        return None
def get_all_current_prices():
    url = "https://coinmate.io/api/tickerAll"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Zajistí, že dostaneme chybu při neplatném požadavku
        data = response.json()

        if data["error"]:
            print(f"Chyba: {data['errorMessage']}")
            return
        czk_prices = {}
        for pair, details in data["data"].items():
            pair = pair.replace('_', '/')
            czk_prices[pair] = details['last']

        for pair, last in list(czk_prices.items()):
            if pair[-3:] != 'CZK' or pair[:4] == 'USDT':
                czk_prices.pop(pair)
                continue
            if pair[:3] == 'ADA' or pair[:3] == 'XRP':
                czk_prices[pair] = round(last, 2)
            else:
                czk_prices[pair] = int(round(last, 0))

        usd_prices = get_crypto_prices_usd()
        for pair, last in list(usd_prices.items()):
            if pair[:3] == 'ADA' or pair[:3] == 'XRP':
                usd_prices[pair] = round(last, 3)
            elif pair[:3] == 'SOL' or pair[:3] == 'LTC':
                usd_prices[pair] = round(last, 2)
            else:
                usd_prices[pair] = int(round(last, 0))
        return czk_prices, usd_prices
    except requests.exceptions.RequestException as e:
        print(f"Nastala chyba při získávání dat: {e}")


def get_prices_for_graph():
    def get_historical_data_for_all_pairs(crypto_pairs, days, api_key):
        """
        Získá historická data pro více kryptoměnových párů za poslední 'days' dnů.
        :param crypto_pairs: Seznam měnových párů (např. ['BTC_USD', 'ETH_USD'])
        :param days: Počet dnů zpět (např. 365 pro poslední rok)
        :param api_key: API klíč pro CryptoCompare
        :return: Slovník s historickými daty pro každý měnový pár
        """
        historical_data = {}

        for pair in crypto_pairs:
            crypto_symbol, second_currency = pair.split('_')
            print(f"Získávání dat pro {pair}...")
            url = "https://min-api.cryptocompare.com/data/v2/histoday"
            params = {
                "fsym": crypto_symbol,
                "tsym": second_currency,
                "limit": days,
                "aggregate": 1,  # Agregace po dnech
                "toTs": int(datetime.now().timestamp()),  # Timestampt pro aktuální čas
                "api_key": api_key
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'Data' in data and 'Data' in data['Data']:
                    timestamps = [datetime.utcfromtimestamp(point['time']).isoformat() for point in
                                  data['Data']['Data']]
                    prices = [point['close'] for point in data['Data']['Data']]
                    historical_data[pair] = {'timestamps': timestamps, 'prices': prices}
                else:
                    print(f"Chyba při získávání dat pro {pair}: Data nejsou dostupná.")
            except requests.exceptions.RequestException as e:
                print(f"Chyba při získávání dat pro {pair}: {e}")

        return historical_data

    def save_to_json(data, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data byla uložena do souboru {filename}")
        except Exception as e:
            print(f"Chyba při ukládání do souboru: {e}")

    api_key = '441a7354c3d3c3d98631c057f30c39805b793f677e7a1a22892c9b8230377b14'
    crypto_pairs = [
        "BTC_USD", "ETH_USD",
        "SOL_USD", "XRP_USD",
        "LTC_USD", "ADA_USD"
    ]
    days = 365 * 5
    historical_data = get_historical_data_for_all_pairs(crypto_pairs, days, api_key)
    save_to_json(historical_data, "historical_data.json")


