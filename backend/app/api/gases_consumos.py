"""
API Endpoints - Gases Medicinales y Consumos
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    get_current_active_admin,
    get_current_hospital_user
)
from app.models.models import Gas, Consumo, Usuario, Hospital, Auditoria
from app.schemas.schemas import (
    GasCreate,
    GasUpdate,
    GasResponse,
    ConsumoCreate,
    ConsumoUpdate,
    ConsumoResponse
)

# ============ GASES ============
router_gases = APIRouter(prefix="/gases", tags=["Gases Medicinales"])


@router_gases.post("/", response_model=GasResponse, status_code=status.HTTP_201_CREATED)
async def crear_gas(
    request: Request,
    gas_data: GasCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """Crear nuevo gas (solo ADMIN)"""
    # Verificar que el código no exista
    existing_gas = db.query(Gas).filter(Gas.codigo == gas_data.codigo).first()
    if existing_gas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un gas con ese código"
        )
    
    nuevo_gas = Gas(**gas_data.dict())
    db.add(nuevo_gas)
    db.commit()
    db.refresh(nuevo_gas)
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="CREAR_GAS",
        detalle=f"Gas creado: {nuevo_gas.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return nuevo_gas


@router_gases.get("/", response_model=List[GasResponse])
async def listar_gases(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar gases medicinales"""
    query = db.query(Gas)
    
    if estado is not None:
        query = query.filter(Gas.estado == estado)
    
    gases = query.offset(skip).limit(limit).all()
    return gases


@router_gases.get("/{gas_id}", response_model=GasResponse)
async def obtener_gas(
    gas_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener gas por ID"""
    gas = db.query(Gas).filter(Gas.id == gas_id).first()
    if not gas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gas no encontrado"
        )
    return gas


@router_gases.put("/{gas_id}", response_model=GasResponse)
async def actualizar_gas(
    request: Request,
    gas_id: int,
    gas_data: GasUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """Actualizar gas (solo ADMIN)"""
    gas = db.query(Gas).filter(Gas.id == gas_id).first()
    if not gas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gas no encontrado"
        )
    
    # Actualizar campos
    update_data = gas_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gas, field, value)
    
    db.commit()
    db.refresh(gas)
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="ACTUALIZAR_GAS",
        detalle=f"Gas actualizado: {gas.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return gas


@router_gases.delete("/{gas_id}")
async def eliminar_gas(
    request: Request,
    gas_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """Desactivar gas (no eliminar físicamente)"""
    gas = db.query(Gas).filter(Gas.id == gas_id).first()
    if not gas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gas no encontrado"
        )
    
    gas.estado = False
    db.commit()
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="DESACTIVAR_GAS",
        detalle=f"Gas desactivado: {gas.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Gas desactivado exitosamente"}


# ============ CONSUMOS ============
router_consumos = APIRouter(prefix="/consumos", tags=["Consumos"])


@router_consumos.post("/", response_model=ConsumoResponse, status_code=status.HTTP_201_CREATED)
async def crear_consumo(
    request: Request,
    consumo_data: ConsumoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crear registro de consumo"""
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER":
        if consumo_data.hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede crear consumos para su hospital"
            )
    
    # Verificar que el hospital exista
    hospital = db.query(Hospital).filter(Hospital.id == consumo_data.hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital no encontrado"
        )
    
    # Verificar que el gas exista
    gas = db.query(Gas).filter(Gas.id == consumo_data.gas_id).first()
    if not gas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gas no encontrado"
        )
    
    # Crear consumo
    nuevo_consumo = Consumo(
        **consumo_data.dict(),
        usuario_id=current_user.id
    )
    
    db.add(nuevo_consumo)
    db.commit()
    db.refresh(nuevo_consumo)
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="CREAR_CONSUMO",
        detalle=f"Consumo creado: {hospital.nombre} - {gas.nombre}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return nuevo_consumo


@router_consumos.get("/", response_model=List[ConsumoResponse])
async def listar_consumos(
    skip: int = 0,
    limit: int = 100,
    hospital_id: Optional[int] = None,
    gas_id: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    modo_suministro: Optional[str] = None,
    validado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar consumos con filtros"""
    query = db.query(Consumo)
    
    # Si es usuario de hospital, solo ver sus consumos
    if current_user.rol == "HOSPITAL_USER":
        query = query.filter(Consumo.hospital_id == current_user.hospital_id)
    elif hospital_id:
        query = query.filter(Consumo.hospital_id == hospital_id)
    
    if gas_id:
        query = query.filter(Consumo.gas_id == gas_id)
    if fecha_inicio:
        query = query.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Consumo.fecha_fin <= fecha_fin)
    if modo_suministro:
        query = query.filter(Consumo.modo_suministro == modo_suministro)
    if validado is not None:
        query = query.filter(Consumo.validado == validado)
    
    # Ordenar por fecha más reciente
    query = query.order_by(Consumo.created_at.desc())
    
    consumos = query.offset(skip).limit(limit).all()
    
    # Cargar relaciones
    for consumo in consumos:
        consumo.hospital
        consumo.gas
    
    return consumos


@router_consumos.get("/{consumo_id}", response_model=ConsumoResponse)
async def obtener_consumo(
    consumo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener consumo por ID"""
    consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumo no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER":
        if consumo.hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para ver este consumo"
            )
    
    # Cargar relaciones
    consumo.hospital
    consumo.gas
    
    return consumo


@router_consumos.put("/{consumo_id}", response_model=ConsumoResponse)
async def actualizar_consumo(
    request: Request,
    consumo_id: int,
    consumo_data: ConsumoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar consumo"""
    consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumo no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER":
        if consumo.hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para editar este consumo"
            )
    
    # Actualizar campos
    update_data = consumo_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consumo, field, value)
    
    db.commit()
    db.refresh(consumo)
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="ACTUALIZAR_CONSUMO",
        detalle=f"Consumo actualizado: ID {consumo_id}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return consumo


@router_consumos.delete("/{consumo_id}")
async def eliminar_consumo(
    request: Request,
    consumo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Eliminar consumo"""
    consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumo no encontrado"
        )
    
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER":
        if consumo.hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para eliminar este consumo"
            )
    
    # Eliminar
    db.delete(consumo)
    db.commit()
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="ELIMINAR_CONSUMO",
        detalle=f"Consumo eliminado: ID {consumo_id}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Consumo eliminado exitosamente"}


@router_consumos.post("/{consumo_id}/validar")
async def validar_consumo(
    request: Request,
    consumo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """Validar consumo (solo ADMIN)"""
    from datetime import datetime
    
    consumo = db.query(Consumo).filter(Consumo.id == consumo_id).first()
    if not consumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumo no encontrado"
        )
    
    consumo.validado = True
    consumo.validado_por = current_user.id
    consumo.fecha_validacion = datetime.utcnow()
    db.commit()
    
    # Auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="VALIDAR_CONSUMO",
        detalle=f"Consumo validado: ID {consumo_id}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Consumo validado exitosamente"}
