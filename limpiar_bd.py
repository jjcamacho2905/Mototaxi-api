"""
Script para limpiar completamente la base de datos
Ejecutar con: python limpiar_bd.py
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pathlib import Path
import shutil

def limpiar_archivos_uploads():
    """Elimina todas las imágenes subidas"""
    upload_dir = Path("app/static/uploads")
    if upload_dir.exists():
        archivos_eliminados = 0
        for archivo in upload_dir.iterdir():
            if archivo.is_file():
                archivo.unlink()
                archivos_eliminados += 1
        return archivos_eliminados
    return 0

def limpiar_base_datos():
    print("=" * 60)
    print("🗑️  LIMPIANDO BASE DE DATOS")
    print("=" * 60)
    
    print("\n⚠️  ADVERTENCIA: Esta acción eliminará:")
    print("   • Todos los viajes")
    print("   • Todos los vehículos")
    print("   • Todos los conductores")
    print("   • Todos los usuarios")
    print("   • Todas las imágenes subidas")
    
    respuesta = input("\n¿SEGURO que deseas ELIMINAR TODOS LOS DATOS? (escribe 'SI' en mayúsculas): ")
    
    if respuesta != 'SI':
        print("\n❌ Operación cancelada")
        print("💡 Para confirmar, debes escribir 'SI' exactamente")
        return
    
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("🗑️  Eliminando registros de la base de datos...")
        print("=" * 60)
        
        # Eliminar en orden (por las relaciones de foreign keys)
        print("\n1️⃣  Eliminando viajes...")
        viajes_eliminados = db.query(models.Viaje).delete()
        print(f"   ✓ {viajes_eliminados} viajes eliminados")
        
        print("\n2️⃣  Eliminando vehículos...")
        vehiculos_eliminados = db.query(models.Vehiculo).delete()
        print(f"   ✓ {vehiculos_eliminados} vehículos eliminados")
        
        print("\n3️⃣  Eliminando conductores...")
        conductores_eliminados = db.query(models.Conductor).delete()
        print(f"   ✓ {conductores_eliminados} conductores eliminados")
        
        print("\n4️⃣  Eliminando usuarios...")
        usuarios_eliminados = db.query(models.Usuario).delete()
        print(f"   ✓ {usuarios_eliminados} usuarios eliminados")
        
        db.commit()
        
        # Limpiar archivos
        print("\n5️⃣  Eliminando imágenes subidas...")
        archivos = limpiar_archivos_uploads()
        print(f"   ✓ {archivos} archivos eliminados")
        
        print("\n" + "=" * 60)
        print("✅ BASE DE DATOS LIMPIADA EXITOSAMENTE")
        print("=" * 60)
        
        print("\n📊 Resumen:")
        print(f"   • Viajes eliminados: {viajes_eliminados}")
        print(f"   • Vehículos eliminados: {vehiculos_eliminados}")
        print(f"   • Conductores eliminados: {conductores_eliminados}")
        print(f"   • Usuarios eliminados: {usuarios_eliminados}")
        print(f"   • Imágenes eliminadas: {archivos}")
        
        print("\n💡 Próximos pasos:")
        print("   1. Generar datos nuevos: python generar_datos_mock.py")
        print("   2. O iniciar servidor vacío: uvicorn main:app --reload")
        print("   3. Acceder a: http://127.0.0.1:8000")
        
    except Exception as e:
        print(f"\n❌ Error al limpiar la base de datos: {e}")
        print("💡 Puede que haya relaciones o restricciones activas")
        db.rollback()
    finally:
        db.close()

def verificar_estado():
    """Muestra el estado actual de la base de datos"""
    db = SessionLocal()
    try:
        viajes = db.query(models.Viaje).count()
        vehiculos = db.query(models.Vehiculo).count()
        conductores = db.query(models.Conductor).count()
        usuarios = db.query(models.Usuario).count()
        
        print("\n📊 Estado actual de la base de datos:")
        print(f"   • Usuarios: {usuarios}")
        print(f"   • Conductores: {conductores}")
        print(f"   • Vehículos: {vehiculos}")
        print(f"   • Viajes: {viajes}")
        print(f"   Total de registros: {usuarios + conductores + vehiculos + viajes}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  🚖 SISTEMA MOTOTAXI SUPATÁ - LIMPIAR BASE DE DATOS    ║")
    print("╚" + "═" * 58 + "╝")
    
    # Mostrar estado actual
    verificar_estado()
    
    # Preguntar qué hacer
    print("\n¿Qué deseas hacer?")
    print("  1. Limpiar toda la base de datos")
    print("  2. Solo ver el estado actual")
    print("  3. Cancelar")
    
    opcion = input("\nSelecciona una opción (1/2/3): ")
    
    if opcion == "1":
        limpiar_base_datos()
    elif opcion == "2":
        print("\n✅ Estado mostrado arriba")
    else:
        print("\n❌ Operación cancelada")