import os
from datetime import datetime, timedelta
from console import dca_day
import security
import sys


if not os.path.exists('pass.bin'):
    sys.exit("Key file not found. Please run the setup script to generate a key.")
else:
        with open('pass.bin', 'rb') as f:
            password = f.read().decode()  

try:
    dca_strategy = security.decrypt_json_from_file('dca_strategy.json', password)
    frequency = dca_strategy['frequency']
    investment_date = datetime.strptime(dca_strategy['investment_date'], '%Y-%m-%d')
    today = datetime.today()

    if investment_date.date() == today.date():
        dca_day()
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

        elif frequency in ['7', '14']:
            start_day = input('Please enter the start day of the week (0 = Monday, 6 = Sunday): ').strip()
            if start_day.isdigit() and 0 <= int(start_day) <= 6:
                start_day = int(start_day)
                weekday = today.weekday()
                delta_days = (start_day - weekday + 7) % 7 or 7
                investment_date = today + timedelta(days=delta_days)

        dca_strategy['investment_date'] = investment_date.strftime('%Y-%m-%d')
        security.encrypt_json_to_file(dca_strategy, 'dca_strategy.json', password)
    else: print('Today is not the scheduled investment date. No action taken.')

except (FileNotFoundError, ValueError):
    print('DCA strategy not found or decryption failed. Please check the file and key.')