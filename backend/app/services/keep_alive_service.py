"""
Servicio Keep-Alive para Render.com
Previene que el servicio entre en sleep mode
Sistema de Gases Medicinales MSPBS
"""

import asyncio
import aiohttp
from datetime import datetime
from app.core.config import settings


class KeepAliveService:
    """
    Servicio que hace ping al propio servidor para mantenerlo activo
    """
    
    def __init__(self):
        self.running = False
        self.task = None
    
    async def ping_self(self):
        """Hacer ping al endpoint de health check"""
        if not settings.KEEP_ALIVE_URL:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{settings.KEEP_ALIVE_URL}/health") as response:
                    if response.status == 200:
                        print(f"[{datetime.now()}] Keep-alive ping exitoso")
                    else:
                        print(f"[{datetime.now()}] Keep-alive ping falló: {response.status}")
        except Exception as e:
            print(f"[{datetime.now()}] Error en keep-alive ping: {e}")
    
    async def run(self):
        """Ejecutar el servicio de keep-alive"""
        self.running = True
        print(f"Keep-Alive Service iniciado - Intervalo: {settings.KEEP_ALIVE_INTERVAL} segundos")
        
        while self.running:
            await self.ping_self()
            await asyncio.sleep(settings.KEEP_ALIVE_INTERVAL)
    
    async def start(self):
        """Iniciar el servicio en background"""
        if not self.task:
            self.task = asyncio.create_task(self.run())
    
    async def stop(self):
        """Detener el servicio"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass


# Instancia global
keep_alive_service = KeepAliveService()
