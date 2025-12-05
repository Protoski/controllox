"""
API Endpoints - Hospitales
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.models import Hospital, Usuario, Auditoria
from app.schemas.schemas import (
    HospitalCreate,
    HospitalUpdate,
    HospitalResponse
)

router = APIRouter(prefix="/hospitales", tags=["Hospitales"])


@router.post("/", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
async def crear_hospital(
    request: Request,
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Crear nuevo hospital (solo ADMIN)
    """
    # Verificar que el código no exista
    existing_hospital = db.query(Hospital).filter(Hospital.codigo == hospital_data.codigo).first()
    if existing_hospital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un hospital con ese código"
        )
    
    nuevo_hospital = Hospital(**hospital_data.dict())
    db.add(nuevo_hospital)
    db.commit()
    db.refresh(nuevo_hospital)
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="CREAR_HOSPITAL",
        detalle=f"Hospital creado: {nuevo_hospital.nombre} ({nuevo_hospital.codigo})",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return nuevo_hospital


@router.get("/", response_model=List[HospitalResponse])
async def listar_hospitales(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    departamento: Optional[str] = None,
    estado: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar hospitales
    """
    query = db.query(Hospital)
    
    if tipo:
        query = query.filter(Hospital.tipo == tipo)
    if departamento:
        query = query.filter(Hospital.departamento == departamento)
    if estado is not None:
        query = query.filter(Hospital.estado == estado)
    if search:
        query = query.filter(
            (Hospital.nombre.ilike(f"%{search}%")) |
            (Hospital.codigo.ilike(f"%{search}%"))
        )
    
    hospitales = query.offset(skip).limit(limit).all()
    return hospitales


@router.get("/departamentos")
async def listar_departamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar departamentos únicos
    """
    departamentos = db.query(Hospital.departamento).distinct().all()
    return [d[0] for d in departamentos if d[0]]


@router.get("/{hospital_id}", response_model=HospitalResponse)
async def obtener_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener hospital por ID
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital no encontrado"
        )
    return hospital


@router.put("/{hospital_id}", response_model=HospitalResponse)
async def actualizar_hospital(
    request: Request,
    hospital_id: int,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Actualizar hospital (solo ADMIN)
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital no encontrado"
        )
    
    # Si se actualiza el código, verificar que no exista
    if hospital_data.codigo and hospital_data.codigo != hospital.codigo:
        existing = db.query(Hospital).filter(Hospital.codigo == hospital_data.codigo).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un hospital con ese código"
            )
    
    # Actualizar campos
    update_data = hospital_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hospital, field, value)
    
    db.commit()
    db.refresh(hospital)
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="ACTUALIZAR_HOSPITAL",
        detalle=f"Hospital actualizado: {hospital.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return hospital


@router.delete("/{hospital_id}")
async def eliminar_hospital(
    request: Request,
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Desactivar hospital (no eliminar físicamente)
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital no encontrado"
        )
    
    hospital.estado = False
    db.commit()
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="DESACTIVAR_HOSPITAL",
        detalle=f"Hospital desactivado: {hospital.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Hospital desactivado exitosamente"}


@router.get("/{hospital_id}/estadisticas")
async def obtener_estadisticas_hospital(
    hospital_id: int,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas de un hospital
    """
    from sqlalchemy import func
    from app.models.models import Consumo, Gas
    from datetime import datetime
    
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER" and current_user.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este hospital"
        )
    
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital no encontrado"
        )
    
    # Construir query
    query = db.query(
        Gas.nombre,
        func.sum(Consumo.cantidad).label("total"),
        Gas.unidad_base
    ).join(Consumo).filter(Consumo.hospital_id == hospital_id)
    
    if fecha_inicio:
        query = query.filter(Consumo.fecha_inicio >= datetime.fromisoformat(fecha_inicio))
    if fecha_fin:
        query = query.filter(Consumo.fecha_fin <= datetime.fromisoformat(fecha_fin))
    
    resultados = query.group_by(Gas.nombre, Gas.unidad_base).all()
    
    return {
        "hospital": hospital.nombre,
        "consumos_por_gas": [
            {
                "gas": r[0],
                "total": float(r[1]) if r[1] else 0,
                "unidad": r[2]
            }
            for r in resultados
        ]
    }
