from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_app.database import engine, Base
from fastapi_app.routers import auth as auth_router, clientes, productos, pedidos
from dotenv import load_dotenv
import os

load_dotenv()

# Crear tabla api_usuarios si no existe
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API CRUD Pedidos — FastAPI + JWT",
    version="1.0.0",
    description="API REST protegida con JWT. Comparte BD con la interfaz Django."
)

# CORS restrictivo: leer origenes permitidas desde variable de entorno
allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(auth_router.router)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(pedidos.router)

@app.get('/api/')
def root():
    return {'mensaje': 'FastAPI + JWT funcionando. Visita /api/docs para Swagger UI.'}
