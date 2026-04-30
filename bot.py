import requests
import time
import json
import re
import os

TOKEN = os.getenv("8636562420:AAHyDJmo1cD1X7a2AnmGjbYiUP8v6j3TKrc")
CHAT_ID = os.getenv("739954208")

INTERVALO = 60

OBJETIVOS = [
    "nba","nfl","mlb","ufc","soccer",
    "lakers","celtics","warriors","heat",
    "mets","yankees","dodgers","braves"
]

enviadas = set()

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": msg})

def equipos(q):
    m = re.search(r"(.+?)\s+(vs\.?|v\.)\s+(.+)", q, re.I)
    return (m.group(1).strip(), m.group(3).strip()) if m else (None, None)

def score(prob, vol):
    s = 0
    if vol > 100000: s += 40
    elif vol > 50000: s += 30
    elif vol > 20000: s += 20

    if 0.4 <= prob <= 0.65: s += 25
    elif prob > 0.75: s -= 10

    return min(s, 100)

def run():
    url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=200"
    data = requests.get(url).json()

    for m in data:
        q = m.get("question", "")
        p = m.get("outcomePrices")
        vol = m.get("volume", 0)

        if not q or not p:
            continue

        if not any(x in q.lower() for x in OBJETIVOS):
            continue

        if "vs" not in q.lower():
            continue

        try:
            probs = [float(x) for x in json.loads(p)] if isinstance(p, str) else p
            prob = max(probs)
        except:
            continue

        sc = score(prob, vol)

        if sc < 50:
            continue

        key = q + str(prob)
        if key in enviadas:
            continue
        enviadas.add(key)

        eq1, eq2 = equipos(q)

        lado = eq1 if prob >= 0.5 else eq2

        msg = f"""
🔥 WHALE SIGNAL

🏟 {q}
📊 Prob: {prob*100:.1f}%
💰 Volumen: {vol}
🎯 Favor: {lado}

📈 Score: {sc}/100
"""

        enviar(msg)
        print("sent")

while True:
    print("running...")
    try:
        run()
    except:
        pass
    time.sleep(INTERVALO)