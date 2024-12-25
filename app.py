from flask import Flask, render_template, jsonify
import json
from models import get_all_current_prices, get_prices_for_graph
app = Flask(__name__)


def load_historical_prices():
    try:
        with open('historical_data.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Chyba při načítání historických dat: {e}")
        return json.load(f)


@app.route('/')
def prices():
    czk_prices, usd_prices = get_all_current_prices()

    # Sloučení cen do jednoho slovníku pro přehlednost
    combined_prices = {}
    for pair in czk_prices:
        # Zajistíme, že cena v USD je k dispozici
        usd_price = usd_prices.get(pair.replace("CZK", "USD"), 'Není dostupná')  # Upravujeme klíč pro správný formát
        combined_prices[pair] = {
            'CZK': czk_prices[pair],
            'USD': usd_price
        }

    historical_prices = load_historical_prices()
    return render_template('prices.html', current_prices=combined_prices, historical_prices=historical_prices)


# API endpoint pro získání aktuálních cen
@app.route('/api/current_prices', methods=['GET'])
def current_prices_api():
    czk_prices, usd_prices = get_all_current_prices()
    combined_prices = {}
    for pair in czk_prices:
        combined_prices[pair] = {
            'CZK': czk_prices[pair],
            'USD': usd_prices.get(pair)
        }

    return jsonify(combined_prices)

# API endpoint pro získání historických cen
@app.route('/api/historical_prices', methods=['GET'])
def historical_prices_api():
    historical_prices = load_historical_prices()
    return jsonify(historical_prices)

if __name__ == '__main__':
    app.run(debug=True)

