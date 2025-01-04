import requests
from datetime import datetime
import hmac
import hashlib
from time import time


# basic pro ziskani udaju na volani api. Vraci tuple (public_key, nonce, signature)
def get_api_credentials(client_id, public_key, private_key):
    def create_signature():
        message = f"{nonce}{client_id}{public_key}".encode('utf-8')
        signature = hmac.new(
            private_key.encode('utf-8'),
            message,
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature.upper()

    nonce = int(time() * 1000)
    signature = create_signature()
    return public_key, nonce, signature


# FRONTEND FUNKCE
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

# vraci {'CZK': 2360202, 'USD': 96576.58}
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


# vraci float % change
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


# -----------------------------------------------------------------------------------------------------------------------
# BACKEND FUNKCE

# abych nemusel porad volat
def get_btc_czk_price():
    url = "https://coinmate.io/api/ticker?currencyPair=BTC_CZK"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_price = data['data']['last']
        return current_price
    except requests.exceptions.RequestException as e:
        print(f"Nastala chyba při získávání dat: {e}")
        return None


# vraci id posledni transakce
def get_last_transaction(public_key, signature, client_id, nonce, amount):
    url = 'https://coinmate.io/api/transactionHistory'
    params = {
        'offset': 0,
        'limit': 1,
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
        return data[0]['orderId']
    else:
        print(f"Error: {response.status_code}, {response.reason}")


# vraci int Id Transakce
def get_pending_dca_transaction(public_key, signature, client_id, nonce, amount):
    url = 'https://coinmate.io/api/openOrders'
    params = {
        'clientId': client_id,
        'publicKey': public_key,
        'nonce': nonce,
        'signature': signature,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=params, headers=headers)
    if response.status_code == 200:
        data = response.json()['data']
        for transaction in data:
            buy = transaction['price'] * transaction['amount']
            if amount + 1 > buy > amount - 1:
                return transaction['id']
    else:
        print(f"Error: {response.status_code}, {response.reason}")


# vraci True
def cancel_pending_dca_transaction(public_key, signature, client_id, nonce, transaction_id):
    url = 'https://coinmate.io/api/cancelOrder'
    params = {
        'orderId': transaction_id,
        'clientId': client_id,
        'publicKey': public_key,
        'nonce': nonce,
        'signature': signature,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, data=params, headers=headers)
    if response.status_code == 200:
        print("Order cancelled")
        return True
    else:
        print(f"Error: {response.status_code}, {response.reason}")



# tvoreni objednavek
def get_dca_limit_price(limit):
    current_price = get_btc_czk_price()
    limit_price = int(float(current_price) - float(current_price) * limit / 100)
    return limit_price


def make_limit_order(limit_price, amount, client_id, public_key, nonce, signature):
    btc_amount = amount / limit_price
    btc_amount = float(f'{btc_amount:.8f}')
    data = {
        "amount": btc_amount,
        "currencyPair": "btc_czk",
        "price": limit_price,
        "clientId": client_id,
        "publicKey": public_key,
        "nonce": nonce,
        "signature": signature,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = "https://coinmate.io/api/buyLimit"
    response = requests.post(url, data=data, headers=headers)
    response_json = response.json()
    if not response_json.get("error", True):
        print("Request successful:", response_json)
    else:
        print("Error occurred:", response_json.get("errorMessage", "Unknown error"))

    return response_json

def make_instant_order(amount, client_id, public_key, nonce, signature):
    data = {
        "total": amount,
        "currencyPair": "btc_czk",
        "clientId": client_id,
        "publicKey": public_key,
        "nonce": nonce,
        "signature": signature
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    url = "https://coinmate.io/api/buyInstant"
    response = requests.post(url, data=data, headers=headers)
    response_json = response.json()
    if not response_json.get("error", True):
        print("Request successful:", response_json)
    else:
        print('aha')
        print("Error occurred:", response_json.get("errorMessage", "Unknown error"))


def check_order_status(client_id, public_key, nonce, signature, order_id):
    data = {
        "clientId": client_id,
        "publicKey": public_key,
        "nonce": nonce,
        "signature": signature,
        "orderId": order_id
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    url = "https://coinmate.io/api/orderById"
    response = requests.post(url, data=data, headers=headers)
    response_json = response.json()
    if not response_json.get("error", True):
        print("Request successful:", response_json)
        return response_json['data']['status']
    else:
        print("Error occurred:", response_json.get("errorMessage", "Unknown error"))
