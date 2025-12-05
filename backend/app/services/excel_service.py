"""
Servicio de Generación de Excel/CSV
Sistema de Gases Medicinales MSPBS
"""

import pandas as pd
from typing import List
from io import BytesIO

from app.models.models import Consumo


def generar_reporte_excel(consumos: List[Consumo], formato: str = "xlsx") -> bytes:
    """
    Generar reporte en Excel o CSV
    """
    # Preparar datos
    data = []
    for consumo in consumos:
        data.append({
            "ID": consumo.id,
            "Hospital": consumo.hospital.nombre,
            "Código Hospital": consumo.hospital.codigo,
            "Departamento": consumo.hospital.departamento,
            "Ciudad": consumo.hospital.ciudad,
            "Gas": consumo.gas.nombre,
            "Código Gas": consumo.gas.codigo,
            "Fecha Inicio": consumo.fecha_inicio.strftime("%Y-%m-%d"),
            "Fecha Fin": consumo.fecha_fin.strftime("%Y-%m-%d"),
            "Modo Suministro": consumo.modo_suministro,
            "Cantidad": consumo.cantidad,
            "Unidad": consumo.unidad_medida,
            "Observaciones": consumo.observaciones or "",
            "Validado": "Sí" if consumo.validado else "No",
            "Fecha Registro": consumo.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Generar archivo
    buffer = BytesIO()
    
    if formato == "xlsx":
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Consumos', index=False)
            
            # Obtener workbook y worksheet
            workbook = writer.book
            worksheet = writer.sheets['Consumos']
            
            # Ajustar anchos de columna
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Formato de encabezado
            from openpyxl.styles import Font, PatternFill, Alignment
            
            header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
    else:
        # CSV
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
    
    buffer.seek(0)
    return buffer.getvalue()


def generar_resumen_consumos(consumos: List[Consumo]) -> dict:
    """
    Generar resumen estadístico de consumos
    """
    if not consumos:
        return {
            "total_registros": 0,
            "total_consumo": 0,
            "por_gas": {},
            "por_hospital": {},
            "por_modo_suministro": {}
        }
    
    # Agrupar por gas
    por_gas = {}
    for consumo in consumos:
        gas_nombre = consumo.gas.nombre
        if gas_nombre not in por_gas:
            por_gas[gas_nombre] = {
                "cantidad": 0,
                "unidad": consumo.gas.unidad_base,
                "registros": 0
            }
        por_gas[gas_nombre]["cantidad"] += consumo.cantidad
        por_gas[gas_nombre]["registros"] += 1
    
    # Agrupar por hospital
    por_hospital = {}
    for consumo in consumos:
        hospital_nombre = consumo.hospital.nombre
        if hospital_nombre not in por_hospital:
            por_hospital[hospital_nombre] = {
                "cantidad": 0,
                "registros": 0
            }
        por_hospital[hospital_nombre]["cantidad"] += consumo.cantidad
        por_hospital[hospital_nombre]["registros"] += 1
    
    # Agrupar por modo de suministro
    por_modo = {}
    for consumo in consumos:
        modo = consumo.modo_suministro
        if modo not in por_modo:
            por_modo[modo] = {
                "cantidad": 0,
                "registros": 0
            }
        por_modo[modo]["cantidad"] += consumo.cantidad
        por_modo[modo]["registros"] += 1
    
    return {
        "total_registros": len(consumos),
        "total_consumo": sum([c.cantidad for c in consumos]),
        "por_gas": por_gas,
        "por_hospital": por_hospital,
        "por_modo_suministro": por_modo
    }
