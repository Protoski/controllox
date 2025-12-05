"""
Modelos de Base de Datos - Sistema de Gases Medicinales MSPBS
DGGIES - Dirección General de Gestión de Información y Estadísticas de Salud
Ministerio de Salud y Bienestar Social - Paraguay
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Usuario(Base):
    """Modelo de usuarios del sistema"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hash_password = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)  # ADMIN, HOSPITAL_USER
    hospital_id = Column(Integer, ForeignKey("hospitales.id"), nullable=True)
    estado = Column(Boolean, default=True)
    ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    token_recuperacion = Column(String(255), nullable=True)
    token_expiracion = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    hospital = relationship("Hospital", back_populates="usuarios")
    consumos = relationship("Consumo", back_populates="usuario")
    auditorias = relationship("Auditoria", back_populates="usuario")


class Hospital(Base):
    """Modelo de hospitales y centros de salud"""
    __tablename__ = "hospitales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=False)  # hospital, centro_salud, instituto
    ciudad = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=True)
    contacto_nombre = Column(String(200), nullable=True)
    contacto_telefono = Column(String(50), nullable=True)
    contacto_email = Column(String(255), nullable=True)
    estado = Column(Boolean, default=True)
    region_sanitaria = Column(String(100), nullable=True)  # Específico de Paraguay
    nivel_atencion = Column(String(50), nullable=True)  # primario, secundario, terciario
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    usuarios = relationship("Usuario", back_populates="hospital")
    consumos = relationship("Consumo", back_populates="hospital")
    alertas = relationship("Alerta", back_populates="hospital")


class Gas(Base):
    """Catálogo maestro de gases medicinales"""
    __tablename__ = "gases"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    unidad_base = Column(String(20), nullable=False)  # m³, L, kg
    formula_quimica = Column(String(50), nullable=True)
    estado = Column(Boolean, default=True)
    es_critico = Column(Boolean, default=False)  # Para alertas de bajo consumo/problemas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    consumos = relationship("Consumo", back_populates="gas")


class Consumo(Base):
    """Registro de consumos de gases medicinales"""
    __tablename__ = "consumos"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitales.id"), nullable=False)
    gas_id = Column(Integer, ForeignKey("gases.id"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    modo_suministro = Column(String(50), nullable=False)  # tanque_criogenico, cilindros, red_central, PSA
    unidad_medida = Column(String(20), nullable=False)
    cantidad = Column(Float, nullable=False)
    observaciones = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    validado = Column(Boolean, default=False)  # Para validación por ADMIN
    validado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_validacion = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    hospital = relationship("Hospital", back_populates="consumos")
    gas = relationship("Gas", back_populates="consumos")
    usuario = relationship("Usuario", back_populates="consumos", foreign_keys=[usuario_id])


class Auditoria(Base):
    """Registro de auditoría del sistema"""
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    accion = Column(String(100), nullable=False)
    detalle = Column(Text, nullable=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="auditorias")


class Alerta(Base):
    """Sistema de alertas para consumos anormales o problemas"""
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitales.id"), nullable=True)
    tipo = Column(String(50), nullable=False)  # consumo_alto, consumo_bajo, sin_registro
    severidad = Column(String(20), nullable=False)  # info, warning, critical
    mensaje = Column(Text, nullable=False)
    fecha_deteccion = Column(DateTime(timezone=True), server_default=func.now())
    resuelta = Column(Boolean, default=False)
    resuelta_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_resolucion = Column(DateTime(timezone=True), nullable=True)
    notas_resolucion = Column(Text, nullable=True)

    # Relaciones
    hospital = relationship("Hospital", back_populates="alertas")


class Configuracion(Base):
    """Configuraciones generales del sistema"""
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(20), default="string")  # string, number, boolean, json
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class HistorialExportacion(Base):
    """Registro de exportaciones de reportes"""
    __tablename__ = "historial_exportacion"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_reporte = Column(String(50), nullable=False)
    formato = Column(String(10), nullable=False)  # PDF, CSV, XLSX
    parametros = Column(Text, nullable=True)  # JSON con filtros aplicados
    archivo_generado = Column(String(255), nullable=True)
    fecha_generacion = Column(DateTime(timezone=True), server_default=func.now())
