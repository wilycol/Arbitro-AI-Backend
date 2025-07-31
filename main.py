import requests, json, os
from datetime import datetime

METODOS_PERMITIDOS = ["UALA", "Global66", "Paypal", "Nequi"]

remote_url = "https://github.com/wilycol/Arbitro-AI"
if not os.path.exists("Arbitro-AI"):
    os.system(f"git clone {remote_url}")

def formatear_oferta(oferta, exchange, tipo):
    return {
        "exchange": exchange,
        "tipo": tipo,
        "cripto": oferta.get("cripto", "USDT"),
        "fiat": oferta.get("fiat", "COP"),
        "precio": float(oferta["precio"]),
        "min": int(oferta.get("min", 0)),
        "max": int(oferta.get("max", 0)),
        "nickname": oferta.get("nickname", ""),
        "metodos_pago": oferta.get("metodos_pago", []),
        "operable": any(m in METODOS_PERMITIDOS for m in oferta.get("metodos_pago", [])),
        "comision_aprox": round(float(oferta["precio"]) * 0.008, 2),
        "brecha": 0.0,
        "prioridad": 1,
        "link": oferta.get("link", ""),
        "reputacion": oferta.get("reputacion", "N/A")
    }

def obtener_binance(tipo):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    datos = []
    side = "BUY" if tipo == "SELL" else "SELL"
    page = 1
    while len(datos) < 20 and page <= 5:
        payload = {
            "page": page,
            "rows": 20,
            "payTypes": [],
            "asset": "USDT",
            "fiat": "COP",
            "tradeType": side
        }
        res = requests.post(url, json=payload)
        for item in res.json().get("data", []):
            adv = item["adv"]
            user = item["advertiser"]
            metodos = [m["tradeMethodName"] for m in adv.get("tradeMethods", [])]
            reputacion = f"{user.get('monthFinishRate', 0)*100:.2f}%" if user.get("monthFinishRate") else "N/A"
            if any(m in METODOS_PERMITIDOS for m in metodos):
                datos.append(formatear_oferta({
                    "precio": adv["price"],
                    "min": adv["minSingleTransAmount"],
                    "max": adv["maxSingleTransAmount"],
                    "nickname": user["nickName"],
                    "metodos_pago": metodos,
                    "reputacion": reputacion,
                    "link": f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={user['userNo']}"
                }, "Binance", tipo))
        page += 1
    print(f"✅ Binance {tipo}: {len(datos)} señales")
    return datos[:20]

def obtener_okx(tipo):
    url = "https://www.okx.com/v3/c2c/tradingOrders/books"
    datos = []
    side = "sell" if tipo == "BUY" else "buy"
    params = {
        "quoteCurrency": "COP",
        "baseCurrency": "USDT",
        "side": side,
        "paymentMethod": "",
        "userType": "all",
        "limit": "50"
    }
    res = requests.get(url, params=params)
    print(f"📦 Respuesta OKX {tipo}: {res.status_code}")
    print(res.text[:1000])

    for item in res.json().get("data", {}).get("orders", []):
        metodos = [m.upper() for m in item.get("paymentMethods", [])]
        if any(m in METODOS_PERMITIDOS for m in metodos):
            datos.append(formatear_oferta({
                "precio": item["price"],
                "min": item["minAmount"],
                "max": item["maxAmount"],
                "nickname": item["user"]["nickName"],
                "metodos_pago": metodos,
                "reputacion": item["user"].get("recentTradeCount", "N/A"),
                "link": "https://www.okx.com/p2p-market"
            }, "OKX", tipo))
    print(f"✅ OKX {tipo}: {len(datos)} señales")
    return datos[:20]

def obtener_bybit(tipo):
    url = "https://api2.bybit.com/fiat/otc/item/online"
    datos = []
    tradeType = "BUY" if tipo == "SELL" else "SELL"
    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "COP",
        "payment": [],
        "side": tradeType,
        "size": 50,
        "page": 1
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json=payload)
    print(f"📦 Respuesta Bybit {tipo}: {res.status_code}")
    print(res.text[:1000])

    for item in res.json().get("result", {}).get("items", []):
        metodos = [m.upper() for m in item.get("paymentMethods", [])]
        if any(m in METODOS_PERMITIDOS for m in metodos):
            datos.append(formatear_oferta({
                "precio": item["price"],
                "min": item["minAmount"],
                "max": item["maxAmount"],
                "nickname": item["nickName"],
                "metodos_pago": metodos,
                "reputacion": item.get("recentOrderNum", "N/A"),
                "link": "https://www.bybit.com/p2p"
            }, "Bybit", tipo))
    print(f"✅ Bybit {tipo}: {len(datos)} señales")
    return datos[:20]

def extraer_senales_destacadas(senales):
    destacadas = []
    for exchange in ["Binance", "OKX", "Bybit"]:
        buy = sorted([s for s in senales if s["exchange"] == exchange and s["tipo"] == "BUY"], key=lambda x: x["precio"])[:5]
        sell = sorted([s for s in senales if s["exchange"] == exchange and s["tipo"] == "SELL"], key=lambda x: x["precio"], reverse=True)[:5]
        destacadas.extend(buy + sell)
    return destacadas

def ejecutar():
    all_signals = []
    for tipo in ["BUY", "SELL"]:
        all_signals.extend(obtener_binance(tipo))
        all_signals.extend(obtener_okx(tipo))
        all_signals.extend(obtener_bybit(tipo))

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    output_folder = "Arbitro-AI/public"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(f"{output_folder}/datos_arbitraje.json", "w", encoding="utf-8") as f:
        json.dump(all_signals, f, indent=2, ensure_ascii=False)

    with open(f"{output_folder}/datos_arbitraje_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(all_signals, f, indent=2, ensure_ascii=False)

    destacadas = extraer_senales_destacadas(all_signals)
    with open(f"{output_folder}/destacadas_arbitraje.json", "w", encoding="utf-8") as f:
        json.dump(destacadas, f, indent=2, ensure_ascii=False)

    print(f"📊 Total señales generadas: {len(all_signals)}")
    print(f"🔹 Binance: {len([s for s in all_signals if s['exchange'] == 'Binance'])} señales")
    print(f"🔸 OKX: {len([s for s in all_signals if s['exchange'] == 'OKX'])} señales")
    print(f"🟣 Bybit: {len([s for s in all_signals if s['exchange'] == 'Bybit'])} señales")

    # Push con autenticación vía token
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        os.chdir("Arbitro-AI")
        os.system("git config --global user.name 'Wily Bot'")
        os.system("git config --global user.email 'wilycol492@gmail.com'")
        os.system("git remote set-url origin https://{}@github.com/wilycol/Arbitro-AI.git".format(token))
        os.system("git pull origin main --rebase")
        os.system("git add public/*.json")
        os.system('git commit -m "🤖 Auto-update desde Render cron job"')
        os.system("git push origin main")
        os.chdir("..")
    else:
        print("❌ No se encontró la variable GITHUB_TOKEN. El push no se realizó.")

if __name__ == "__main__":
    ejecutar()
