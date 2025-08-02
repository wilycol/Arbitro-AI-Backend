# utils/push.py

import os
import base64
import json
import requests
from datetime import datetime

def push_to_github(file_path, repo, branch, token, target_path):
    """Sube un archivo al repositorio especificado usando GitHub API."""

    api_url = f"https://api.github.com/repos/{repo}/contents/{target_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Leer contenido del archivo local
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Verificar si el archivo ya existe para obtener SHA
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None

    data = {
        "message": f"Actualización automática {datetime.now().isoformat()}",
        "content": content,
        "branch": branch,
    }

    if sha:
        data["sha"] = sha

    response = requests.put(api_url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()
