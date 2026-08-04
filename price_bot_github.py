import requests
import re
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = "8670693553:AAGlZ_zoagz18y-EZzrf4tqLfx0gCAzMbiA"
CHAT_ID = "524556830"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
}

SYMBOLS = {
    "price_dollar_rl": ("\U0001f1fa\U0001f1f8", "دلار آزاد"),
    "price_dollar_lr": ("\U0001f1f8\U0001f1ff", "دلار رسمی"),
    "crypto-tether-irr": ("\U0001f4b0", "تتر USDT"),
    "crypto-bitcoin": ("⚡", "بیتکوین"),
    "geram18": ("\U0001f48e", "طلای 18 عیار هر گرم"),
    "mesghal": ("⬛", "مثقال طلا"),
    "sekee": ("\U0001f947", "سکه امامی"),
}

USD_SYMBOLS = {"crypto-bitcoin", "ons", "silver", "oil_brent"}


def fetch_prices():
    r = requests.get("https://www.tgju.org/", headers=HEADERS, timeout=20)
    r.raise_for_status()
    html = r.text
    results = {}
    pattern = r'data-market-row="([^"]+)"[^>]*?data-price="([^"]*)"'
    seen = set()
    for symbol, price_str in re.findall(pattern, html):
        if symbol in seen or symbol not in SYMBOLS or not price_str:
            continue
        seen.add(symbol)
        try:
            val = float(price_str.replace(",", ""))
            if val > 0:
                if symbol not in USD_SYMBOLS:
                    val = val / 10
                results[symbol] = val
        except:
            pass
    return results


def fmt(value):
    if value == 0:
        return "---"
    v = int(value)
    if v >= 1_000_000_000:
        return f"{v/1_000_000_000:.2f} milliard"
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f} M"
    return f"{v:,}"


def build_message(prices):
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(iran_tz).strftime("%H:%M")
    lines = [f"\U0001f4c8 به روز [{now}]", "━" * 28, ""]
    for symbol, (emoji, name) in SYMBOLS.items():
        price = prices.get(symbol, 0)
        if symbol == "crypto-bitcoin":
            if price > 0:
                lines.append(f"{emoji} {name}:")
                lines.append(f"   \U0001f1fa\U0001f1f8 ${price:,.2f}")
                dr = prices.get("price_dollar_rl", 0)
                if dr > 0:
                    lines.append(f"   \U0001f1ee\U0001f1f7 {fmt(price * dr)} T")
                lines.append("")
            continue
        lines.append(f"{emoji} {name}:")
        lines.append(f"   {fmt(price)} T")
        lines.append("")
    lines.extend(["━" * 28, "\U0001f501 Har saat", "\U0001f4dd tgju.org"])
    return "\n".join(lines)


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text}, timeout=15
    )
    return r.json()


if __name__ == "__main__":
    prices = fetch_prices()
    msg = build_message(prices)
    result = send(msg)
    print("OK" if result.get("ok") else f"Error: {result}")
