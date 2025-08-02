# ciclo_push.py

import asyncio
import json
import datetime
import os
from utils.push import push_to_repo
from p2p_sources import get_binance_data, get_okx_data, get_bybit_data

ARCHIVO_JSON = "public/datos_arbitraje.json"
INTERVALO_MINUTOS = 3

def formatear_senales(raw_data):
    # Este formato debe seguir el estándar JSON que tú aprobaste
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

async def ciclo_actualizacion():
    while True:
        try:
            print(f"[{datetime.datetime.now()}] Iniciando recolección de señales...")

            # Recolección desde exchanges
            binance = get_binance_data()
            okx = get_okx_data()
            bybit = get_bybit_data()

            # Unir todas las señales
            todas = binance + okx + bybit
            print(f"Total señales recolectadas: {len(todas)}")

            # Formatear
            procesadas = formatear_senales(todas)

            # Guardar en archivo local
            with open(ARCHIVO_JSON, "w", encoding="utf-8") as f:
                json.dump(procesadas, f, indent=2, ensure_ascii=False)

            # Push a GitHub
            push_to_repo()

            print(f"✅ Señales actualizadas y subidas exitosamente.")

        except Exception as e:
            print(f"❌ Error en ciclo de actualización: {str(e)}")

        await asyncio.sleep(INTERVALO_MINUTOS * 60)
