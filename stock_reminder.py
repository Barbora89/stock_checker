import requests
import os
import json

STOCKS = {
    "GEN": {"above": 29.00}
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
    
    # Zjistíme, jak byl skript v GitHub Actions spuštěn
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    is_manual_run = (event_name == "workflow_dispatch")

    if is_manual_run:
        print("🤖 Skript byl spuštěn RUČNĚ. Cache bude pro toto spuštění ignorována.")

    for ticker, thresholds in STOCKS.items():
        try:
            #price = get_price(ticker)
            #test check prices 
            price = 100
            print(f"{ticker}: ${price:.2f}")

            key_above = f"{ticker}_above"
            if thresholds.get("above"):
                if price >= thresholds["above"]:
                    # ZMĚNA: Notifikace odejde, pokud stav ještě není v cache NEBO pokud skript pouštíte ručně
                    if not state.get(key_above) or is_manual_run:
                        notify(f"📈 {ticker} roste!", f"Cena ${price:.2f}")
                        state[key_above] = True
                    else:
                        print(f"ℹ️ {ticker} je nad hranicí, ale upozornění už v cache existuje.")
                else:
                    state[key_above] = False

        except Exception as e:
            print(f"Chyba u {ticker}: {e}")

    save_state(state)
