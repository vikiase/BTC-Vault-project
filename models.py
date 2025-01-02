import requests
from datetime import datetime, timedelta
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
        response.raise_for_status()
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

#vraci {'CZK': 2360202, 'USD': 96576.58}
def get_btc_current_price():
    url = "https://coinmate.io/api/ticker?currencyPair=BTC_CZK"
    result = {}
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result['CZK'] = data['data']['last']
    except requests.exceptions.RequestException as e:
        print(f"Nastala chyba při získávání dat: {e}")
        return None

    url = "https://min-api.cryptocompare.com/data/pricemulti"
    symbols = "BTC"
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
        result['USD'] = formatted_data['BTC/USD']

    except requests.exceptions.RequestException as e:
        print(f"Chyba při získávání dat: {e}")
        return None
    return result

#vraci float
def get_btc_change():
    # Coinmate API pro CZK
    url = "https://coinmate.io/api/ticker?currencyPair=BTC_CZK"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        change = data['data']['change']
        change = round(change, 2)
        return change
    except requests.exceptions.RequestException as e:
        print(f"Nastala chyba při získávání dat z Coinmate: {e}")
        return None


def format_float(value):
    if value.is_integer():
        integer_part = "{:,}".format(int(value)).replace(",", " ")
        return integer_part
    else:
        integer_part, decimal_part = str(value).split(".")
        integer_part = "{:,}".format(int(integer_part)).replace(",", " ")
        formatted_value = f"{integer_part}.{decimal_part}"
        return formatted_value





