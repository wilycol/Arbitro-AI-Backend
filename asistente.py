# asistente.py

from fastapi import APIRouter, Request
import json

router = APIRouter()

# Ruta de IA: responde con las mejores señales según parámetros
@router.get("/asesor")
async def asesor_ia(request: Request):
    params = request.query_params
    cripto = params.get("cripto", "USDT")
    fiat = params.get("fiat", "COP")
    operacion = params.get("operacion", "BUY").upper()

    try:
        with open("public/datos_arbitraje.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"No se pudo leer el archivo: {str(e)}"}

    # Filtro básico por los parámetros recibidos
    resultados = [
        s for s in data
        if s["cripto"] == cripto and
           s["fiat"] == fiat and
           s["tipo_operacion"] == operacion
    ]

    # Ordenamos por mejor brecha estimada (puedes cambiarlo a prioridad, reputación, etc.)
    resultados = sorted(resultados, key=lambda x: x.get("brecha", 0), reverse=True)

    return {
        "status": "ok",
        "total": len(resultados),
        "resultados": resultados[:10]  # Devuelve solo los 10 mejores
    }
