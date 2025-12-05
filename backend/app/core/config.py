"""
Configuración General del Sistema
Sistema de Gases Medicinales MSPBS
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # App
    APP_NAME: str = "Sistema de Gases Medicinales MSPBS"
    APP_VERSION: str = "1.0.0"
    ORGANIZACION: str = "DGGIES - Ministerio de Salud y Bienestar Social"
    PAIS: str = "Paraguay"
    DEBUG: bool = False
    
    # Base de datos
    DATABASE_URL: str
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Email (para recuperación de contraseña)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = "noreply@mspbs.gov.py"
    
    # Render keep-alive (para evitar sleep)
    KEEP_ALIVE_URL: Optional[str] = None
    KEEP_ALIVE_INTERVAL: int = 840  # 14 minutos (Render duerme a los 15 min)
    
    # Paginación
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Reportes
    REPORTS_DIR: str = "static/reports"
    LOGO_PATH: str = "static/logos/mspbs_logo.png"
    
    # Límites de archivos
    MAX_UPLOAD_SIZE: int = 10485760  # 10 MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
