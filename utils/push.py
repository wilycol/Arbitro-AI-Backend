# utils/push.py

import base64
import requests
import os
import datetime

def push_to_github(filepath, branch="main"):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Exception("Token de GitHub no definido en variable de entorno GITHUB_TOKEN")

    repo = "wilycol/Arbitro-AI-Backend"
    filename = os.path.basename(filepath)
    ruta_en_repo = f"public/{filename}"

    # Leer contenido local
    with open(filepath, "rb") as f:
        content = f.read()
    content_encoded = base64.b64encode(content).decode("utf-8")

    # Verificar si ya existe (para obtener SHA)
    url = f"https://api.github.com/repos/{repo}/contents/{ruta_en_repo}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    # Mensaje de commit
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"Auto-update desde backend Árbitro IA - {fecha}"

    data = {
        "message": mensaje,
        "content": content_encoded,
        "branch": branch,
    }
    if sha:
        data["sha"] = sha

    # Hacer el push
    put_response = requests.put(url, headers=headers, json=data)
    if put_response.status_code not in [200, 201]:
        raise Exception(f"Fallo al hacer push: {put_response.json()}")

    print("✅ Push a GitHub realizado con éxito.")
