"""
Script para generar datos mock realistas del proyecto Mototaxi Supatá
Ejecutar: python generar_datos_mock.py
"""

from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas, crud
from datetime import datetime, timedelta
import random

# Datos realistas de Supatá, Cundinamarca
NOMBRES_USUARIOS = [
    "Carlos Rodríguez", "María González", "Juan Martínez", "Ana Ramírez",
    "Pedro Sánchez", "Laura Torres", "José García", "Camila López",
    "Diego Hernández", "Valentina Díaz", "Andrés Castro", "Sofía Vargas",
    "Miguel Ángel Ruiz", "Isabella Moreno", "Santiago Gutiérrez", "Mariana Rojas",
    "Sebastián Ortiz", "Daniela Castillo", "Alejandro Jiménez", "Natalia Rincón"
]

NOMBRES_CONDUCTORES = [
    "Roberto Pérez", "Fernando Gómez", "Alberto Silva", "Héctor Mendoza",
    "Ricardo Parra", "Luis Eduardo Ávila", "Jorge Mario Cruz", "Gustavo León",
    "Fabio Murillo", "Víctor Hugo Reyes", "Javier Suárez", "Wilson Cortés",
    "Óscar Velásquez", "Mauricio Bravo", "Iván Salazar", "César Morales"
]

# Lugares reales de Supatá
ORIGENES = [
    "Plaza Principal Supatá", "Iglesia de Supatá", "Hospital San Rafael",
    "Colegio Departamental", "Parque Municipal", "Terminal de Transporte",
    "Mercado Municipal", "Centro Comercial", "Barrio El Centro",
    "Vereda San José", "Vereda La Palma", "Vereda El Cuadrado"
]

DESTINOS = [
    "La Vega", "San Francisco", "Villeta", "Sasaima", "Útica",
    "Bogotá", "Nocaima", "Quebradanegra", "Nimaima", "Albán",
    "Vereda El Tablazo", "Vereda La Fría", "Finca El Paraíso",
    "Alto del Zorro", "Puente Piedra", "Mirador Los Alpes"
]

MODELOS_VEHICULOS = [
    "Bajaj Qute 2023", "Bajaj RE 2022", "Bajaj Maxima 2023",
    "Piaggio Ape City 2022", "TVS King 2023", "Atul Auto Shakti 2022",
    "Mahindra Alfa 2023", "Bajaj RE Compact 2022", "Force Urbania 2023"
]

def generar_telefono():
    """Genera un número de teléfono colombiano realista"""
    prefijos = ["310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "350"]
    prefijo = random.choice(prefijos)
    numero = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefijo}{numero}"

def generar_placa():
    """Genera una placa colombiana realista"""
    letras = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    return f"{letras}-{numeros}"

def generar_licencia():
    """Genera un número de licencia de conducir"""
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generar_precio_viaje(origen, destino):
    """Genera un precio realista según la distancia"""
    # Viajes dentro de Supatá: $3,000 - $8,000
    if "Vereda" in origen or "Vereda" in destino or "Barrio" in origen:
        return random.randint(3000, 8000)
    # Viajes a municipios cercanos: $10,000 - $25,000
    elif destino in ["La Vega", "San Francisco", "Villeta", "Sasaima", "Útica"]:
        return random.randint(10000, 25000)
    # Viajes largos (Bogotá, etc): $30,000 - $60,000
    else:
        return random.randint(30000, 60000)

def limpiar_base_datos(db: Session):
    """Elimina todos los datos existentes"""
    print("🗑️  Limpiando base de datos...")
    db.query(models.Viaje).delete()
    db.query(models.Vehiculo).delete()
    db.query(models.Conductor).delete()
    db.query(models.Usuario).delete()
    db.commit()
    print("✅ Base de datos limpiada")

def generar_usuarios(db: Session, cantidad: int = 20):
    """Genera usuarios con datos realistas"""
    print(f"\n👥 Generando {cantidad} usuarios...")
    usuarios_creados = []
    
    for i, nombre in enumerate(NOMBRES_USUARIOS[:cantidad], 1):
        usuario = schemas.UsuarioCrear(
            nombre=nombre,
            telefono=generar_telefono(),
            contrasena="password123"  # En producción, usar contraseñas únicas
        )
        usuario_db = crud.crear_usuario(db, usuario)
        usuarios_creados.append(usuario_db)
        print(f"  ✓ Usuario {i}: {nombre}")
    
    print(f"✅ {len(usuarios_creados)} usuarios creados")
    return usuarios_creados

def generar_conductores(db: Session, cantidad: int = 15):
    """Genera conductores con datos realistas"""
    print(f"\n🏍️  Generando {cantidad} conductores...")
    conductores_creados = []
    
    for i, nombre in enumerate(NOMBRES_CONDUCTORES[:cantidad], 1):
        conductor = schemas.ConductorCrear(
            nombre=nombre,
            licencia=generar_licencia()
        )
        conductor_db = crud.crear_conductor(db, conductor)
        conductores_creados.append(conductor_db)
        print(f"  ✓ Conductor {i}: {nombre} - Licencia: {conductor_db.licencia}")
    
    print(f"✅ {len(conductores_creados)} conductores creados")
    return conductores_creados

def generar_vehiculos(db: Session, cantidad: int = 15):
    """Genera vehículos con datos realistas"""
    print(f"\n🚗 Generando {cantidad} vehículos...")
    vehiculos_creados = []
    placas_usadas = set()
    
    for i in range(cantidad):
        # Generar placa única
        placa = generar_placa()
        while placa in placas_usadas:
            placa = generar_placa()
        placas_usadas.add(placa)
        
        vehiculo = schemas.VehiculoCrear(
            placa=placa,
            modelo=random.choice(MODELOS_VEHICULOS)
        )
        vehiculo_db = crud.crear_vehiculo(db, vehiculo)
        vehiculos_creados.append(vehiculo_db)
        print(f"  ✓ Vehículo {i+1}: {placa} - {vehiculo_db.modelo}")
    
    print(f"✅ {len(vehiculos_creados)} vehículos creados")
    return vehiculos_creados

def generar_viajes(db: Session, usuarios, conductores, vehiculos, cantidad: int = 50):
    """Genera viajes con datos realistas"""
    print(f"\n🚖 Generando {cantidad} viajes...")
    viajes_creados = []
    estados = ["pendiente", "en_curso", "completado", "completado", "completado"]  # Más completados
    
    # Generar viajes en los últimos 6 meses
    fecha_inicio = datetime.now() - timedelta(days=180)
    
    for i in range(cantidad):
        origen = random.choice(ORIGENES)
        destino = random.choice(DESTINOS)
        precio = generar_precio_viaje(origen, destino)
        
        # Fecha aleatoria en los últimos 6 meses
        dias_random = random.randint(0, 180)
        fecha_viaje = fecha_inicio + timedelta(
            days=dias_random,
            hours=random.randint(6, 22),  # Entre 6 AM y 10 PM
            minutes=random.randint(0, 59)
        )
        
        viaje = schemas.ViajeCrear(
            usuario_id=random.choice(usuarios).id,
            conductor_id=random.choice(conductores).id,
            vehiculo_id=random.choice(vehiculos).id,
            origen=origen,
            destino=destino,
            precio=precio,
            fecha=fecha_viaje,
            estado=random.choice(estados)
        )
        
        viaje_db = crud.crear_viaje(db, viaje)
        viajes_creados.append(viaje_db)
        
        if (i + 1) % 10 == 0:
            print(f"  ✓ {i + 1} viajes creados...")
    
    print(f"✅ {len(viajes_creados)} viajes creados")
    return viajes_creados

def generar_estadisticas(db: Session):
    """Muestra estadísticas de los datos generados"""
    print("\n" + "="*60)
    print("📊 ESTADÍSTICAS DE DATOS GENERADOS")
    print("="*60)
    
    usuarios = db.query(models.Usuario).all()
    conductores = db.query(models.Conductor).all()
    vehiculos = db.query(models.Vehiculo).all()
    viajes = db.query(models.Viaje).all()
    
    print(f"\n👥 Usuarios: {len(usuarios)}")
    print(f"   - Activos: {sum(1 for u in usuarios if u.activo)}")
    
    print(f"\n🏍️  Conductores: {len(conductores)}")
    print(f"   - Activos: {sum(1 for c in conductores if c.activo)}")
    
    print(f"\n🚗 Vehículos: {len(vehiculos)}")
    print(f"   - Activos: {sum(1 for v in vehiculos if v.activo)}")
    
    print(f"\n🚖 Viajes: {len(viajes)}")
    viajes_por_estado = {}
    for viaje in viajes:
        estado = viaje.estado or "pendiente"
        viajes_por_estado[estado] = viajes_por_estado.get(estado, 0) + 1
    
    for estado, cantidad in viajes_por_estado.items():
        print(f"   - {estado.capitalize()}: {cantidad}")
    
    ingresos_totales = sum(v.precio or 0 for v in viajes)
    print(f"\n💰 Ingresos Totales: ${ingresos_totales:,.0f} COP")
    print(f"💵 Ingreso Promedio por Viaje: ${ingresos_totales/len(viajes):,.0f} COP")
    
    print("\n" + "="*60)

def main():
    """Función principal"""
    print("="*60)
    print("🚖 GENERADOR DE DATOS MOCK - MOTOTAXI SUPATÁ")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Preguntar si desea limpiar la BD
        respuesta = input("\n⚠️  ¿Desea limpiar la base de datos? (s/n): ")
        if respuesta.lower() == 's':
            limpiar_base_datos(db)
        
        # Generar datos
        usuarios = generar_usuarios(db, cantidad=20)
        conductores = generar_conductores(db, cantidad=15)
        vehiculos = generar_vehiculos(db, cantidad=15)
        viajes = generar_viajes(db, usuarios, conductores, vehiculos, cantidad=80)
        
        # Mostrar estadísticas
        generar_estadisticas(db)
        
        print("\n✅ ¡Datos generados exitosamente!")
        print("🌐 Inicia el servidor con: uvicorn main:app --reload")
        print("📊 Visita: http://127.0.0.1:8000/dashboard")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()