import os
import sys
import time
import json
from datetime import datetime

# Añadir manualmente la ruta al módulo core/
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from arbitraje import obtener_todas_las_senales
from procesamiento import extraer_senales_destacadas

def git_push(token, repo_url, timestamp):
    os.system('git config --global user.email "render@arbitro-ia.local"')
    os.system('git config --global user.name "Render Bot"')
    os.system('git init')
    os.system('git add public/*.json')
    commit_command = f'git commit -m "🤖 Auto-push desde Render ({timestamp})" || echo "⚠️ Sin cambios para commitear"'
    os.system(commit_command)
    os.system(f'git remote add origin https://{token}@{repo_url}')
    os.system('git push origin main || echo "⚠️ Push fallido"')

def main():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        print(f"⏱️ Ejecutando ciclo - {timestamp}")
        all_signals = obtener_todas_las_senales()

        binance_buy = len([s for s in all_signals if s["exchange"] == "binance" and s["tipo"] == "BUY"])
        binance_sell = len([s for s in all_signals if s["exchange"] == "binance" and s["tipo"] == "SELL"])
        okx_buy = len([s for s in all_signals if s["exchange"] == "okx" and s["tipo"] == "BUY"])
        okx_sell = len([s for s in all_signals if s["exchange"] == "okx" and s["tipo"] == "SELL"])
        bybit_buy = len([s for s in all_signals if s["exchange"] == "bybit" and s["tipo"] == "BUY"])
        bybit_sell = len([s for s in all_signals if s["exchange"] == "bybit" and s["tipo"] == "SELL"])

        print("📊 Señales obtenidas:")
        print(f"  🟢 Binance: BUY={binance_buy} | SELL={binance_sell}")
        print(f"  🟠 OKX:     BUY={okx_buy} | SELL={okx_sell}")
        print(f"  🔵 Bybit:   BUY={bybit_buy} | SELL={bybit_sell}")
        print(f"  🧮 Total: {len(all_signals)} señales")

        Path("public").mkdir(exist_ok=True)
        with open("public/datos_arbitraje.json", "w") as f:
            json.dump(all_signals, f, indent=2)

        # Filtrar señales destacadas
        destacadas = extraer_senales_destacadas(all_signals)
        with open("public/destacadas_arbitraje.json", "w") as f:
            json.dump(destacadas, f, indent=2)

        # Push con token oculto
        git_token = os.getenv("GITTOKEN")
        git_repo = "github.com/wilycol/Arbitro-AI.git"
        git_push(git_token, git_repo, timestamp)

        print(f"✅ Push completado - {timestamp}")

    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
