"""
Servicio de Generación de PDFs
Sistema de Gases Medicinales MSPBS
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from typing import List
import os

from app.models.models import Consumo, Usuario
from app.schemas.schemas import FiltroReporte
from app.core.config import settings


def generar_reporte_pdf(
    consumos: List[Consumo],
    tipo_reporte: str,
    filtros: FiltroReporte,
    usuario: Usuario
) -> bytes:
    """
    Generar reporte PDF de consumos
    """
    buffer = BytesIO()
    
    # Crear documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    titulo_style = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle(
        'SubtituloCustom',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = styles['Normal']
    normal_style.fontSize = 9
    
    # Header con logo (si existe)
    if os.path.exists(settings.LOGO_PATH):
        try:
            logo = Image(settings.LOGO_PATH, width=1.5*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 12))
        except:
            pass
    
    # Título principal
    elements.append(Paragraph(
        f"{settings.ORGANIZACION}",
        titulo_style
    ))
    elements.append(Paragraph(
        f"Ministerio de Salud y Bienestar Social - {settings.PAIS}",
        normal_style
    ))
    elements.append(Spacer(1, 12))
    
    # Título del reporte
    if tipo_reporte == "global":
        titulo_reporte = "REPORTE GLOBAL DE CONSUMO DE GASES MEDICINALES"
    elif tipo_reporte == "hospital":
        hospital_nombre = consumos[0].hospital.nombre if consumos else "N/A"
        titulo_reporte = f"REPORTE DE CONSUMO - {hospital_nombre}"
    else:
        titulo_reporte = "REPORTE DE CONSUMO DE GASES MEDICINALES"
    
    elements.append(Paragraph(titulo_reporte, subtitulo_style))
    elements.append(Spacer(1, 12))
    
    # Información del reporte
    info_data = [
        ["Fecha de generación:", datetime.now().strftime("%d/%m/%Y %H:%M")],
        ["Generado por:", f"{usuario.nombre} {usuario.apellido}"],
    ]
    
    if filtros.fecha_inicio:
        info_data.append(["Periodo desde:", filtros.fecha_inicio.strftime("%d/%m/%Y")])
    if filtros.fecha_fin:
        info_data.append(["Periodo hasta:", filtros.fecha_fin.strftime("%d/%m/%Y")])
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Tabla de consumos
    if consumos:
        # Encabezados
        headers = ["Hospital", "Gas", "Periodo", "Modo", "Cantidad", "Unidad"]
        
        # Datos
        data = [headers]
        for consumo in consumos:
            data.append([
                consumo.hospital.codigo,
                consumo.gas.nombre,
                f"{consumo.fecha_inicio.strftime('%d/%m/%y')} - {consumo.fecha_fin.strftime('%d/%m/%y')}",
                consumo.modo_suministro.replace('_', ' ').title(),
                f"{consumo.cantidad:.2f}",
                consumo.unidad_medida
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.3*inch, 1.2*inch, 0.8*inch, 0.6*inch])
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Resumen
        total_registros = len(consumos)
        total_consumo = sum([c.cantidad for c in consumos])
        
        resumen_data = [
            ["RESUMEN"],
            ["Total de registros:", str(total_registros)],
            ["Consumo total:", f"{total_consumo:.2f}"],
        ]
        
        resumen_table = Table(resumen_data, colWidths=[2*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('SPAN', (0, 0), (-1, 0)),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(resumen_table)
    else:
        elements.append(Paragraph("No hay datos para mostrar con los filtros seleccionados.", normal_style))
    
    # Pie de página
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        f"Documento generado automáticamente por {settings.APP_NAME} v{settings.APP_VERSION}",
        ParagraphStyle('Footer', fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
