"""
Script para generar datos mock realistas del proyecto Mototaxi Supatá
Ejecutar: python generar_datos_mock.py

✅ ACTUALIZADO: Compatible con las reglas de negocio implementadas
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
    """Genera un número de teléfono colombiano realista (10 dígitos)"""
    prefijos = ["310", "311", "312", "313", "314", "315", "316", "317", "318", "319", "320", "321", "322", "323", "324", "350"]
    prefijo = random.choice(prefijos)
    numero = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefijo}{numero}"

def generar_placa():
    """Genera una placa colombiana realista (ABC123)"""
    letras = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    return f"{letras}{numeros}"  # Sin guión para que pase validación

def generar_licencia():
    """Genera un número de licencia corto (1-6 caracteres como requiere la validación)"""
    # La validación permite de 1 a 6 caracteres
    longitud = random.randint(4, 6)
    return ''.join([str(random.randint(0, 9)) for _ in range(longitud)])

def generar_precio_viaje(origen, destino):
    """Genera un precio realista según la distancia (mínimo 1000, máximo 500000)"""
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
    """Elimina todos los datos existentes respetando las FK"""
    print("🗑️  Limpiando base de datos...")
    try:
        # Borrar en orden correcto (respetando foreign keys)
        viajes_borrados = db.query(models.Viaje).delete()
        vehiculos_borrados = db.query(models.Vehiculo).delete()
        conductores_borrados = db.query(models.Conductor).delete()
        usuarios_borrados = db.query(models.Usuario).delete()
        
        db.commit()
        
        print(f"✅ Limpieza completada:")
        print(f"   - {viajes_borrados} viajes eliminados")
        print(f"   - {vehiculos_borrados} vehículos eliminados")
        print(f"   - {conductores_borrados} conductores eliminados")
        print(f"   - {usuarios_borrados} usuarios eliminados")
    except Exception as e:
        print(f"❌ Error al limpiar: {e}")
        db.rollback()
        raise

def generar_usuarios(db: Session, cantidad: int = 20):
    """Genera usuarios con datos realistas"""
    print(f"\n👥 Generando {cantidad} usuarios...")
    usuarios_creados = []
    
    for i, nombre in enumerate(NOMBRES_USUARIOS[:cantidad], 1):
        try:
            # Crear usuario SIN contraseña (como lo hace el formulario HTML)
            usuario_db = models.Usuario(
                nombre=nombre.strip(),
                telefono=generar_telefono(),
                password_hash=None,  # Sin contraseña
                activo=True
            )
            db.add(usuario_db)
            db.commit()
            db.refresh(usuario_db)
            
            usuarios_creados.append(usuario_db)
            print(f"  ✓ Usuario {i}: {nombre}")
        except Exception as e:
            print(f"  ✗ Error creando usuario {nombre}: {e}")
            db.rollback()
    
    print(f"✅ {len(usuarios_creados)} usuarios creados")
    return usuarios_creados

def generar_conductores(db: Session, cantidad: int = 15):
    """Genera conductores con datos realistas"""
    print(f"\n🏍️  Generando {cantidad} conductores...")
    conductores_creados = []
    
    for i, nombre in enumerate(NOMBRES_CONDUCTORES[:cantidad], 1):
        try:
            licencia = generar_licencia()
            
            conductor_db = models.Conductor(
                nombre=nombre.strip(),
                licencia=licencia,
                activo=True
            )
            db.add(conductor_db)
            db.commit()
            db.refresh(conductor_db)
            
            conductores_creados.append(conductor_db)
            print(f"  ✓ Conductor {i}: {nombre} - Licencia: {licencia}")
        except Exception as e:
            print(f"  ✗ Error creando conductor {nombre}: {e}")
            db.rollback()
    
    print(f"✅ {len(conductores_creados)} conductores creados")
    return conductores_creados

def generar_vehiculos(db: Session, conductores, cantidad: int = 15):
    """Genera vehículos con datos realistas y los asigna a conductores"""
    print(f"\n🚗 Generando {cantidad} vehículos...")
    vehiculos_creados = []
    placas_usadas = set()
    
    for i in range(cantidad):
        try:
            # Generar placa única
            placa = generar_placa()
            intentos = 0
            while placa in placas_usadas and intentos < 100:
                placa = generar_placa()
                intentos += 1
            
            if intentos >= 100:
                print(f"  ⚠️  No se pudo generar placa única después de 100 intentos")
                continue
            
            placas_usadas.add(placa)
            
            # Asignar conductor aleatoriamente (algunos vehículos sin conductor)
            conductor_id = None
            if i < len(conductores):
                conductor_id = conductores[i].id
            
            vehiculo_db = models.Vehiculo(
                placa=placa,
                modelo=random.choice(MODELOS_VEHICULOS),
                conductor_id=conductor_id,
                activo=True
            )
            db.add(vehiculo_db)
            db.commit()
            db.refresh(vehiculo_db)
            
            vehiculos_creados.append(vehiculo_db)
            conductor_info = f" → Conductor: {conductores[i].nombre}" if conductor_id else ""
            print(f"  ✓ Vehículo {i+1}: {placa} - {vehiculo_db.modelo}{conductor_info}")
        except Exception as e:
            print(f"  ✗ Error creando vehículo: {e}")
            db.rollback()
    
    print(f"✅ {len(vehiculos_creados)} vehículos creados")
    return vehiculos_creados

def generar_viajes(db: Session, usuarios, conductores, vehiculos, cantidad: int = 50):
    """
    Genera viajes con datos realistas
    IMPORTANTE: Solo crea viajes COMPLETADOS para evitar conflictos con conductores ocupados
    """
    print(f"\n🚖 Generando {cantidad} viajes...")
    viajes_creados = []
    
    # Solo estados completados/cancelados para no bloquear conductores
    estados = ["completado", "completado", "completado", "cancelado"]
    
    # Generar viajes en los últimos 6 meses
    fecha_inicio = datetime.now() - timedelta(days=180)
    
    for i in range(cantidad):
        try:
            origen = random.choice(ORIGENES)
            destino = random.choice(DESTINOS)
            
            # Asegurar que origen y destino sean diferentes
            while origen.lower() == destino.lower():
                destino = random.choice(DESTINOS)
            
            precio = generar_precio_viaje(origen, destino)
            
            # Fecha aleatoria en los últimos 6 meses
            dias_random = random.randint(0, 180)
            fecha_viaje = fecha_inicio + timedelta(
                days=dias_random,
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            
            # Seleccionar conductor y vehículo
            conductor = random.choice(conductores)
            
            # Intentar usar un vehículo del conductor, si no tiene, usar cualquiera
            vehiculos_conductor = [v for v in vehiculos if v.conductor_id == conductor.id]
            if vehiculos_conductor:
                vehiculo = random.choice(vehiculos_conductor)
            else:
                vehiculo = random.choice(vehiculos)
            
            viaje_db = models.Viaje(
                usuario_id=random.choice(usuarios).id,
                conductor_id=conductor.id,
                vehiculo_id=vehiculo.id,
                origen=origen,
                destino=destino,
                precio=precio,
                fecha=fecha_viaje,
                estado=random.choice(estados),
                activo=True
            )
            
            db.add(viaje_db)
            db.commit()
            db.refresh(viaje_db)
            
            viajes_creados.append(viaje_db)
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ {i + 1} viajes creados...")
        except Exception as e:
            print(f"  ✗ Error creando viaje {i+1}: {e}")
            db.rollback()
    
    print(f"✅ {len(viajes_creados)} viajes creados")
    return viajes_creados

def generar_estadisticas(db: Session):
    """Muestra estadísticas de los datos generados"""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DE DATOS GENERADOS")
    print("="*70)
    
    usuarios = db.query(models.Usuario).all()
    conductores = db.query(models.Conductor).all()
    vehiculos = db.query(models.Vehiculo).all()
    viajes = db.query(models.Viaje).all()
    
    print(f"\n👥 Usuarios: {len(usuarios)}")
    print(f"   - Activos: {sum(1 for u in usuarios if u.activo)}")
    print(f"   - Inactivos: {sum(1 for u in usuarios if not u.activo)}")
    
    print(f"\n🏍️  Conductores: {len(conductores)}")
    print(f"   - Activos: {sum(1 for c in conductores if c.activo)}")
    print(f"   - Con vehículos: {sum(1 for c in conductores if any(v.conductor_id == c.id for v in vehiculos))}")
    
    print(f"\n🚗 Vehículos: {len(vehiculos)}")
    print(f"   - Activos: {sum(1 for v in vehiculos if v.activo)}")
    print(f"   - Con conductor asignado: {sum(1 for v in vehiculos if v.conductor_id is not None)}")
    print(f"   - Sin conductor: {sum(1 for v in vehiculos if v.conductor_id is None)}")
    
    print(f"\n🚖 Viajes: {len(viajes)}")
    viajes_por_estado = {}
    for viaje in viajes:
        estado = viaje.estado or "pendiente"
        viajes_por_estado[estado] = viajes_por_estado.get(estado, 0) + 1
    
    for estado, cantidad in viajes_por_estado.items():
        print(f"   - {estado.capitalize()}: {cantidad}")
    
    if viajes:
        ingresos_totales = sum(v.precio or 0 for v in viajes)
        print(f"\n💰 Ingresos Totales: ${ingresos_totales:,.0f} COP")
        print(f"💵 Ingreso Promedio por Viaje: ${ingresos_totales/len(viajes):,.0f} COP")
    
    print("\n" + "="*70)

def main():
    """Función principal"""
    print("="*70)
    print("🚖 GENERADOR DE DATOS MOCK - MOTOTAXI SUPATÁ")
    print("="*70)
    print("\n✅ Compatible con reglas de negocio actualizadas:")
    print("   - Licencias: 1-6 caracteres (pueden repetirse)")
    print("   - Placas: ABC123 (6 caracteres, únicas)")
    print("   - Teléfonos: 10 dígitos")
    print("   - Usuarios sin contraseña (como formulario HTML)")
    print("   - Vehículos asignados a conductores")
    print("   - Viajes solo completados/cancelados")
    
    db = SessionLocal()
    
    try:
        # Preguntar si desea limpiar la BD
        respuesta = input("\n⚠️  ¿Desea limpiar la base de datos? (s/n): ")
        if respuesta.lower() == 's':
            limpiar_base_datos(db)
        
        # Generar datos
        print("\n🔄 Iniciando generación de datos...")
        usuarios = generar_usuarios(db, cantidad=20)
        
        if not usuarios:
            print("❌ No se crearon usuarios. Abortando.")
            return
        
        conductores = generar_conductores(db, cantidad=15)
        
        if not conductores:
            print("❌ No se crearon conductores. Abortando.")
            return
        
        vehiculos = generar_vehiculos(db, conductores, cantidad=15)
        
        if not vehiculos:
            print("❌ No se crearon vehículos. Abortando.")
            return
        
        viajes = generar_viajes(db, usuarios, conductores, vehiculos, cantidad=50)
        
        # Mostrar estadísticas
        generar_estadisticas(db)
        
        print("\n✅ ¡Datos generados exitosamente!")
        print("🌐 Inicia el servidor con: uvicorn main:app --reload")
        print("📊 Visita: http://127.0.0.1:8000/dashboard")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        db.rollback()
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
        print("\n🔒 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()