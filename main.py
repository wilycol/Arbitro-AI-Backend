
import requests
import json
from datetime import datetime

# Métodos de pago permitidos
metodos_pago_permitidos = ["NEQUI", "Paypal", "Global66", "UALA"]

# Criptomonedas objetivo
criptomonedas_objetivo = ["USDT", "USDC"]

# Moneda fiat
monedas_fiat = ["COP"]

# Función para obtener datos de Binance P2P
def obtener_datos_binance():
    datos = []
    for cripto in criptomonedas_objetivo:
        for fiat in monedas_fiat:
            for tipo in ["BUY", "SELL"]:
                try:
                    response = requests.post(
                        "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                        headers={"Content-Type": "application/json"},
                        json={
                            "asset": cripto,
                            "fiat": fiat,
                            "merchantCheck": False,
                            "page": 1,
                            "payTypes": [],
                            "publisherType": None,
                            "rows": 20,
                            "tradeType": tipo
                        },
                        timeout=10
                    )
                    ofertas = response.json()["data"]
                    for oferta in ofertas:
                        metodos_pago = oferta["adv"]["tradeMethods"]
                        metodos_validos = [
                            m["identifier"] for m in metodos_pago
                            if any(metodo.upper() in m["identifier"].upper() for metodo in metodos_pago_permitidos)
                        ]
                        if metodos_validos:
                            datos.append({
                                "exchange": "Binance",
                                "operacion": tipo,
                                "cripto": cripto,
                                "fiat": fiat,
                                "precio": float(oferta["adv"]["price"]),
                                "min": float(oferta["adv"]["minSingleTransAmount"]),
                                "max": float(oferta["adv"]["maxSingleTransAmount"]),
                                "nickname": oferta["advertiser"]["nickName"],
                                "reputacion": f'{oferta["advertiser"]["positiveRate"]}%',
                                "metodos_pago": metodos_validos,
                                "comision_estim": 0,
                                "brecha": 0,
                                "prioridad": 0,
                                "operable": True,
                                "link": f'https://p2p.binance.com/es/advertiserDetail?advertiserNo={oferta["advertiser"]["userNo"]}'
                            })
                except Exception as e:
                    print(f"Error en Binance ({tipo} {cripto}/{fiat}):", e)
    return datos

# Función para obtener datos simulados de OKX
def obtener_datos_okx():
    # Esta función está simulada. Aquí debes insertar tu lógica real de scraping o API de OKX.
    # Vamos a simular solo el formato correcto por ahora.
    datos = []
    for tipo in ["BUY", "SELL"]:
        datos.append({
            "exchange": "OKX",
            "operacion": tipo,
            "cripto": "USDT",
            "fiat": "COP",
            "precio": 4000 if tipo == "BUY" else 4500,
            "min": 100000,
            "max": 1000000,
            "nickname": "OKX_User" + tipo,
            "reputacion": "99.9%",
            "metodos_pago": ["NEQUI"],
            "comision_estim": 0,
            "brecha": 0,
            "prioridad": 0,
            "operable": True,
            "link": "https://www.okx.com/p2p-markets"
        })
    return datos

# Función para obtener datos simulados de Bybit
def obtener_datos_bybit():
    # Esta función está simulada. Aquí también insertarás tu lógica real más adelante.
    datos = []
    for tipo in ["BUY", "SELL"]:
        datos.append({
            "exchange": "Bybit",
            "operacion": tipo,
            "cripto": "USDC",
            "fiat": "COP",
            "precio": 4050 if tipo == "BUY" else 4550,
            "min": 50000,
            "max": 800000,
            "nickname": "Bybit_User" + tipo,
            "reputacion": "98.5%",
            "metodos_pago": ["Global66"],
            "comision_estim": 0,
            "brecha": 0,
            "prioridad": 0,
            "operable": True,
            "link": "https://www.bybit.com/fiat/trade/otc"
        })
    return datos

# Función principal para combinar todos los datos y guardarlos
def generar_archivo_json():
    datos_totales = (
        obtener_datos_binance()
        + obtener_datos_okx()
        + obtener_datos_bybit()
    )
    nombre_archivo = "datos_arbitraje.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos_totales, f, indent=4, ensure_ascii=False)
    print(f"{nombre_archivo} generado correctamente con {len(datos_totales)} señales.")

# Ejecutar si este archivo es llamado directamente
if __name__ == "__main__":
    generar_archivo_json()
