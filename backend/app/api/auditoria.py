"""
API Endpoints - Auditoría
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.models import Auditoria, Usuario
from app.schemas.schemas import AuditoriaResponse

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])


@router.get("/", response_model=List[AuditoriaResponse])
async def listar_auditoria(
    skip: int = 0,
    limit: int = 100,
    usuario_id: Optional[int] = None,
    accion: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Listar registros de auditoría (solo ADMIN)
    """
    query = db.query(Auditoria)
    
    if usuario_id:
        query = query.filter(Auditoria.usuario_id == usuario_id)
    if accion:
        query = query.filter(Auditoria.accion.ilike(f"%{accion}%"))
    if fecha_inicio:
        query = query.filter(Auditoria.fecha_hora >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Auditoria.fecha_hora <= fecha_fin)
    
    # Ordenar por más reciente
    query = query.order_by(Auditoria.fecha_hora.desc())
    
    auditorias = query.offset(skip).limit(limit).all()
    return auditorias


@router.get("/acciones")
async def listar_acciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Listar tipos de acciones únicas en auditoría
    """
    acciones = db.query(Auditoria.accion).distinct().all()
    return [a[0] for a in acciones if a[0]]


@router.get("/estadisticas")
async def estadisticas_auditoria(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Estadísticas de auditoría
    """
    from sqlalchemy import func
    
    query = db.query(Auditoria)
    
    if fecha_inicio:
        query = query.filter(Auditoria.fecha_hora >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Auditoria.fecha_hora <= fecha_fin)
    
    # Total de eventos
    total_eventos = query.count()
    
    # Eventos por acción
    eventos_por_accion = query.with_entities(
        Auditoria.accion,
        func.count(Auditoria.id).label('cantidad')
    ).group_by(Auditoria.accion).all()
    
    # Usuarios más activos
    usuarios_activos = query.filter(Auditoria.usuario_id.isnot(None)).with_entities(
        Auditoria.usuario_id,
        func.count(Auditoria.id).label('cantidad')
    ).group_by(Auditoria.usuario_id).order_by(
        func.count(Auditoria.id).desc()
    ).limit(10).all()
    
    # Obtener nombres de usuarios
    usuarios_con_nombres = []
    for usuario_id, cantidad in usuarios_activos:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if usuario:
            usuarios_con_nombres.append({
                "usuario_id": usuario_id,
                "nombre": f"{usuario.nombre} {usuario.apellido}",
                "cantidad": cantidad
            })
    
    return {
        "total_eventos": total_eventos,
        "eventos_por_accion": [
            {"accion": accion, "cantidad": cantidad}
            for accion, cantidad in eventos_por_accion
        ],
        "usuarios_mas_activos": usuarios_con_nombres
    }


@router.delete("/limpiar")
async def limpiar_auditoria_antigua(
    dias_antiguedad: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Limpiar registros de auditoría antiguos (solo ADMIN)
    Elimina registros más antiguos que X días
    """
    from datetime import timedelta
    
    fecha_limite = datetime.utcnow() - timedelta(days=dias_antiguedad)
    
    registros_eliminados = db.query(Auditoria).filter(
        Auditoria.fecha_hora < fecha_limite
    ).delete()
    
    db.commit()
    
    return {
        "mensaje": f"Auditoría limpiada exitosamente",
        "registros_eliminados": registros_eliminados,
        "dias_antiguedad": dias_antiguedad
    }
