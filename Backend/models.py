from sqlalchemy import Column, Integer, String, Float, DateTime
from Backend.database import Base
import datetime

class Familiar(Base):
    __tablename__ = "familiares" 

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True)

class Tematica(Base):
    __tablename__ = "tematicas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True)

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    persona = Column(String(50))
    tema_tematica = Column(String(100))
    dinero_gastado = Column(Float)
    fecha = Column(DateTime, default=datetime.datetime.now)