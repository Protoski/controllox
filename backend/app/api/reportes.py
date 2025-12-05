"""
API Endpoints - Reportes y Dashboard
Sistema de Gases Medicinales MSPBS
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date, datetime
import io

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.models import (
    Usuario, Hospital, Gas, Consumo, Alerta
)
from app.schemas.schemas import (
    DashboardStats,
    EstadisticaGas,
    EstadisticaHospital,
    FiltroReporte
)
from app.services.pdf_service import generar_reporte_pdf
from app.services.excel_service import generar_reporte_excel

router = APIRouter(prefix="/reportes", tags=["Reportes y Dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
async def obtener_dashboard(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_admin)
):
    """
    Dashboard principal con estadísticas generales (solo ADMIN)
    """
    # Total hospitales activos
    total_hospitales = db.query(Hospital).filter(Hospital.estado == True).count()
    
    # Construir query base de consumos
    query_consumos = db.query(Consumo)
    if fecha_inicio:
        query_consumos = query_consumos.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query_consumos = query_consumos.filter(Consumo.fecha_fin <= fecha_fin)
    
    # Total registros en periodo
    total_registros = query_consumos.count()
    
    # Consumo total de oxígeno en periodo
    oxigeno = db.query(Gas).filter(Gas.codigo == "O2").first()
    consumo_oxigeno = 0
    if oxigeno:
        result = query_consumos.filter(Consumo.gas_id == oxigeno.id).with_entities(
            func.sum(Consumo.cantidad)
        ).scalar()
        consumo_oxigeno = float(result) if result else 0
    
    # Alertas pendientes
    alertas_pendientes = db.query(Alerta).filter(Alerta.resuelta == False).count()
    
    # Hospitales sin registro en el periodo
    hospitales_con_registro = query_consumos.with_entities(
        Consumo.hospital_id
    ).distinct().all()
    hospitales_con_registro_ids = [h[0] for h in hospitales_con_registro]
    
    hospitales_sin_registro = db.query(Hospital).filter(
        Hospital.estado == True,
        ~Hospital.id.in_(hospitales_con_registro_ids)
    ).all()
    
    hospitales_sin_registro_nombres = [h.nombre for h in hospitales_sin_registro]
    
    # Top 5 hospitales con mayor consumo
    top_hospitales = db.query(
        Hospital.id,
        Hospital.nombre,
        Hospital.codigo,
        func.sum(Consumo.cantidad).label("total_consumo"),
        func.count(Consumo.id).label("cantidad_registros")
    ).join(Consumo).group_by(Hospital.id, Hospital.nombre, Hospital.codigo)
    
    if fecha_inicio:
        top_hospitales = top_hospitales.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        top_hospitales = top_hospitales.filter(Consumo.fecha_fin <= fecha_fin)
    
    top_hospitales = top_hospitales.order_by(func.sum(Consumo.cantidad).desc()).limit(5).all()
    
    top_consumidores = [
        EstadisticaHospital(
            hospital_id=h[0],
            hospital_nombre=h[1],
            hospital_codigo=h[2],
            total_consumo=float(h[3]),
            cantidad_registros=h[4]
        )
        for h in top_hospitales
    ]
    
    # Consumo por tipo de gas
    consumo_por_gas_query = db.query(
        Gas.id,
        Gas.nombre,
        Gas.unidad_base,
        func.sum(Consumo.cantidad).label("total")
    ).join(Consumo).group_by(Gas.id, Gas.nombre, Gas.unidad_base)
    
    if fecha_inicio:
        consumo_por_gas_query = consumo_por_gas_query.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        consumo_por_gas_query = consumo_por_gas_query.filter(Consumo.fecha_fin <= fecha_fin)
    
    consumo_por_gas_result = consumo_por_gas_query.all()
    
    # Calcular total para porcentajes
    total_general = sum([float(g[3]) for g in consumo_por_gas_result if g[3]])
    
    consumo_por_gas = [
        EstadisticaGas(
            gas_id=g[0],
            gas_nombre=g[1],
            unidad=g[2],
            total_consumo=float(g[3]) if g[3] else 0,
            porcentaje=round((float(g[3]) / total_general * 100) if total_general > 0 else 0, 2)
        )
        for g in consumo_por_gas_result
    ]
    
    return DashboardStats(
        total_hospitales_activos=total_hospitales,
        total_registros_periodo=total_registros,
        consumo_total_oxigeno=consumo_oxigeno,
        alertas_pendientes=alertas_pendientes,
        hospitales_sin_registro=hospitales_sin_registro_nombres,
        top_consumidores=top_consumidores,
        consumo_por_gas=consumo_por_gas
    )


@router.get("/dashboard/hospital")
async def obtener_dashboard_hospital(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Dashboard para usuarios de hospital
    """
    if current_user.rol == "HOSPITAL_USER" and not current_user.hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no tiene hospital asignado"
        )
    
    hospital_id = current_user.hospital_id if current_user.rol == "HOSPITAL_USER" else None
    
    if not hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital no especificado"
        )
    
    # Query de consumos del hospital
    query_consumos = db.query(Consumo).filter(Consumo.hospital_id == hospital_id)
    if fecha_inicio:
        query_consumos = query_consumos.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        query_consumos = query_consumos.filter(Consumo.fecha_fin <= fecha_fin)
    
    # Total registros
    total_registros = query_consumos.count()
    
    # Consumo por gas
    consumo_por_gas = db.query(
        Gas.nombre,
        Gas.unidad_base,
        func.sum(Consumo.cantidad).label("total")
    ).join(Consumo).filter(Consumo.hospital_id == hospital_id)
    
    if fecha_inicio:
        consumo_por_gas = consumo_por_gas.filter(Consumo.fecha_inicio >= fecha_inicio)
    if fecha_fin:
        consumo_por_gas = consumo_por_gas.filter(Consumo.fecha_fin <= fecha_fin)
    
    consumo_por_gas = consumo_por_gas.group_by(Gas.nombre, Gas.unidad_base).all()
    
    return {
        "hospital": db.query(Hospital).filter(Hospital.id == hospital_id).first().nombre,
        "total_registros": total_registros,
        "consumo_por_gas": [
            {
                "gas": g[0],
                "unidad": g[1],
                "total": float(g[2]) if g[2] else 0
            }
            for g in consumo_por_gas
        ]
    }


@router.post("/generar-pdf")
async def generar_pdf(
    filtros: FiltroReporte,
    tipo_reporte: str = "global",  # global, hospital, gas
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Generar reporte en PDF
    """
    # Verificar permisos para tipo de reporte
    if tipo_reporte == "global" and current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo ADMIN puede generar reportes globales"
        )
    
    if tipo_reporte == "hospital" and current_user.rol == "HOSPITAL_USER":
        if not filtros.hospital_id or filtros.hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede generar reportes de su hospital"
            )
    
    # Obtener datos para el reporte
    query = db.query(Consumo)
    
    if filtros.hospital_id:
        query = query.filter(Consumo.hospital_id == filtros.hospital_id)
    if filtros.gas_id:
        query = query.filter(Consumo.gas_id == filtros.gas_id)
    if filtros.fecha_inicio:
        query = query.filter(Consumo.fecha_inicio >= filtros.fecha_inicio)
    if filtros.fecha_fin:
        query = query.filter(Consumo.fecha_fin <= filtros.fecha_fin)
    if filtros.modo_suministro:
        query = query.filter(Consumo.modo_suministro == filtros.modo_suministro)
    
    consumos = query.all()
    
    # Cargar relaciones
    for consumo in consumos:
        consumo.hospital
        consumo.gas
    
    # Generar PDF
    pdf_buffer = generar_reporte_pdf(
        consumos=consumos,
        tipo_reporte=tipo_reporte,
        filtros=filtros,
        usuario=current_user
    )
    
    # Retornar PDF
    filename = f"reporte_{tipo_reporte}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/generar-excel")
async def generar_excel(
    filtros: FiltroReporte,
    formato: str = "xlsx",  # xlsx, csv
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Generar reporte en Excel o CSV
    """
    # Obtener datos
    query = db.query(Consumo)
    
    if filtros.hospital_id:
        query = query.filter(Consumo.hospital_id == filtros.hospital_id)
    if filtros.gas_id:
        query = query.filter(Consumo.gas_id == filtros.gas_id)
    if filtros.fecha_inicio:
        query = query.filter(Consumo.fecha_inicio >= filtros.fecha_inicio)
    if filtros.fecha_fin:
        query = query.filter(Consumo.fecha_fin <= filtros.fecha_fin)
    
    consumos = query.all()
    
    # Cargar relaciones
    for consumo in consumos:
        consumo.hospital
        consumo.gas
    
    # Generar archivo
    if formato == "xlsx":
        file_buffer = generar_reporte_excel(consumos)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        extension = "xlsx"
    else:
        file_buffer = generar_reporte_excel(consumos, formato="csv")
        media_type = "text/csv"
        extension = "csv"
    
    filename = f"reporte_consumos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    
    return StreamingResponse(
        io.BytesIO(file_buffer),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/consumo-mensual")
async def obtener_consumo_mensual(
    hospital_id: Optional[int] = None,
    gas_id: Optional[int] = None,
    año: int = datetime.now().year,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener consumo mensual para gráficos
    """
    from sqlalchemy import extract
    
    # Verificar permisos
    if current_user.rol == "HOSPITAL_USER":
        hospital_id = current_user.hospital_id
    
    query = db.query(
        extract('month', Consumo.fecha_inicio).label('mes'),
        func.sum(Consumo.cantidad).label('total')
    )
    
    if hospital_id:
        query = query.filter(Consumo.hospital_id == hospital_id)
    if gas_id:
        query = query.filter(Consumo.gas_id == gas_id)
    
    query = query.filter(extract('year', Consumo.fecha_inicio) == año)
    query = query.group_by(extract('month', Consumo.fecha_inicio))
    query = query.order_by(extract('month', Consumo.fecha_inicio))
    
    resultados = query.all()
    
    # Crear array con todos los meses
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    datos_mensuales = {i+1: 0 for i in range(12)}
    for mes, total in resultados:
        datos_mensuales[int(mes)] = float(total) if total else 0
    
    return {
        "meses": meses,
        "valores": [datos_mensuales[i+1] for i in range(12)]
    }
