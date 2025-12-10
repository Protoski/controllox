"""
Aplicación Principal - FastAPI
Sistema de Gases Medicinales MSPBS
DGGIES - Ministerio de Salud y Bienestar Social - Paraguay
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, usuarios, hospitales, gases_consumos, reportes
from app.services.keep_alive_service import keep_alive_service


# Lifespan para inicialización y limpieza
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Iniciando aplicación...")
    
    # Inicializar base de datos
    try:
        init_db()
        print("Base de datos inicializada")
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")
    
    # Iniciar servicio de keep-alive si está configurado
    if settings.KEEP_ALIVE_URL:
        await keep_alive_service.start()
        print("Servicio Keep-Alive iniciado")
    
    yield
    
    # Shutdown
    print("Deteniendo aplicación...")
    
    # Detener keep-alive
    if settings.KEEP_ALIVE_URL:
        await keep_alive_service.stop()
        print("Servicio Keep-Alive detenido")


# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=f"{settings.ORGANIZACION} - {settings.PAIS}",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporal - permite todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if settings.DEBUG else "Error procesando solicitud"
        }
    )


# Endpoints base
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "organizacion": settings.ORGANIZACION,
        "pais": settings.PAIS,
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Usado por Render y el servicio de keep-alive
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/info")
async def api_info():
    """Información de la API"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "organizacion": settings.ORGANIZACION,
        "endpoints": {
            "auth": "/api/auth",
            "usuarios": "/api/usuarios",
            "hospitales": "/api/hospitales",
            "gases": "/api/gases",
            "consumos": "/api/consumos",
            "reportes": "/api/reportes"
        }
    }


# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(usuarios.router, prefix="/api")
app.include_router(hospitales.router, prefix="/api")
app.include_router(gases_consumos.router_gases, prefix="/api")
app.include_router(gases_consumos.router_consumos, prefix="/api")
app.include_router(reportes.router, prefix="/api")


# Endpoint adicional para auditoría
from app.api.auditoria import router as auditoria_router
app.include_router(auditoria_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
