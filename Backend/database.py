import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
URL_BASE_DATOS = os.getenv("DATABASE_URL")

# Indicamos a PyMySQL que negocie una conexión SSL válida sin verificar certificado local
engine = create_engine(
    URL_BASE_DATOS,
    connect_args={"ssl": {}}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()