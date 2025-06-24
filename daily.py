import os
from datetime import datetime, timedelta
from console import dca_day
import security
import sys


if not os.path.exists('key.bin'):
    sys.exit("Key file not found. Please run the setup script to generate a key.")
else:
    key= security.load_key()
try:
    dca_strategy = security.decrypt_json_from_file('dca_strategy.json', key)
    frequency = dca_strategy['frequency']
    investment_date = datetime.strptime(dca_strategy['investment_date'], '%Y-%m-%d')
    today = datetime.today()

    if investment_date.date() == today.date():
        dca_day()
        if frequency != 30:
            dca_strategy['investment_date'] = (investment_date + timedelta(days=frequency)).strftime('%Y-%m-%d')
        else:
            dca_strategy['investment_date'] = datetime(today.year, today.month+1, today.day).strftime('%Y-%m-%d')

        security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', key)

except (FileNotFoundError, ValueError):
    print('DCA strategy not found or decryption failed. Please check the file and key.')