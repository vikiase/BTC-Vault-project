import requests
from datetime import datetime, timedelta
import hmac
import hashlib
from time import time


def get_api_credentials(client_id, public_key, private_key):
    def create_signature(client_id, public_key, private_key, nonce):
        message = f"{nonce}{client_id}{public_key}".encode('utf-8')
        signature = hmac.new(
            private_key.encode('utf-8'),
            message,
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature.upper()
    nonce = int(time() * 1000)
    signature = create_signature(client_id, public_key,private_key, nonce)
    return public_key, nonce, signature

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

def get_dca_transactions(public_key, signature, client_id, nonce, amount):
    url = 'https://coinmate.io/api/transactionHistory'
    params = {
        'offset': 0,
        'limit': 35,
        'sort': 'ASC',
        'timestampFrom': 1401390154803,
        'clientId': client_id,
        'publicKey': public_key,
        'nonce': nonce,
        'signature': signature
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=params, headers=headers)

    if response.status_code == 200:

        data = response.json()['data']

        buy_btc_transactions = []
        final = []
        for trans in data:
            if trans['transactionType'] == 'BUY' and trans['amountCurrency'] == 'BTC':
                buy = trans['price']*trans['amount']+trans['fee']
                if amount+1 > buy > amount-1:
                    buy_btc_transactions.append(trans)
        for transaction in buy_btc_transactions:
            t = {}
            t['amount'] = transaction['amount']
            t['price'] = transaction['price']
            t['date'] = datetime.fromtimestamp(transaction['timestamp']/1000).strftime('%Y-%m-%d')

            final.append(t)
        return final
    else:
        print(f"Error: {response.status_code}, {response.reason}")



