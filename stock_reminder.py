import requests
import os
import json

STOCKS = {
    "GEN": {"above": 24}
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
STATE_FILE = "alert_state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_price(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data["c"]


def notify(title, message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"**{title}** {message}"})


def check_prices():
    state = load_state()

    for ticker, thresholds in STOCKS.items():
        try:
            price = get_price(ticker)
            print(f"{ticker}: ${price:.2f}")

            key_above = f"{ticker}_above"
            if thresholds.get("above"):
                if price > thresholds["above"]:
                    if not state.get(key_above):
                        notify(f"📈 {ticker} roste!", f"Cena ${price:.2f}")
                        state[key_above] = True
                else:
                    state[key_above] = False

        except Exception as e:
            print(f"Chyba u {ticker}: {e}")

    save_state(state)


check_prices()
