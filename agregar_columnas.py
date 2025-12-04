"""
Script para agregar la columna conductor_id a la tabla vehiculos
"""
from sqlalchemy import text
from database import engine

def agregar_columna_conductor_id():
    print("=" * 60)
    print("🔧 Agregando columna conductor_id a tabla vehiculos")
    print("=" * 60)
    
    try:
        with engine.connect() as connection:
            # Verificar si la columna ya existe
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='vehiculos' AND column_name='conductor_id'
            """))
            
            if result.fetchone():
                print("✅ La columna conductor_id ya existe")
                return
            
            print("\n📝 Agregando columna conductor_id...")
            connection.execute(text("""
                ALTER TABLE vehiculos ADD COLUMN conductor_id INTEGER;
            """))
            connection.commit()
            print("✅ Columna conductor_id agregada")
            
            print("\n🔗 Agregando foreign key...")
            connection.execute(text("""
                ALTER TABLE vehiculos 
                ADD CONSTRAINT fk_vehiculos_conductor 
                FOREIGN KEY (conductor_id) 
                REFERENCES conductores(id) 
                ON DELETE SET NULL;
            """))
            connection.commit()
            print("✅ Foreign key agregada")
            
            print("\n📊 Verificando estructura de la tabla...")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name='vehiculos'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Columnas en tabla vehiculos:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} (Nullable: {row[2]})")
            
            print("\n" + "=" * 60)
            print("✅ Proceso completado exitosamente")
            print("💡 Ahora puedes ejecutar: python generar_datos_mock.py")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Intenta ejecutar este SQL manualmente en tu base de datos:")
        print("""
        ALTER TABLE vehiculos ADD COLUMN conductor_id INTEGER;
        ALTER TABLE vehiculos ADD CONSTRAINT fk_vehiculos_conductor 
            FOREIGN KEY (conductor_id) REFERENCES conductores(id) ON DELETE SET NULL;
        """)

if __name__ == "__main__":
    agregar_columna_conductor_id()