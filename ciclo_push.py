# ciclo_push.py

import asyncio
import json
import datetime
import os
from utils.push import push_to_github
from p2p_sources import get_binance_data, get_okx_data, get_bybit_data

ARCHIVO_JSON = "public/datos_arbitraje.json"
CARPETA_HISTORIAL = "historial_arbitraje"
ARCHIVO_DESTACADAS = "public/destacadas_arbitraje.json"
INTERVALO_MINUTOS = 3

def formatear_senales(raw_data):
    resultado = []
    for entrada in raw_data:
        resultado.append({
            "exchange": entrada.get("exchange", ""),
            "tipo_operacion": entrada.get("tipo_operacion", ""),
            "cripto": entrada.get("cripto", ""),
            "fiat": entrada.get("fiat", ""),
            "precio": entrada.get("precio", 0.0),
            "limite_min": entrada.get("limite_min", 0.0),
            "limite_max": entrada.get("limite_max", 0.0),
            "nickname": entrada.get("nickname", ""),
            "metodos_pago": entrada.get("metodos_pago", []),
            "reputacion": entrada.get("reputacion", ""),
            "link": entrada.get("link", ""),
            "comision_aprox": entrada.get("comision_aprox", 0.0),
            "ganancia_estimada": entrada.get("ganancia_estimada", 0.0),
            "brecha": entrada.get("brecha", 0.0),
            "operable": entrada.get("operable", False),
            "prioridad": entrada.get("prioridad", "")
        })
    return resultado

def filtrar_destacadas(senales):
    resultado = []
    exchanges = set([s["exchange"] for s in senales])
    for ex in exchanges:
        buy = [s for s in senales if s["exchange"] == ex and s["tipo_operacion"] == "BUY"]
        sell = [s for s in senales if s["exchange"] == ex and s["tipo_operacion"] == "SELL"]
        buy_ordenadas = sorted(buy, key=lambda x: x["precio"])[:5]
        sell_ordenadas = sorted(sell, key=lambda x: x["precio"], reverse=True)[:5]
        resultado.extend(buy_ordenadas)
        resultado.extend(sell_ordenadas)
    return resultado

async def ciclo_actualizacion():
    while True:
        try:
            print(f"[{datetime.datetime.now()}] Iniciando recolección de señales...")

            # Recolección
            binance = get_binance_data()
            okx = get_okx_data()
            bybit = get_bybit_data()
            todas = binance + okx + bybit
            print(f"Total señales recolectadas: {len(todas)}")

            # Formateo
            procesadas = formatear_senales(todas)

            # Guardar archivo principal
            with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
                json.dump(procesadas, f, indent=2, ensure_ascii=False)

            # Guardar archivo histórico
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_historial = f"{CARPETA_HISTORIAL}/datos_arbitraje_{timestamp}.json"
            with open(archivo_historial, "w", encoding="utf-8") as f:
                json.dump(procesadas, f, indent=2, ensure_ascii=False)

            # Guardar destacadas
            destacadas = filtrar_destacadas(procesadas)
            with open(ARCHIVO_DESTACADAS, "w", encoding="utf-8") as f:
                json.dump(destacadas, f, indent=2, ensure_ascii=False)

            # Push a GitHub
            push_to_github(ARCHIVO_JSON)
            push_to_github(archivo_historial)
            push_to_github(ARCHIVO_DESTACADAS)

            print("✅ Señales actualizadas y subidas exitosamente.")

        except Exception as e:
            print(f"❌ Error en ciclo de actualización: {str(e)}")

        await asyncio.sleep(INTERVALO_MINUTOS * 60)
