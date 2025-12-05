"""
Script de Inicialización de Base de Datos
Crea usuario administrador y datos iniciales
Sistema de Gases Medicinales MSPBS
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base, init_db
from app.models.models import Usuario, Hospital, Gas, Configuracion
from app.core.security import get_password_hash


def crear_usuario_admin(db: Session):
    """Crear usuario administrador por defecto"""
    admin_email = "admin@mspbs.gov.py"
    
    # Verificar si ya existe
    existing_admin = db.query(Usuario).filter(Usuario.email == admin_email).first()
    if existing_admin:
        print(f"Usuario admin ya existe: {admin_email}")
        return existing_admin
    
    # Crear admin
    admin = Usuario(
        nombre="Administrador",
        apellido="Sistema",
        email=admin_email,
        hash_password=get_password_hash("admin123"),  # Cambiar en producción
        rol="ADMIN",
        estado=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"Usuario admin creado: {admin_email} / admin123")
    return admin


def crear_gases_iniciales(db: Session):
    """Crear catálogo de gases medicinales"""
    gases_data = [
        {
            "nombre": "Oxígeno Medicinal",
            "codigo": "O2",
            "descripcion": "Oxígeno medicinal para uso terapéutico",
            "unidad_base": "m³",
            "formula_quimica": "O₂",
            "es_critico": True
        },
        {
            "nombre": "Aire Medicinal",
            "codigo": "AIR",
            "descripcion": "Aire medicinal comprimido",
            "unidad_base": "m³",
            "formula_quimica": "N₂/O₂",
            "es_critico": False
        },
        {
            "nombre": "Óxido Nitroso",
            "codigo": "N2O",
            "descripcion": "Óxido nitroso para anestesia",
            "unidad_base": "kg",
            "formula_quimica": "N₂O",
            "es_critico": False
        },
        {
            "nombre": "Dióxido de Carbono Medicinal",
            "codigo": "CO2",
            "descripcion": "CO2 medicinal para laparoscopia",
            "unidad_base": "kg",
            "formula_quimica": "CO₂",
            "es_critico": False
        },
        {
            "nombre": "Mezcla Heliox",
            "codigo": "HELIOX",
            "descripcion": "Mezcla de helio y oxígeno",
            "unidad_base": "m³",
            "formula_quimica": "He/O₂",
            "es_critico": False
        },
        {
            "nombre": "Argón Medicinal",
            "codigo": "AR",
            "descripcion": "Argón para procedimientos quirúrgicos",
            "unidad_base": "m³",
            "formula_quimica": "Ar",
            "es_critico": False
        }
    ]
    
    gases_creados = []
    for gas_data in gases_data:
        # Verificar si ya existe
        existing_gas = db.query(Gas).filter(Gas.codigo == gas_data["codigo"]).first()
        if not existing_gas:
            gas = Gas(**gas_data)
            db.add(gas)
            gases_creados.append(gas_data["nombre"])
    
    db.commit()
    
    if gases_creados:
        print(f"Gases creados: {', '.join(gases_creados)}")
    else:
        print("Todos los gases ya existen")


def crear_hospitales_ejemplo(db: Session):
    """Crear algunos hospitales de ejemplo"""
    hospitales_data = [
        {
            "nombre": "Hospital de Clínicas",
            "codigo": "HC-001",
            "tipo": "hospital",
            "ciudad": "Asunción",
            "departamento": "Capital",
            "direccion": "Avenida General Santos y Lagerenza",
            "contacto_nombre": "Dr. Juan Pérez",
            "contacto_telefono": "+595 21 123456",
            "contacto_email": "contacto@clinicas.gov.py",
            "region_sanitaria": "Capital",
            "nivel_atencion": "terciario"
        },
        {
            "nombre": "Instituto Nacional de Cardiología",
            "codigo": "INC-001",
            "tipo": "instituto",
            "ciudad": "Asunción",
            "departamento": "Capital",
            "direccion": "Avenida Mariscal López",
            "region_sanitaria": "Capital",
            "nivel_atencion": "terciario"
        },
        {
            "nombre": "Hospital Regional de Ciudad del Este",
            "codigo": "HR-CDE-001",
            "tipo": "hospital",
            "ciudad": "Ciudad del Este",
            "departamento": "Alto Paraná",
            "region_sanitaria": "Alto Paraná",
            "nivel_atencion": "secundario"
        },
        {
            "nombre": "Centro de Salud San Lorenzo",
            "codigo": "CS-SL-001",
            "tipo": "centro_salud",
            "ciudad": "San Lorenzo",
            "departamento": "Central",
            "region_sanitaria": "Central",
            "nivel_atencion": "primario"
        }
    ]
    
    hospitales_creados = []
    for hospital_data in hospitales_data:
        # Verificar si ya existe
        existing_hospital = db.query(Hospital).filter(
            Hospital.codigo == hospital_data["codigo"]
        ).first()
        if not existing_hospital:
            hospital = Hospital(**hospital_data)
            db.add(hospital)
            hospitales_creados.append(hospital_data["nombre"])
    
    db.commit()
    
    if hospitales_creados:
        print(f"Hospitales creados: {', '.join(hospitales_creados)}")
    else:
        print("Todos los hospitales ya existen")


def crear_configuraciones_iniciales(db: Session):
    """Crear configuraciones iniciales del sistema"""
    configs = [
        {
            "clave": "alerta_consumo_bajo_dias",
            "valor": "30",
            "descripcion": "Días sin registro para generar alerta de consumo bajo",
            "tipo": "number"
        },
        {
            "clave": "alerta_consumo_alto_umbral",
            "valor": "150",
            "descripcion": "Porcentaje sobre promedio para alerta de consumo alto",
            "tipo": "number"
        },
        {
            "clave": "backup_automatico_habilitado",
            "valor": "true",
            "descripcion": "Habilitar backup automático de base de datos",
            "tipo": "boolean"
        },
        {
            "clave": "dias_retencion_auditoria",
            "valor": "180",
            "descripcion": "Días de retención de registros de auditoría",
            "tipo": "number"
        }
    ]
    
    for config_data in configs:
        existing_config = db.query(Configuracion).filter(
            Configuracion.clave == config_data["clave"]
        ).first()
        if not existing_config:
            config = Configuracion(**config_data)
            db.add(config)
    
    db.commit()
    print("Configuraciones iniciales creadas")


def main():
    """Función principal de inicialización"""
    print("=== Inicializando Base de Datos ===")
    print(f"Sistema de Gases Medicinales - MSPBS Paraguay")
    print("=" * 40)
    
    # Crear todas las tablas
    print("\n1. Creando tablas...")
    init_db()
    print("✓ Tablas creadas")
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Crear usuario admin
        print("\n2. Creando usuario administrador...")
        crear_usuario_admin(db)
        print("✓ Usuario admin creado")
        
        # Crear gases
        print("\n3. Creando catálogo de gases medicinales...")
        crear_gases_iniciales(db)
        print("✓ Gases creados")
        
        # Crear hospitales de ejemplo
        print("\n4. Creando hospitales de ejemplo...")
        crear_hospitales_ejemplo(db)
        print("✓ Hospitales creados")
        
        # Crear configuraciones
        print("\n5. Creando configuraciones iniciales...")
        crear_configuraciones_iniciales(db)
        print("✓ Configuraciones creadas")
        
        print("\n" + "=" * 40)
        print("✓ Inicialización completada exitosamente")
        print("=" * 40)
        print("\nCredenciales de acceso:")
        print("Email: admin@mspbs.gov.py")
        print("Password: admin123")
        print("\n¡IMPORTANTE! Cambia la contraseña del admin en producción")
        
    except Exception as e:
        print(f"\n✗ Error durante la inicialización: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
