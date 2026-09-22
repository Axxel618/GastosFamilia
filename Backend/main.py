from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from Backend.database import engine, SessionLocal, Base
from Backend import models
from Backend.schemas import FamiliarCreate, GastoCreate, TematicaCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"mensaje": "¡El backend familiar de control de datos está funcionando! 🚀"}

# --- FAMILIARES ---
@app.get("/familiar/")
def obtener_familiares(db: Session = Depends(get_db)):
    familiares_db = db.query(models.Familiar).all()
    return {"familiares": [f.nombre for f in familiares_db]}

@app.get("/gastos/")
def obtener_gastos(db: Session = Depends(get_db)):
    gastos_db = db.query(models.Gasto).all()
    # Convertimos los objetos de la base de datos a diccionarios
    return [
        {
            "persona": g.persona, 
            "tema_tematica": g.tema_tematica, 
            "dinero_gastado": g.dinero_gastado, 
            "fecha": g.fecha
        } 
        for g in gastos_db
    ]
@app.post("/familiar/")
def crear_familiar(familiar: FamiliarCreate, db: Session = Depends(get_db)):
    familiar_existente = db.query(models.Familiar).filter(models.Familiar.nombre == familiar.nombre).first()
    if familiar_existente:
        raise HTTPException(status_code=400, detail="El familiar ya existe")
    
    nuevo_familiar = models.Familiar(nombre=familiar.nombre)
    db.add(nuevo_familiar)
    db.commit()
    return {"mensaje": f"Familiar {familiar.nombre} creado con éxito"}

# --- TEMÁTICAS ---
@app.get("/tematicas/")
def obtener_tematica(db: Session = Depends(get_db)):
    tematicas_db = db.query(models.Tematica).all()
    return {"tematicas": [t.nombre for t in tematicas_db]}

@app.post("/tematica/")
def crear_tematica(tematica: TematicaCreate, db: Session = Depends(get_db)):
    tematica_existente = db.query(models.Tematica).filter(models.Tematica.nombre == tematica.nombre).first()
    if tematica_existente:
         raise HTTPException(status_code=400, detail="La temática ya existe")
    
    nueva_tematica = models.Tematica(nombre=tematica.nombre)
    db.add(nueva_tematica)
    db.commit()
    return {"mensaje": f"Temática {tematica.nombre} creada con éxito"}

# --- GASTOS / DATOS ---
@app.post("/gasto/")
def registrar_gasto(gasto: GastoCreate, db: Session = Depends(get_db)):
    nuevo_gasto = models.Gasto(
        persona=gasto.persona,
        tema_tematica=gasto.tema_tematica,
        dinero_gastado=gasto.dinero_gastado
    )
    db.add(nuevo_gasto)
    db.commit()
    return {"mensaje": "Gasto registrado correctamente"}