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
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_price(ticker):
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "c" not in data:
        raise ValueError(f"Odpověď z Finnhub API neobsahuje cenu. Odpověď: {data}")
        
    return data["c"]


def notify(title, message):
    if DISCORD_WEBHOOK_URL:
        # Přidali jsme uložení odpovědi, abychom viděli chyby komunikace
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": f"**{title}** {message}"})
        if response.status_code == 204:
            print("🚀 Notifikace úspěšně odeslána na Discord.")
        else:
            print(f"❌ Discord odmítl notifikaci (Status: {response.status_code}): {response.text}")
    else:
        print("⚠️ Notifikace neodeslána: DISCORD_WEBHOOK_URL je prázdný!")


def check_prices():
    state = load_state()
    
    # OPRAVA: GitHub Actions standardně plní proměnnou GITHUB_EVENT_NAME malými písmeny, 
    # nebo používáme vestavěnou proměnnou GITHUB_WORKFLOW_REF / GITHUB_EVENT_NAME.
    # Pro jistotu zkontrolujeme obě varianty (velká i malá písmena).
    event_name = os.environ.get("GITHUB_EVENT_NAME", "").lower()
    is_manual_run = (event_name == "workflow_dispatch")

    if is_manual_run:
        print("🤖 Skript detekoval RUČNÍ SPUŠTĚNÍ (workflow_dispatch). Cache bude ignorována!")

    for ticker, thresholds in STOCKS.items():
        try:
            price = get_price(ticker)
            print(f"Sledovaný ticker {ticker}: Aktuální cena je ${price:.2f} (Hranice je ${thresholds['above']:.2f})")

            key_above = f"{ticker}_above"
            if thresholds.get("above"):
                if price >= thresholds["above"]:
                    # Zpráva odejde, pokud stav není v cache NEBO pokud skript pouštíte ručně
                    if not state.get(key_above) or is_manual_run:
                        notify(f"📈 {ticker} roste!", f"Cena ${price:.2f}")
                        state[key_above] = True
                    else:
                        print(f"ℹ️ {ticker} je nad hranicí, ale upozornění už v cache existuje.")
                else:
                    print(f"📉 {ticker} je pod hranicí. Nastavuji stav na False.")
                    state[key_above] = False

        except Exception as e:
            print(f"❌ Chyba u {ticker}: {e}")

    save_state(state)


check_prices()
