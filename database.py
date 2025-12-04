from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ✅ MEJOR PRÁCTICA: Usar variable de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ufrqizsynh7hw1lwkypl:TDIEkb5nDrOF8Ow4SVacVAicm8bjb8@bcjwxq3t9ckvbf5r82mu-postgresql.services.clever-cloud.com:50013/bcjwxq3t9ckvbf5r82mu"
)

# ✅ CONFIGURACIÓN CRÍTICA PARA CLEVER CLOUD
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"
    },
    pool_size=3,                    # ✅ Máximo 3 conexiones
    max_overflow=0,                 # ✅ NO crear conexiones adicionales
    pool_pre_ping=True,             # ✅ Verificar conexión antes de usar
    pool_recycle=1800,              # ✅ Reciclar cada 30 minutos
    pool_timeout=30,                # ✅ Timeout de 30 segundos
    echo=False
)

# Crear una sesión local para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir los modelos
Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Función para verificar conexión
def verificar_conexion():
    try:
        with engine.connect() as conn:
            print("✅ Conexión a PostgreSQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False