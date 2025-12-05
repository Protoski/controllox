"""
API Endpoints - Usuarios
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    get_current_active_admin,
    get_password_hash
)
from app.models.models import Usuario, Auditoria
from app.schemas.schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    request: Request,
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Crear nuevo usuario (solo ADMIN)
    """
    # Verificar que el email no exista
    existing_user = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Validar hospital_id si es usuario de hospital
    if usuario_data.rol == "HOSPITAL_USER":
        from app.models.models import Hospital
        hospital = db.query(Hospital).filter(Hospital.id == usuario_data.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital no encontrado"
            )
    
    # Crear usuario
    nuevo_usuario = Usuario(
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        email=usuario_data.email,
        hash_password=get_password_hash(usuario_data.password),
        rol=usuario_data.rol,
        hospital_id=usuario_data.hospital_id,
        estado=usuario_data.estado
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="CREAR_USUARIO",
        detalle=f"Usuario creado: {nuevo_usuario.email}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return nuevo_usuario


@router.get("/", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    rol: Optional[str] = None,
    estado: Optional[bool] = None,
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Listar usuarios (solo ADMIN)
    """
    query = db.query(Usuario)
    
    if rol:
        query = query.filter(Usuario.rol == rol)
    if estado is not None:
        query = query.filter(Usuario.estado == estado)
    if hospital_id:
        query = query.filter(Usuario.hospital_id == hospital_id)
    
    usuarios = query.offset(skip).limit(limit).all()
    return usuarios


@router.get("/me", response_model=UsuarioResponse)
async def obtener_usuario_actual(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener datos del usuario actual
    """
    return current_user


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Obtener usuario por ID (solo ADMIN)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    request: Request,
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Actualizar usuario (solo ADMIN)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar campos
    update_data = usuario_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="ACTUALIZAR_USUARIO",
        detalle=f"Usuario actualizado: {usuario.email}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return usuario


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Desactivar usuario (no eliminar físicamente)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    usuario.estado = False
    db.commit()
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="DESACTIVAR_USUARIO",
        detalle=f"Usuario desactivado: {usuario.email}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Usuario desactivado exitosamente"}


@router.post("/{usuario_id}/change-password")
async def cambiar_password(
    request: Request,
    usuario_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar contraseña de usuario
    Los usuarios pueden cambiar su propia contraseña
    Los ADMIN pueden cambiar cualquier contraseña
    """
    # Verificar permisos
    if current_user.id != usuario_id and current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para cambiar esta contraseña"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    usuario.hash_password = get_password_hash(new_password)
    db.commit()
    
    # Registrar en auditoría
    auditoria = Auditoria(
        usuario_id=current_user.id,
        accion="CAMBIAR_PASSWORD",
        detalle=f"Contraseña cambiada para: {usuario.email}",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}
