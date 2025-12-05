"""
API Endpoints - Autenticación
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    generate_recovery_token,
    get_password_hash
)
from app.models.models import Usuario, Auditoria
from app.schemas.schemas import (
    UsuarioLogin,
    Token,
    RecuperarPasswordRequest,
    ResetPasswordRequest
)
from app.services.email_service import send_recovery_email

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    Retorna token JWT y datos del usuario
    """
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verify_password(form_data.password, usuario.hash_password):
        # Registrar intento fallido
        auditoria = Auditoria(
            usuario_id=usuario.id if usuario else None,
            accion="LOGIN_FALLIDO",
            detalle=f"Intento de login fallido para: {form_data.username}",
            ip=request.client.host if request.client else None
        )
        db.add(auditoria)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not usuario.estado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    # Crear token
    access_token = create_access_token(data={"sub": usuario.email})
    
    # Actualizar último acceso
    usuario.ultimo_acceso = datetime.utcnow()
    
    # Registrar login exitoso
    auditoria = Auditoria(
        usuario_id=usuario.id,
        accion="LOGIN_EXITOSO",
        detalle=f"Login exitoso",
        ip=request.client.host if request.client else None
    )
    db.add(auditoria)
    db.commit()
    
    # Preparar respuesta
    from app.schemas.schemas import UsuarioResponse
    usuario_response = UsuarioResponse.from_orm(usuario)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario_response
    }


@router.post("/recuperar-password")
async def recuperar_password(
    request: RecuperarPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Enviar email de recuperación de contraseña
    """
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    
    if not usuario:
        # No revelar si el email existe o no
        return {"mensaje": "Si el email existe, recibirás instrucciones para recuperar tu contraseña"}
    
    # Generar token de recuperación
    recovery_token = generate_recovery_token()
    usuario.token_recuperacion = recovery_token
    usuario.token_expiracion = datetime.utcnow() + timedelta(hours=24)
    
    db.commit()
    
    # Enviar email
    try:
        await send_recovery_email(usuario.email, usuario.nombre, recovery_token)
    except Exception as e:
        print(f"Error enviando email: {e}")
    
    return {"mensaje": "Si el email existe, recibirás instrucciones para recuperar tu contraseña"}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resetear contraseña con token de recuperación
    """
    usuario = db.query(Usuario).filter(
        Usuario.token_recuperacion == request.token
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
    
    if usuario.token_expiracion < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )
    
    # Actualizar contraseña
    usuario.hash_password = get_password_hash(request.new_password)
    usuario.token_recuperacion = None
    usuario.token_expiracion = None
    
    # Registrar cambio
    auditoria = Auditoria(
        usuario_id=usuario.id,
        accion="PASSWORD_RESET",
        detalle="Contraseña reseteada mediante token de recuperación"
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente"}


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """
    Logout (registrar en auditoría)
    """
    # En realidad el logout se maneja en el frontend eliminando el token
    # Aquí solo registramos el evento
    
    try:
        # Intentar extraer usuario del token si está disponible
        from app.core.security import get_current_user
        usuario = await get_current_user(request.headers.get("Authorization", "").replace("Bearer ", ""), db)
        
        auditoria = Auditoria(
            usuario_id=usuario.id,
            accion="LOGOUT",
            detalle="Logout del sistema",
            ip=request.client.host if request.client else None
        )
        db.add(auditoria)
        db.commit()
    except:
        pass
    
    return {"mensaje": "Logout exitoso"}
