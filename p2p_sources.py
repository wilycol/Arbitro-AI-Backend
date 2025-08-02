import requests

# Cantidad de señales por tipo y exchange
LIMIT = 20

def get_binance_data():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json"}
    criptos = ["USDT"]
    fiat = "COP"
    operaciones = ["BUY", "SELL"]
    resultado = []

    for op in operaciones:
        for cripto in criptos:
            data = {
                "asset": cripto,
                "fiat": fiat,
                "tradeType": op,
                "page": 1,
                "rows": LIMIT,
                "payTypes": [],
                "publisherType": None
            }

            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                ofertas = response.json().get("data", [])
                for oferta in ofertas:
                    adv = oferta["adv"]
                    usuario = oferta["advertiser"]
                    resultado.append({
                        "exchange": "Binance",
                        "tipo_operacion": "venta" if op == "BUY" else "compra",
                        "cripto": adv["asset"],
                        "fiat": adv["fiatUnit"],
                        "precio": float(adv["price"]),
                        "limite_min": float(adv["minSingleTransAmount"]),
                        "limite_max": float(adv["maxSingleTransAmount"]),
                        "nickname": usuario["nickName"],
                        "reputacion": usuario.get("monthFinishRate", "N/A"),
                        "metodos_pago": adv.get("tradeMethods", []),
                        "operable": True,
                        "link": f"https://p2p.binance.com/es/advertiserDetail?advertiserNo={usuario['userNo']}"
                    })
            else:
                print("Error al obtener datos de Binance:", response.status_code)

    return resultado


def get_okx_data():
    url = "https://www.okx.com/v3/c2c/tradingOrders/book"
    criptos = ["USDT"]
    fiat = "COP"
    operaciones = ["buy", "sell"]
    resultado = []

    for op in operaciones:
        for cripto in criptos:
            params = {
                "quoteCurrency": fiat,
                "baseCurrency": cripto,
                "side": op,
                "paymentMethod": "",
                "userType": "all",
                "limit": LIMIT
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json().get("data", {}).get("orders", [])
                for item in data:
                    resultado.append({
                        "exchange": "OKX",
                        "tipo_operacion": "venta" if op == "buy" else "compra",
                        "cripto": cripto,
                        "fiat": fiat,
                        "precio": float(item["price"]),
                        "limite_min": float(item["minAmount"]),
                        "limite_max": float(item["maxAmount"]),
                        "nickname": item["userInfo"]["nickName"],
                        "reputacion": item["userInfo"].get("completionRate", "N/A"),
                        "metodos_pago": item.get("payMethods", []),
                        "operable": True,
                        "link": f"https://www.okx.com/p2p-markets?quoteCurrency={fiat}&baseCurrency={cripto}&side={op}"
                    })
            else:
                print("Error al obtener datos de OKX:", response.status_code)

    return resultado


def get_bybit_data():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    criptos = ["USDT"]
    fiat = "COP"
    operaciones = ["BUY", "SELL"]
    resultado = []

    for op in operaciones:
        for cripto in criptos:
            payload = {
                "userId": "",
                "tokenId": cripto,
                "currencyId": fiat,
                "payment": [],
                "side": op,
                "size": LIMIT,
                "page": 1
            }

            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json().get("result", {}).get("items", [])
                for item in data:
                    resultado.append({
                        "exchange": "Bybit",
                        "tipo_operacion": "venta" if op == "BUY" else "compra",
                        "cripto": cripto,
                        "fiat": fiat,
                        "precio": float(item["price"]),
                        "limite_min": float(item["minAmount"]),
                        "limite_max": float(item["maxAmount"]),
                        "nickname": item["nickName"],
                        "reputacion": item.get("orderCompleteRate", "N/A"),
                        "metodos_pago": item.get("paymentMethods", []),
                        "operable": True,
                        "link": f"https://www.bybit.com/fiat/trade/{op.lower()}/{cripto}?currency={fiat}"
                    })
            else:
                print("Error al obtener datos de Bybit:", response.status_code)

    return resultado
