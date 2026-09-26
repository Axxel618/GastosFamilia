from pydantic import BaseModel
from typing import Optional

class FamiliarCreate(BaseModel):
    nombre: str

class TematicaCreate(BaseModel):
    nombre: str

class GastoCreate(BaseModel):
    persona: str
    tema_tematica: str
    dinero_gastado: float
    comentario: Optional[str] = None