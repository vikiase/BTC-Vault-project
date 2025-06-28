import models
import os
from datetime import datetime, timedelta
from getpass import getpass
import security
import sys

def help():
    print('Available commands:')
    print('1. help - Show this help message')
    print('2. exit - Exit the program')
    print('3. view_dca - View DCA strategy information and statistics')
    print('4. edit_dca - Edit DCA strategy settings')
    print('5. start_dca - Start new DCA strategy (only 1 active at a time)')
    print('6. stop_dca - Stop the current DCA strategy')

    print('7. view_grid - View grid trading strategy information and statistics')
    print('8. edit_grid - Edit grid trading strategy settings')
    print('9. start_grid - Start new grid trading strategy (only 1 active at a time)')
    print('10. stop_grid - Stop the current grid trading strategy')

    print('11. btc - view current BTC price and statistics')
    print('12. credentials - edit API credentials (can not be viewed for security reasons)')


#DCA SETTINGS ----------------------------------------------------------------------------------------------------------
def view_dca():
    print('Viewing DCA strategy information...')
    try:
        dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
        if dca_strategy:
            print('Current DCA strategy settings:')
            print(f"Amount: {dca_strategy['amount']} CZK, Limit: {dca_strategy['limit']}%")
            print(f"Frequency: {dca_strategy['frequency']} days, Start Day: {dca_strategy['start_day']}\n")

            print('Current DCA strategy statistics (update every DCA day):')
            print(f'Average price: {format_price(dca_strategy["average_price"])} CZK')
            print(
                f"Fiat Amount: {models.get_btc_current_price()['CZK'] * dca_strategy['btc_amount']} CZK, BTC Amount: {dca_strategy['btc_amount']} BTC")
            print(
                f"Goal: {dca_strategy['goal']} CZK, completion: {round((dca_strategy['btc_amount'] * models.get_btc_current_price()['CZK']) / dca_strategy['goal'] * 100, 2)}%")

    except FileNotFoundError:
        print('No DCA strategy file found. Please start a new one.')

def edit_dca():
    try:
        dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
        if dca_strategy:
            print('Current DCA strategy settings:')
            print(f"Amount: {dca_strategy['amount']} CZK")
            print(f"Frequency: {dca_strategy['frequency']} days")
            print(f"Start Day: {dca_strategy['start_day']}")
            print(f"Limit: {dca_strategy['limit']}%")
            print(f"Goal: {dca_strategy['goal']} CZK")
            replace = input('Do you want to edit these settings? (yes/no)').strip().lower()

            if replace == 'yes':
                print('Editing DCA strategy settings...')
                create_dca()
            else:
                print('DCA strategy settings not changed.')

    except FileNotFoundError:
        print('No DCA strategy file found. Please start a new one.')


def create_dca():
    amount = input('Please enter the amount of CZK to invest each time (min. 50): ')
    frequency = input('Please enter the frequency of investments (1, 7, 14, or 30 days): ').strip()
    today = datetime.today()

    if frequency == '30':
        start_day = input('Please enter the start day of the month (1-28): ').strip()
        if start_day.isdigit() and 1 <= int(start_day) <= 28:
            start_day = int(start_day)
            if start_day <= today.day:
                if today.month == 12:
                    year = today.year + 1
                    month = 1
                else:
                    year = today.year
                    month = today.month + 1
            else:
                year = today.year
                month = today.month
            investment_date = datetime(year, month, start_day)

    elif frequency == '1':
        investment_date = today + timedelta(days=1)
        start_day = 0

    elif frequency in ['7', '14']:
        start_day = input('Please enter the start day of the week (0 = Monday, 6 = Sunday): ').strip()
        if start_day.isdigit() and 0 <= int(start_day) <= 6:
            start_day = int(start_day)
            weekday = today.weekday()
            delta_days = (start_day - weekday + 7) % 7 or 7
            investment_date = today + timedelta(days=delta_days)

        else:
            print("Invalid input. Please enter a number from 0 (Monday) to 6 (Sunday).")
            return
    else:
        print("Invalid frequency. Please enter 1, 7, 14, or 30.")
        return

    limit = input('Please enter your limit % change for buying (e.g. 5 for 5%, max 50): ')
    goal = input('Please enter your goal amount of CZK (fiat): ')

    if amount.isdigit() and int(amount)>=50 and frequency.isdigit() and limit.isdigit() and 50>=int(limit)>0 and goal.isdigit() and int(goal)>0:
        days_diff = (investment_date - today).days
        try:
            existing_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
            if existing_strategy:
                dca_strategy = {
                    'amount': int(amount),
                    'frequency': int(frequency),
                    'start_day': int(start_day),
                    'investment_date': investment_date.strftime('%Y-%m-%d'),
                    'limit': int(limit),
                    'goal': int(goal),
                    'btc_amount': existing_strategy['btc_amount'],
                    'average_price': existing_strategy['average_price'],
                    'number_of_investments': existing_strategy['number_of_investments'],
                }
                security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', password)

        except FileNotFoundError:
            dca_strategy = {
                'amount': int(amount),
                'frequency': int(frequency),
                'start_day': int(start_day),
                'investment_date': investment_date.strftime('%Y-%m-%d'),
                'limit': int(limit),
                'goal': int(goal),
                'btc_amount': 0,  # This will be updated during the DCA process
                'average_price': 0,  # This will be updated during the DCA process
                'number_of_investments': 0,  # This will be updated during the DCA process
            }
            security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', password)

        print('DCA strategy created successfully!')
        print(f'DCA strategy will start in {days_diff} day(s) on {investment_date.strftime("%Y-%m-%d")}.')
        
    else:
        print('Invalid input. Please enter numeric values for amount, frequency, limit, and goal.')

def start_dca():
    print('Starting new DCA strategy...')
    try:
        dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
        if dca_strategy:
            print('You already have an active DCA strategy. Do you wish to replace it? (yes/no)')
            replace = input().strip().lower()
            if replace == 'yes':
                create_dca()
            else:
                print('DCA strategy not started.')
    except FileNotFoundError:
        create_dca()

def stop_dca():
    print('Stopping DCA strategy...')
    try:
        dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)

        try:
            amount = dca_strategy['amount']
            credentials = load_credentials()
            if credentials[0] and credentials[1] and credentials[2]:
                nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                transaction_id = models.get_pending_dca_transaction(credentials[0], signature, credentials[2], nonce,
                                                                    amount)

                if transaction_id:
                    nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                    models.cancel_pending_dca_transaction(credentials[0], signature, credentials[2], nonce,
                                                          transaction_id)
                    print('Limit buy order cancelled successfully.')
        except TypeError:
            print('No pending limit buy order found or corrupted data.')

        os.remove('dca_strategy.json')
        print('DCA strategy stopped successfully.')
    except FileNotFoundError:
        print('No active DCA strategy found.')


#GRID SETTINGS - NOT IMPLEMENTED YET------------------------------------------------------------------------------------
def view_grid():
    print('Viewing grid trading strategy information...')
    try:
        pass # Here you would implement the logic to view grid trading strategy information
    except FileNotFoundError:
        print('No grid trading strategy found. Please start a new one.')

def edit_grid():
    print('Editing grid trading strategy settings...')
    try:
        pass # Here you would implement the logic to edit grid trading strategy settings
    except FileNotFoundError:
        print('No grid trading strategy found. Please start a new one.')

def create_grid():
    pass

def start_grid():
    print('Starting new grid trading strategy...')
    try:
        #najit soubor
        print('You already have an active grid trading strategy. Do you wish to replace it? (yes/no)')
        replace = input().strip().lower()
        if replace == 'yes':
            create_grid()
        else:
            print('Grid trading strategy not started.')
    except FileNotFoundError:
        create_grid()

def stop_grid():
    print('Stopping grid trading strategy...')
    try:
        # Here you would implement the logic to stop the grid trading strategy
        print('Grid trading strategy stopped successfully.')
    except FileNotFoundError:
        print('No active grid trading strategy found.')


# BTC PRICE ------------------------------------------------------------------------------------------------------------
def format_price(price):
    number = round(float(price))
    return f"{number:,}".replace(",", " ")

def btc():
    prices = models.get_btc_current_price()
    current_usd_price = format_price(prices['USD'])
    current_czk_price = format_price(prices['CZK'])

    change = models.get_btc_change()
    print(f'Current BTC price: {current_usd_price} USD / {current_czk_price} CZK')
    print(f'24h change: {change}%')

# CREDENTIALS ----------------------------------------------------------------------------------------------------------
def save_credentials(public_key, private_key, client_id):
    creds = {'public_key': public_key, 'private_key': private_key, 'client_id': client_id, 'ready': True}

    nonce, signature = models.get_api_credentials(public_key, private_key, client_id)
    if models.get_balances(client_id, public_key, nonce, signature) == None:
        print('Invalid credentials. Please check your public key, private key, and client ID.')
        return False
    security.encrypt_json_to_file(creds, 'credentials.json', password)
    print('Credentials saved successfully!')




def load_credentials():
    try:
        creds = security.decrypt_json_from_file('credentials.json', password)
        return creds['public_key'], creds['private_key'], creds['client_id']
    except FileNotFoundError:
        print('No credentials found. Please set your credentials first.')
        return None, None, None
def credentials():
    print('Editing credentials...')
    global public_key, private_key, client_id
    password = getpass('Please enter your password to edit credentials: ')
    public_key = input('Please enter your new public key: ')
    private_key = input('Please enter your new private key: ')
    client_id = input('Please enter your new client ID: ')
    save_credentials(public_key, private_key, client_id)

#COMMANDS FOR BUYING ---------------------------------------------------------------------------------------------------
def set_limit_buy():
    dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
    if dca_strategy:
        amount = dca_strategy['amount']
        limit = dca_strategy['limit']

        limit_price = models.get_dca_limit_price(limit)
        credentials = load_credentials()

        if credentials[0] and credentials[1] and credentials[2]:
            try:
                nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                models.make_limit_order(limit_price, amount, credentials[2], credentials[0], nonce, signature)
                print('Limit buy order placed successfully.')
            except Exception as e:
                print(f'Error placing limit buy order: {e}')
                return
        else:
            print('Credentials are not set.')
    else:
        print('No DCA strategy found')


def cancel_limit_buy():
    dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
    amount = dca_strategy['amount']
    credentials = load_credentials()
    if credentials[0] and credentials[1] and credentials[2]:
        try:
            nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
            transaction_id = models.get_pending_dca_transaction(credentials[0], signature, credentials[2], nonce,
                                                                amount)

            if transaction_id:
                nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                models.cancel_pending_dca_transaction(credentials[0], signature, credentials[2], nonce, transaction_id)
                print('Limit buy order cancelled successfully.')
                return True
            else:
                nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                last_id = models.get_last_transaction(credentials[0], signature, credentials[2], nonce)

                nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
                data = models.check_order_status(credentials[2], credentials[0], nonce, signature, last_id)
                amount_bought = float(data['trades'][0]['amount'])
                price_bought = data['trades'][0]['price']
                print(
                    f'Last transaction found: {last_id} - Amount bought: {amount_bought} BTC at price: {price_bought} CZK')

                dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
                dca_strategy['btc_amount'] += amount_bought / models.get_btc_current_price()['CZK']
                dca_strategy['number_of_investments'] += 1
                dca_strategy['average_price'] = (dca_strategy['average_price'] * dca_strategy[
                    'number_of_investments'] + float(price_bought) * amount_bought) / dca_strategy[
                                                    'number_of_investments']

                security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', password)
                print('No pending limit buy order found.')
        except Exception as e:
            print(f'Error cancelling limit buy order: {e}')
            return False

    else: print('Credentials are not set. Please set your API credentials first.')
    return False


def auto_buy():
    dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
    amount = dca_strategy['amount']
    credentials = load_credentials()

    if credentials[0] and credentials[1] and credentials[2]:
        try:
            nonce, signature = models.get_api_credentials(credentials[0], credentials[1], credentials[2])
            models.make_instant_order(amount, credentials[2], credentials[0], nonce, signature)
            print('Instant buy order placed successfully.')

            dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
            dca_strategy['btc_amount'] += amount / models.get_btc_current_price()['CZK']
            dca_strategy['number_of_investments'] += 1
            dca_strategy['average_price'] = (dca_strategy['average_price'] * dca_strategy['number_of_investments'] +
                                             models.get_btc_current_price()['CZK'] * amount) / dca_strategy[
                                                'number_of_investments']

            security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', password)
        except Exception as e:
            print(f'Error placing instant buy order: {e}')
            return

    else: print('Credentials are not set. Please set your API credentials first.')

#TIME RELATED FUNCIONALITY ---------------------------------------------------------------------------------------------
def dca_day():
    if cancel_limit_buy():
        auto_buy()
    set_limit_buy()

#MAIN LOOP -------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print(
        'Welcome to Crypto Vault!\nInvest in Bitcoin without worrying about your emotions. Your investing will be managed via Coinmate API.')
    print('Made by viktor vyhnalek, 2025')
    if os.path.exists('pass.bin'):
        password = input('Please enter your password to decrypt your credentials: ')
        data = security.decrypt_json_from_file('credentials.json', password)
        if data:
            print('User signed in successfully!\n')
        else:
            print('Decryption failed. Please check your password.')
            sys.exit(2)
    else:
        print('At first, we will need some information from you for the API connection.')

        password = input('Please enter your password to encrypt your credentials (remember it!!): ')
        with open('pass.bin', 'wb') as f:
            f.write(password.encode())

        public_key = input('Please enter your public key: ')
        private_key = input('Please enter your private key: ')
        client_id = input('Please enter your client ID: ')
        if client_id.isdigit():
            if save_credentials(public_key, private_key, client_id) == False:
                sys.exit(2)
        else:
            print('Invalid client ID. Please enter a numeric value.')
            sys.exit(2)

    while True:
        print(
            '------------------------------------------------------------------------------------------------------------')
        prompt = input('Enter command (type "help" for options): ').strip().lower()
        if prompt == 'help':
            help()
        elif prompt == 'exit':
            break
        elif prompt == 'view_dca':
            view_dca()
        elif prompt == 'edit_dca':
            edit_dca()
        elif prompt == 'start_dca':
            start_dca()
        elif prompt == 'stop_dca':
            stop_dca()

        elif prompt == 'view_grid':
            view_grid()
        elif prompt == 'edit_grid':
            edit_grid()
        elif prompt == 'start_grid':
            start_grid()
        elif prompt == 'stop_grid':
            stop_grid()

        elif prompt == 'btc':
            btc()
        elif prompt == 'credentials':
            credentials()
        else:
            print('Unknown command. Type "help" for options.')