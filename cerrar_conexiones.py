"""
Script de emergencia para cerrar conexiones PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# URL directa sin el ?sslmode=require al final
conn_params = {
    "host": "bcjwxq3t9ckvbf5r82mu-postgresql.services.clever-cloud.com",
    "port": 50013,
    "database": "bcjwxq3t9ckvbf5r82mu",
    "user": "ufrqizsynh7hw1lwkypl",
    "password": "TDIEkb5nDrOF8Ow4SVacVAicm8bjb8",
    "sslmode": "require"
}

try:
    print("🔌 Intentando conectar a PostgreSQL...")
    conn = psycopg2.connect(**conn_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Obtener nombre de BD
    cursor.execute("SELECT current_database();")
    dbname = cursor.fetchone()[0]
    print(f"✅ Conectado a: {dbname}")
    
    # Ver conexiones actuales
    cursor.execute("""
        SELECT COUNT(*) FROM pg_stat_activity 
        WHERE datname = %s;
    """, (dbname,))
    total = cursor.fetchone()[0]
    print(f"📈 Conexiones activas antes: {total}")
    
    # Cerrar todas menos la actual
    print("🗑️ Cerrando todas las conexiones...")
    cursor.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s AND pid <> pg_backend_pid();
    """, (dbname,))
    
    # Verificar conexiones después
    cursor.execute("""
        SELECT COUNT(*) FROM pg_stat_activity 
        WHERE datname = %s;
    """, (dbname,))
    total_despues = cursor.fetchone()[0]
    print(f"📉 Conexiones activas después: {total_despues}")
    
    print("\n✅ Conexiones cerradas exitosamente")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("💡 Ahora ejecuta:")
    print("   python inicializar_bd.py")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error al cerrar conexiones: {e}")
    print("\n🔧 SOLUCIÓN ALTERNATIVA:")
    print("   1. Ve a Clever Cloud dashboard")
    print("   2. Busca tu base de datos PostgreSQL")
    print("   3. Reinicia la base de datos desde el panel")
    print("   4. Espera 2 minutos")
    print("   5. Vuelve a intentar")