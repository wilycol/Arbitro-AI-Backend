🎯 Árbitro IA - Backend

Este es el backend oficial del sistema de arbitraje automatizado Árbitro IA.

🚀 Funcionalidades principales:
- Se ejecuta como un **servidor FastAPI en Render**.
- Ejecuta un ciclo de recolección automática cada 3 minutos (`ciclo_push.py`) que:
  - Conecta con Binance, OKX y Bybit.
  - Recolecta 120 señales P2P (20 BUY y 20 SELL por exchange).
  - Formatea las señales al esquema JSON extendido.
  - Publica los datos actualizados en GitHub para consumo externo.
- Exposición de una **API dinámica `/asesor`**, que permite consultas personalizadas desde interfaces de usuario gobernadas por IA (por ejemplo, Google Studio).
- Arquitectura modular y escalable, compatible con sistemas externos como dashboards, apps móviles o interfaces de IA.

🌐 JSONs publicados:
- [`datos_arbitraje.json`](https://raw.githubusercontent.com/wilycol/Arbitro-AI/main/public/datos_arbitraje.json)
- [`destacadas_arbitraje.json`](https://raw.githubusercontent.com/wilycol/Arbitro-AI/main/public/destacadas_arbitraje.json)

🧠 Compatible con Árbitro IA (Google Studio), dashboards en Vercel y ejecución manual o automatizada.

---

> Este backend es 100% gratuito, público y optimizado para el plan free de Render.
