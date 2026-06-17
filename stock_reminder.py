import yfinance as yf
import requests
import urllib3
import os
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STOCKS = {
    "GEN": {"above": 24}
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
STATE_FILE = "alert_state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def notify(title, message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": f"**{title}** {message}"}, verify=False)


def check_prices():
    state = load_state()
    session = requests.Session()
    session.verify = False

    for ticker, thresholds in STOCKS.items():
        try:
            stock = yf.Ticker(ticker, session=session)
            price = stock.fast_info["last_price"]
            print(f"{ticker}: ${price:.2f}")

            key_above = f"{ticker}_above"
            if thresholds.get("above"):
                if price > thresholds["above"]:
                    if not state.get(key_above):
                        notify(f"📈 {ticker} roste!", f"Cena ${price:.2f} je nad {thresholds['above']}")
                        state[key_above] = True
                else:
                    state[key_above] = False

        except Exception as e:
            print(f"Chyba u {ticker}: {e}")

    save_state(state)

check_prices()
