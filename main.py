
import requests, json, os
from datetime import datetime

# Lista de métodos de pago permitidos para considerar una oferta como operable
METODOS_PERMITIDOS = ["UALA", "Global66", "Paypal", "Nequi"]

# URL del repositorio remoto de GitHub
remote_url = "https://github.com/wilycol/Arbitro-AI"

# Si el repositorio no está clonado localmente, clónalo
if not os.path.exists("Arbitro-AI"):
    os.system(f"git clone {remote_url}")

# Función para estructurar una oferta de cualquier exchange con campos estándar
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

# Función para obtener señales desde Binance
def obtener_binance(tipo):
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        datos = []
        side = "BUY" if tipo == "SELL" else "SELL"
        criptos = ["USDT", "USDC"]

        for cripto in criptos:
            page = 1
            while len([d for d in datos if d["cripto"] == cripto and d["tipo"] == tipo]) < 20 and page <= 5:
                payload = {
                    "page": page,
                    "rows": 20,
                    "payTypes": [],
                    "asset": cripto,
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
                            "link": f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={user['userNo']}",
                            "cripto": cripto,
                            "fiat": "COP"
                        }, "Binance", tipo))
                page += 1
        print(f"✅ Binance ({tipo}): {len(datos[:40])} señales")
        return datos[:40]
    except Exception as e:
        print(f"❌ Error en Binance ({tipo}):", e)
        return []

# Funciones vacías para OKX y Bybit por ahora
def obtener_okx(tipo): return []
def obtener_bybit(tipo): return []

# Selecciona las mejores 5 BUY y 5 SELL por exchange
def extraer_senales_destacadas(senales):
    destacadas = []
    for exchange in ["Binance", "OKX", "Bybit"]:
        buy = sorted([s for s in senales if s["exchange"] == exchange and s["tipo"] == "BUY"], key=lambda x: x["precio"])[:5]
        sell = sorted([s for s in senales if s["exchange"] == exchange and s["tipo"] == "SELL"], key=lambda x: x["precio"], reverse=True)[:5]
        destacadas.extend(buy + sell)
    return destacadas

# Función principal que orquesta todo el flujo
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

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        os.chdir("Arbitro-AI")
        os.system("git config --global user.name 'Wily Bot'")
        os.system("git config --global user.email 'wilycol492@gmail.com'")
        os.system("git remote set-url origin https://{}@github.com/wilycol/Arbitro-AI.git".format(token))
        os.system("git add public/*.json")
        os.system('git commit -m "🤖 Auto-update desde Render cron job"')
        os.system("git push origin main")
        os.chdir("..")
    else:
        print("❌ No se encontró la variable GITHUB_TOKEN. El push no se realizó.")

# Ejecuta la función principal si se corre el archivo directamente
if __name__ == "__main__":
    ejecutar()
