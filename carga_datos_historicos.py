"""
Script para cargar datos históricos de rutas de Supatá
Ejecutar con: python cargar_datos_historicos.py
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Crear tablas
models.Base.metadata.create_all(bind=engine)

# Datos históricos de rutas reales de Supatá, Cundinamarca
RUTAS_HISTORICAS = [
    {
        "origen": "Centro Supatá",
        "destino": "Vereda Monte dulce",
        "distancia_km": 8.5,
        "tarifa_base": 18000,
        "tarifa_maxima": 25000,
        "tiempo_estimado_min": 30,
        "viajes_historicos": 145
    },
    {
        "origen": "Centro Supatá",
        "destino": "Vereda  Paraiso",
        "distancia_km": 6.2,
        "tarifa_base": 10000,
        "tarifa_maxima": 20000,
        "tiempo_estimado_min": 18,
        "viajes_historicos": 230
    },
    {
        "origen": "Centro Supatá",
        "destino": "Vereda Encantado",
        "distancia_km": 12.0,
        "tarifa_base": 12000,
        "tarifa_maxima": 22000,
        "tiempo_estimado_min": 20,
        "viajes_historicos": 89
    },
    {
        "origen": "Centro Supatá",
        "destino": "Hospital Municipal",
        "distancia_km": 2.5,
        "tarifa_base": 5000,
        "tarifa_maxima": 6000,
        "tiempo_estimado_min": 8,
        "viajes_historicos": 450
    },
    {
        "origen": "Centro Supatá",
        "destino": "Colegio Departamental",
        "distancia_km": 3.0,
        "tarifa_base": 5000,
        "tarifa_maxima": 6000,
        "tiempo_estimado_min": 8,
        "viajes_historicos": 380
    },
    {
        "origen": "Centro Supatá",
        "destino": "Vereda Reforma",
        "distancia_km": 12.5,
        "tarifa_base": 23000,
        "tarifa_maxima": 30000,
        "tiempo_estimado_min": 30,
        "viajes_historicos": 67
    },
    {
        "origen": "Vereda Magola",
        "destino": "Centro Supatá",
        "distancia_km": 13.5,
        "tarifa_base": 22000,
        "tarifa_maxima": 28000,
        "tiempo_estimado_min": 25,
        "viajes_historicos": 132
    },
    {
        "origen": "Hospital Municipal",
        "destino": "Vereda Paraiso",
        "distancia_km": 7.0,
        "tarifa_base": 11000,
        "tarifa_maxima": 13000,
        "tiempo_estimado_min": 20,
        "viajes_historicos": 45
    },
    {
        "origen": "Centro Supatá",
        "destino": "Vereda Imparal",
        "distancia_km": 15.0,
        "tarifa_base": 50000,
        "tarifa_maxima": 65000,
        "tiempo_estimado_min": 45,
        "viajes_historicos": 34
    },
    {
        "origen": "Centro Supatá",
        "destino": "Canchas de futbol",
        "distancia_km": 0.5,
        "tarifa_base": 3000,
        "tarifa_maxima": 4000,
        "tiempo_estimado_min": 5,
        "viajes_historicos": 520
    },
]

def cargar_datos():
    db = SessionLocal()
    try:
        # Verificar si ya existen datos
        existe = db.query(models.RutaHistorica).first()
        if existe:
            print("⚠️  Ya existen datos históricos en la base de datos")
            print(f"   Total de rutas: {db.query(models.RutaHistorica).count()}")
            return
        
        print("📊 Cargando datos históricos...")
        
        # Insertar rutas históricas
        for ruta_data in RUTAS_HISTORICAS:
            ruta = models.RutaHistorica(**ruta_data)
            db.add(ruta)
        
        db.commit()
        print(f"✅ Se cargaron {len(RUTAS_HISTORICAS)} rutas históricas exitosamente")
        print(f"   Total de viajes históricos: {sum(r['viajes_historicos'] for r in RUTAS_HISTORICAS)}")
        
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚖 Sistema Mototaxi Supatá - Carga de Datos Históricos")
    print("=" * 60)
    cargar_datos()
    print("=" * 60)