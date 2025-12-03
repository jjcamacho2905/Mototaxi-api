from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATOS DE CLEVER CLOUD
DB_HOST = "bcjw...postgresql.services.clever-cloud.com"
DB_NAME = "bcjw...f5r82mu"
DB_USER = "ufrqizsynh7hwlwkypI"
DB_PASS = "TU_PASSWORD"
DB_PORT = "50013"

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

