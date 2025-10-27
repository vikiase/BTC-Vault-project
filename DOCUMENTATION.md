# BTC Vault V1.0 Documentation

## Overview
**BTC Vault** is a Python-based command-line application designed to automate Bitcoin (BTC) investment strategies, primarily focusing on Dollar-Cost Averaging (DCA). The application interacts with the Coinmate API to execute trades directly on the user's account. It includes features for managing API credentials, encrypting sensitive data, and automating investment processes.

---

## File Descriptions

### `security.py`
Handles encryption and decryption of sensitive data, such as API credentials and DCA strategy settings.

#### Key Functions:
1. **`generate_key_from_password(password: str, salt: bytes) -> bytes`**  
   - Derives a cryptographic key from a password using PBKDF2 with SHA256.
   - Returns: A 32-byte key encoded in Base64.

2. **`encrypt_json_to_file(data: dict, file_path: str, password: str)`**  
   - Encrypts a JSON object and saves it to a file.
   - Adds a `magic_key` for validation during decryption.

3. **`decrypt_json_from_file(file_path: str, password: str) -> dict`**  
   - Decrypts a JSON file and validates its integrity using the `magic_key`.

---

### `models.py`
Contains backend functions for interacting with the Coinmate API and retrieving cryptocurrency data.

#### Key Functions:
1. **`get_api_credentials(public_key, private_key, client_id) -> tuple`**  
   - Generates a nonce and HMAC signature for API authentication.

2. **`get_btc_current_price() -> dict`**  
   - Fetches the current BTC price in CZK and USD.

3. **`get_btc_change() -> float`**  
   - Retrieves the 24-hour percentage change in BTC price.

4. **`get_last_transaction(public_key, signature, client_id, nonce) -> int`**  
   - Retrieves the ID of the last transaction.

5. **`make_limit_order(limit_price, amount, client_id, public_key, nonce, signature)`**  
   - Places a limit buy order for BTC.

6. **`make_instant_order(amount, client_id, public_key, nonce, signature)`**  
   - Places an instant buy order for BTC.

7. **`get_balances(client_id, public_key, nonce, signature) -> tuple`**  
   - Retrieves account balances for CZK, BTC, and ETH.

---

### `console.py`
Provides the main user interface and command-line functionality for managing DCA strategies, viewing BTC prices, and editing API credentials.

#### Key Functions:
1. **DCA Strategy Management**:
   - **`view_dca()`**: Displays current DCA strategy settings and statistics.
   - **`edit_dca()`**: Edits existing DCA strategy settings.
   - **`edit_btc_dca()`**: User can add a transaction to the strategy.
   - **`create_dca()`**: Creates a new DCA strategy.
   - **`start_dca()`**: Starts a new DCA strategy.
   - **`stop_dca()`**: Stops the current DCA strategy.

2. **BTC Price Tracking**:
   - **`btc()`**: Displays the current BTC price and 24-hour change.

3. **API Credentials Management**:
   - **`save_credentials(public_key, private_key, client_id)`**: Saves encrypted API credentials.
   - **`load_credentials()`**: Loads and decrypts API credentials.
   - **`credentials()`**: Edits API credentials.

4. **Automated Buying**:
   - **`set_limit_buy()`**: Places a limit buy order for the DCA strategy.
   - **`cancel_limit_buy()`**: Cancels a pending limit buy order.
   - **`auto_buy()`**: Places an instant buy order for the DCA strategy.

---

### `daily.py`
Automates the execution of DCA strategies on scheduled days. This script should be run everyday for example by cron or systemd timer.

#### Workflow:
1. Decrypts the DCA strategy file.
2. Checks if the current date matches the scheduled investment date.
3. Executes the DCA strategy using the `dca_day()` function from `console.py`.
4. Updates the next investment date in the DCA strategy file.

---

### `pass.bin`
File used for **automatic** encryption and decryption.
- Should be stored somewhere safe, for example AWS has its tools for safe storage of keys.

---

### `credentials.json`
Encrypted file storing API credentials (public key, private key, client ID).

---

### `dca_strategy.json`
Encrypted file storing DCA strategy settings, including investment amount, frequency, price limit, and statistics.

---

## Usage

### Commands
- **help**: Display available commands.
- **exit**: Exit the program.
- **view_dca**: View DCA strategy information and statistics.
- **edit_dca**: Edit DCA strategy settings.
- **start_dca**: Start a new DCA strategy.
- **stop_dca**: Stop the current DCA strategy.
- **btc**: View current BTC price and statistics.
- **credentials**: Edit API credentials.

### First-Time Setup
1. Run the program and follow the prompts to set up your password and API credentials.
2. Your credentials will be encrypted and stored securely.

### Automated DCA Execution
Schedule the `daily.py` script to run daily using systemd timers on Linux. The script will automatically execute DCA strategies on scheduled days.

#### Systemd Timer Setup (Ubuntu/Linux)
1. **Create Service File**  
   Create `/etc/systemd/system/btc-vault.service`:

```[Unit]
Description=BTC Vault Daily Script
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
User=vv
WorkingDirectory=/home/vv/BTC Vault
ExecStart=/usr/bin/python3 '/home/vv/BTC Vault/daily.py'
```

2. **Create Timer File**  
Create `/etc/systemd/system/btc-vault.timer`:

```[Unit]
Description=BTC Vault Daily Timer
[Timer]
OnCalendar=12:00
Persistent=true
[Install]
WantedBy=timers.target
```

3. **Activate Timer**  
`$ sudo systemctl enable btc-vault.timer`
`$ sudo systemctl start btc-vault.timer`


**Note**: The `Persistent=true` setting ensures missed executions (e.g., when the system is off) run on the next system boot.

---

## Security
- Sensitive data is encrypted using the `cryptography` library.
- A password-based key is derived using PBKDF2 with a salt.
- Ensure the `pass.bin` is stored securely.

---

## Limitations
- The program assumes the presence of working Coinmate API connection.

---

## Author
Viktor Vyhnalek, 2025

---

## Disclaimer
This program is provided as-is and is intended for educational purposes. Use it at your own risk. Always verify the security of your API keys and credentials.
