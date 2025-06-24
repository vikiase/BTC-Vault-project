# Project Documentation - currently works only for ideal user, not tested yet :(

## Overview
This project is a Python-based application designed to manage cryptocurrency investments using the Coinmate API. It provides functionality for Dollar-Cost Averaging (DCA) and grid trading strategies, along with tools for viewing and managing Bitcoin prices and API credentials. Below is a detailed description of each `.py` file and its functions.

---

## `security.py`
This file handles encryption and decryption of sensitive data, key generation, and salt management.

### Functions:
1. **`generate_key_from_password(password: str, salt: bytes) -> bytes`**  
   - Derives a cryptographic key from a password using PBKDF2 with SHA256.
   - Parameters:
     - `password`: The user-provided password.
     - `salt`: A random salt for key derivation.
   - Returns: A 32-byte key encoded in Base64.

2. **`encrypt_json_to_file(data: dict, file_path: str, password: str)`**  
   - Encrypts a JSON object and saves it to a file.
   - Parameters:
     - `data`: The dictionary to encrypt.
     - `file_path`: Path to save the encrypted file.
     - `password`: Password used for encryption.

3. **`decrypt_json_from_file(file_path: str, password: str) -> dict`**  
   - Decrypts a JSON file and returns the data as a dictionary.
   - Parameters:
     - `file_path`: Path to the encrypted file.
     - `password`: Password used for decryption.
   - Returns: Decrypted data as a dictionary.

4. **`generate_salt()`**  
   - Generates a random salt and saves it to `salt.bin`.

5. **`get_salt() -> bytes`**  
   - Reads the salt from `salt.bin`.

6. **`save_key(key: bytes)`**  
   - Saves the cryptographic key to `key.bin`.

7. **`load_key() -> bytes`**  
   - Loads the cryptographic key from `key.bin`.

---

## `models.py`
This file contains backend functions for interacting with the Coinmate API and retrieving cryptocurrency data.

### Functions:
1. **`get_api_credentials(public_key, private_key, client_id) -> tuple`**  
   - Generates a nonce and HMAC signature for API authentication.
   - Returns: A tuple `(nonce, signature)`.

2. **`get_crypto_prices_usd() -> dict`**  
   - Fetches current cryptocurrency prices in USD from CryptoCompare API.
   - Returns: A dictionary of prices.

3. **`get_all_current_prices() -> tuple`**  
   - Fetches current cryptocurrency prices in CZK and USD.
   - Returns: A tuple `(czk_prices, usd_prices)`.

4. **`get_btc_current_price() -> dict`**  
   - Fetches the current Bitcoin price in CZK and USD.
   - Returns: A dictionary with prices.

5. **`get_btc_change() -> float`**  
   - Fetches the 24-hour percentage change in Bitcoin price.
   - Returns: Percentage change as a float.

6. **`get_last_transaction(public_key, signature, client_id, nonce) -> int`**  
   - Retrieves the ID of the last transaction.

7. **`get_pending_dca_transaction(public_key, signature, client_id, nonce, amount) -> int`**  
   - Finds a pending DCA transaction matching the specified amount.

8. **`cancel_pending_dca_transaction(public_key, signature, client_id, nonce, transaction_id) -> bool`**  
   - Cancels a pending DCA transaction.

9. **`get_dca_limit_price(limit) -> int`**  
   - Calculates the limit price for a DCA order based on the current price and limit percentage.

10. **`make_limit_order(limit_price, amount, client_id, public_key, nonce, signature)`**  
    - Places a limit buy order.

11. **`make_instant_order(amount, client_id, public_key, nonce, signature)`**  
    - Places an instant buy order.

12. **`check_order_status(client_id, public_key, nonce, signature, order_id) -> dict`**  
    - Checks the status of an order by its ID.

13. **`get_balances(client_id, public_key, nonce, signature) -> tuple`**  
    - Retrieves account balances for CZK, BTC, and ETH.

---

## `console.py`
This file provides the main user interface and command-line functionality. It is the main script using others like models.py and security.py. A script that is written to be **run every day at 11 AM**, which can be scheduled either using cron on a server or macOS/Linux machine, or by setting up a task in the Windows Task Scheduler on a local PC.

### Functions:
1. **`help()`**  
   - Displays available commands.

2. **`view_dca()`**  
   - Displays current DCA strategy settings and statistics.

3. **`edit_dca()`**  
   - Edits existing DCA strategy settings.

4. **`create_dca()`**  
   - Creates a new DCA strategy.

5. **`start_dca()`**  
   - Starts a new DCA strategy.

6. **`stop_dca()`**  
   - Stops the current DCA strategy.

7. **`view_grid()`**  
   - Displays grid trading strategy information (not implemented).

8. **`edit_grid()`**  
   - Edits grid trading strategy settings (not implemented).

9. **`start_grid()`**  
   - Starts a new grid trading strategy (not implemented).

10. **`stop_grid()`**  
    - Stops the current grid trading strategy (not implemented).

11. **`btc()`**  
    - Displays the current Bitcoin price and 24-hour change.

12. **`credentials()`**  
    - Edits API credentials.

13. **`set_limit_buy()`**  
    - Places a limit buy order for the DCA strategy.

14. **`cancel_limit_buy()`**  
    - Cancels a pending limit buy order.

15. **`auto_buy()`**  
    - Places an instant buy order for the DCA strategy.

16. **`dca_day()`**  
    - Executes the DCA strategy for the current day.

---

## `daily.py`
This file automates the execution of DCA strategies on scheduled days.

### Functions:
1. **`dca_day()`**  
   - Executes the DCA strategy for the current day.
   - Uses models.py (console.py) for interacting with Coinmate API.

### Workflow:
- Checks if the current date matches the scheduled investment date.
- Executes the DCA strategy using `dca_day()` from `console.py`.
- Updates the next investment date in the DCA strategy file.


## `salt.bin` and `key.bin`
These files are used for encryption and decryption:
- `salt.bin`: Contains the random salt used for key derivation.
- `key.bin`: Stores the derived cryptographic key.

---

## File Structure
- `security.py`: Handles encryption and decryption of sensitive data.
- `models.py`: Contains backend functions for API interaction and data retrieval.
- `console.py`: Provides the main user interface and command-line functionality.
- `daily.py`: Automates DCA strategy execution.
- `dca_strategy.json` File used for storing encrypted parameters and statistics of users DCA strategy.
- `credentials.json` File used for storing encrypted API credentials.
- `salt.bin` and `key.bin`: Files used for encryption and decryption. (not on Github because of security reasons)

---


## Author
Viktor Vyhnalek, 2025

---

## Disclaimer
This program is provided as-is and is intended for educational purposes. Use it at your own risk. Always verify the security of your API keys and credentials.
**Security hole**: your key is stored in `key.bin`. Anybody who gets access to your files can use it and read your API credentials. But nobody can withdraw from your account using these credentials.
