import os
import time
import json
from datetime import datetime
from core.arbitraje import obtener_todas_las_senales
from core.procesamiento import extraer_senales_destacadas

while True:
    try:
        print("⏳ Obteniendo señales...")
        all_signals = obtener_todas_las_senales()

        # Contador por exchange
        binance_buy = len([s for s in all_signals if s["exchange"] == "binance" and s["tipo"] == "BUY"])
        binance_sell = len([s for s in all_signals if s["exchange"] == "binance" and s["tipo"] == "SELL"])
        okx_buy = len([s for s in all_signals if s["exchange"] == "okx" and s["tipo"] == "BUY"])
        okx_sell = len([s for s in all_signals if s["exchange"] == "okx" and s["tipo"] == "SELL"])
        bybit_buy = len([s for s in all_signals if s["exchange"] == "bybit" and s["tipo"] == "BUY"])
        bybit_sell = len([s for s in all_signals if s["exchange"] == "bybit" and s["tipo"] == "SELL"])

        print(f"📊 Señales obtenidas:")
        print(f"🟢 Binance: BUY={binance_buy} | SELL={binance_sell}")
        print(f"🟡 OKX:    BUY={okx_buy} | SELL={okx_sell}")
        print(f"🔵 Bybit:  BUY={bybit_buy} | SELL={bybit_sell}")
        print(f"🔷 Total: {len(all_signals)} señales")

        # Guardar archivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = "Arbitro-AI/public"
        historial_folder = "Arbitro-AI/historial_arbitraje"

        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(historial_folder, exist_ok=True)

        with open(f"{output_folder}/datos_arbitraje.json", "w", encoding="utf-8") as f:
            json.dump(all_signals, f, indent=2, ensure_ascii=False)

        with open(f"{historial_folder}/datos_arbitraje_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(all_signals, f, indent=2, ensure_ascii=False)

        destacadas = extraer_senales_destacadas(all_signals)
        with open(f"{output_folder}/destacadas_arbitraje.json", "w", encoding="utf-8") as f:
            json.dump(destacadas, f, indent=2, ensure_ascii=False)

        # Configuración de Git y push
        print("🛠 Configurando Git...")
        os.system('git config --global user.email "arbitro@render.io"')
        os.system('git config --global user.name "Wily Bot en Render"')

        token = os.getenv("GITTOKEN")
        if token:
            os.chdir("Arbitro-AI")
            os.system(f'git remote set-url origin https://{token}@github.com/wilycol/Arbitro-AI.git')
            os.system("git add public/*.json")
            os.system("git add historial_arbitraje/*.json")
            os.system(f'git commit -m "🤖 Auto-push desde Render - {timestamp}" || echo "❌ No hay cambios nuevos"')
            os.system("git push origin main")
            os.chdir("..")
            print(f"✅ Push completado - {timestamp}")
        else:
            print("❌ Token de GitHub no encontrado en variables de entorno")

    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

    time.sleep(180)
