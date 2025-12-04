"""
Script para crear las tablas en PostgreSQL
Ejecutar ANTES de iniciar la aplicación
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Misma URL de tu database.py
DATABASE_URL = "postgresql://ufrqizsynh7hw1lwkypl:TDIEkb5nDrOF8Ow4SVacVAicm8bjb8@bcjwxq3t9ckvbf5r82mu-postgresql.services.clever-cloud.com:50013/bcjwxq3t9ckvbf5r82mu"

def verificar_conexion():
    """Verificar que podemos conectarnos a la base de datos"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexión exitosa a PostgreSQL")
            print(f"   Versión: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def crear_tablas():
    """Crear todas las tablas necesarias"""
    if not verificar_conexion():
        return False
    
    try:
        # Importar Base y modelos DESPUÉS de verificar conexión
        from database import Base, engine
        import models  # Esto debe importar Usuario, Conductor, Vehiculo, Viaje
        
        print("\n🔄 Creando tablas...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Verificar que se crearon
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        
        if tablas:
            print(f"✅ {len(tablas)} tabla(s) creada(s):")
            for tabla in tablas:
                columnas = inspector.get_columns(tabla)
                print(f"\n   📋 {tabla} ({len(columnas)} columnas)")
                for col in columnas[:3]:  # Mostrar solo primeras 3 columnas
                    print(f"      - {col['name']}: {col['type']}")
            return True
        else:
            print("⚠️ No se encontraron tablas después de la creación")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIALIZACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    if crear_tablas():
        print("\n" + "=" * 60)
        print("✅ Base de datos lista para usar")
        print("=" * 60)
        print("\nAhora puedes ejecutar: uvicorn main:app --reload")
    else:
        print("\n" + "=" * 60)
        print("❌ Hubo errores en la inicialización")
        print("=" * 60)