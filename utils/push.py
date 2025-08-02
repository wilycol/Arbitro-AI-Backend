import os
import subprocess
from datetime import datetime
import shutil

REPO_URL = "https://github.com/wilycol/Arbitro-AI"
CLONE_DIR = "temp_arbitro_ai"
BRANCH = "main"
FILES_TO_COPY = ["datos_arbitraje.json", "destacadas_arbitraje.json"]
DEST_FOLDER = "public"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def push_to_repo():
    if not GITHUB_TOKEN:
        print("❌ No se encontró la variable GITHUB_TOKEN")
        return

    # Construimos la URL con el token embebido (de forma segura)
    auth_repo_url = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")

    # Eliminamos carpeta anterior si existe
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR)

    try:
        print("📥 Clonando repositorio de datos...")
        subprocess.run(["git", "clone", "-b", BRANCH, auth_repo_url, CLONE_DIR], check=True)

        # Copiamos los archivos generados al directorio destino
        for filename in FILES_TO_COPY:
            src = filename
            dest = os.path.join(CLONE_DIR, DEST_FOLDER, filename)
            shutil.copyfile(src, dest)
            print(f"✅ Copiado: {src} ➡️ {dest}")

        # Hacemos commit y push
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(["git", "-C", CLONE_DIR, "add", "."], check=True)
        subprocess.run(["git", "-C", CLONE_DIR, "commit", "-m", f"📊 Update arbitrage data {now}"], check=True)
        subprocess.run(["git", "-C", CLONE_DIR, "push"], check=True)

        print("🚀 Push completado con éxito")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante el push: {e}")

    # (Opcional) Borrar carpeta temporal
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR)
        print("🧹 Carpeta temporal eliminada")

