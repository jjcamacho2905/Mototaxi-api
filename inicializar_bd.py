"""
Script para crear tablas en PostgreSQL
Ejecutar UNA SOLA VEZ al inicio del proyecto
"""
from database import engine
import models

def crear_tablas():
    print("=" * 60)
    print("📋 Creando tablas en PostgreSQL - Clever Cloud")
    print("=" * 60)
    
    try:
        print("\n🔨 Creando estructura de base de datos...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente\n")
        
        print("📊 Tablas creadas:")
        print("   • usuarios")
        print("   • conductores")
        print("   • vehiculos")
        print("   • viajes")
        
        print("\n💡 Próximos pasos:")
        print("   1. Genera datos: python generar_datos_mock.py")
        print("   2. Inicia servidor: uvicorn main:app --reload")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        print("\n💡 Posibles causas:")
        print("   • Las tablas ya existen")
        print("   • Problemas de conexión")
        print("   • Límite de conexiones alcanzado")

if __name__ == "__main__":
    crear_tablas()