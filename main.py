# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from ciclo_push import ciclo_actualizacion
from asistente import router as asistente_router

app = FastAPI()

# CORS (permite llamadas desde tu frontend, como Vercel o Google Studio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes reemplazar "*" por la URL exacta de tu frontend si deseas restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas del asistente IA
app.include_router(asistente_router)

# Iniciar el ciclo automático cada 3 minutos al iniciar el servidor
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ciclo_actualizacion())
