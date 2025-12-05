"""
Schemas Pydantic para Validación
Sistema de Gases Medicinales MSPBS
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ============ ENUMS ============
class RolEnum(str, Enum):
    ADMIN = "ADMIN"
    HOSPITAL_USER = "HOSPITAL_USER"


class TipoHospitalEnum(str, Enum):
    HOSPITAL = "hospital"
    CENTRO_SALUD = "centro_salud"
    INSTITUTO = "instituto"


class ModoSuministroEnum(str, Enum):
    TANQUE_CRIOGENICO = "tanque_criogenico"
    CILINDROS = "cilindros"
    RED_CENTRAL = "red_central"
    PSA = "PSA"
    OTRO = "otro"


class SeveridadAlertaEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ============ USUARIOS ============
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: RolEnum
    hospital_id: Optional[int] = None
    estado: bool = True


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=50)
    
    @validator('hospital_id')
    def validate_hospital_user(cls, v, values):
        if values.get('rol') == RolEnum.HOSPITAL_USER and v is None:
            raise ValueError('Usuario de hospital debe tener hospital_id')
        if values.get('rol') == RolEnum.ADMIN and v is not None:
            raise ValueError('Usuario ADMIN no debe tener hospital_id')
        return v


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[RolEnum] = None
    hospital_id: Optional[int] = None
    estado: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    id: int
    ultimo_acceso: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse


class RecuperarPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=50)


# ============ HOSPITALES ============
class HospitalBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=255)
    codigo: str = Field(..., min_length=2, max_length=50)
    tipo: TipoHospitalEnum
    ciudad: str = Field(..., min_length=2, max_length=100)
    departamento: str = Field(..., min_length=2, max_length=100)
    direccion: Optional[str] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[EmailStr] = None
    estado: bool = True
    region_sanitaria: Optional[str] = None
    nivel_atencion: Optional[str] = None


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[TipoHospitalEnum] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    direccion: Optional[str] = None
    contacto_nombre: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_email: Optional[EmailStr] = None
    estado: Optional[bool] = None
    region_sanitaria: Optional[str] = None
    nivel_atencion: Optional[str] = None


class HospitalResponse(HospitalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ GASES ============
class GasBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    codigo: str = Field(..., min_length=2, max_length=20)
    descripcion: Optional[str] = None
    unidad_base: str = Field(..., min_length=1, max_length=20)
    formula_quimica: Optional[str] = None
    estado: bool = True
    es_critico: bool = False


class GasCreate(GasBase):
    pass


class GasUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_base: Optional[str] = None
    formula_quimica: Optional[str] = None
    estado: Optional[bool] = None
    es_critico: Optional[bool] = None


class GasResponse(GasBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ CONSUMOS ============
class ConsumoBase(BaseModel):
    hospital_id: int
    gas_id: int
    fecha_inicio: date
    fecha_fin: date
    modo_suministro: ModoSuministroEnum
    unidad_medida: str = Field(..., min_length=1, max_length=20)
    cantidad: float = Field(..., gt=0)
    observaciones: Optional[str] = None
    
    @validator('fecha_fin')
    def validate_fechas(cls, v, values):
        if 'fecha_inicio' in values and v < values['fecha_inicio']:
            raise ValueError('fecha_fin debe ser mayor o igual a fecha_inicio')
        return v


class ConsumoCreate(ConsumoBase):
    pass


class ConsumoUpdate(BaseModel):
    gas_id: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    modo_suministro: Optional[ModoSuministroEnum] = None
    unidad_medida: Optional[str] = None
    cantidad: Optional[float] = None
    observaciones: Optional[str] = None


class ConsumoResponse(ConsumoBase):
    id: int
    usuario_id: int
    validado: bool
    validado_por: Optional[int]
    fecha_validacion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Relaciones
    hospital: Optional[HospitalResponse] = None
    gas: Optional[GasResponse] = None
    
    class Config:
        from_attributes = True


# ============ REPORTES ============
class FiltroReporte(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    hospital_id: Optional[int] = None
    gas_id: Optional[int] = None
    modo_suministro: Optional[ModoSuministroEnum] = None
    departamento: Optional[str] = None


class ReporteGlobalRequest(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    formato: str = Field(..., pattern="^(PDF|CSV|XLSX)$")


class ReporteHospitalRequest(BaseModel):
    hospital_id: int
    fecha_inicio: date
    fecha_fin: date
    formato: str = Field(..., pattern="^(PDF|CSV|XLSX)$")
    gas_id: Optional[int] = None


class EstadisticaGas(BaseModel):
    gas_id: int
    gas_nombre: str
    total_consumo: float
    unidad: str
    porcentaje: float


class EstadisticaHospital(BaseModel):
    hospital_id: int
    hospital_nombre: str
    hospital_codigo: str
    total_consumo: float
    cantidad_registros: int


class DashboardStats(BaseModel):
    total_hospitales_activos: int
    total_registros_periodo: int
    consumo_total_oxigeno: float
    alertas_pendientes: int
    hospitales_sin_registro: List[str]
    top_consumidores: List[EstadisticaHospital]
    consumo_por_gas: List[EstadisticaGas]


# ============ ALERTAS ============
class AlertaResponse(BaseModel):
    id: int
    hospital_id: Optional[int]
    tipo: str
    severidad: SeveridadAlertaEnum
    mensaje: str
    fecha_deteccion: datetime
    resuelta: bool
    
    class Config:
        from_attributes = True


# ============ AUDITORIA ============
class AuditoriaResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    accion: str
    detalle: Optional[str]
    ip: Optional[str]
    fecha_hora: datetime
    
    class Config:
        from_attributes = True


# ============ PAGINACIÓN ============
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    size: int
    pages: int
