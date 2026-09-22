from pydantic import BaseModel

class FamiliarCreate(BaseModel):
    nombre: str

class TematicaCreate(BaseModel):
    nombre: str

class GastoCreate(BaseModel):
    persona: str
    tema_tematica: str
    dinero_gastado: float