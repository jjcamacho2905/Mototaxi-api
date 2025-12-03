from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a PostgreSQL usando los datos de Clever Cloud
DATABASE_URL = "postgresql://ufrqizsynh7hw1lwkypl:TDIEkb5nDrOF8Ow4SVacVAicm8bjb8@bcjwxq3t9ckvbf5r82mu-postgresql.services.clever-cloud.com:50013/bcjwxq3t9ckvbf5r82mu"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})  # Habilitar SSL si es necesario

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

