from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app import auth, models_fa as models, schemas
from fastapi_app.database import get_db

router = APIRouter(prefix='/api/productos', tags=['Productos'])

@router.get('/')
def listar(
    skip:  int = 0,
    limit: int = 10,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_user)
):
    total = db.query(models.Producto).count()
    productos = db.query(models.Producto).offset(skip).limit(limit).all()
    return {'total': total, 'datos': productos}

@router.post('/', response_model=schemas.ProductoResponse, status_code=201)
def crear(
    datos: schemas.ProductoCreate,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_admin)  # Solo admin
):
    nuevo = models.Producto(**datos.dict())
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return nuevo

@router.get('/{pid}', response_model=schemas.ProductoResponse)
def obtener(pid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_user)):
    p = db.query(models.Producto).filter(models.Producto.id==pid).first()
    if not p: raise HTTPException(404, 'Producto no encontrado')
    return p

@router.put('/{pid}', response_model=schemas.ProductoResponse)
def actualizar(
    pid:   int,
    datos: schemas.ProductoCreate,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_admin)  # Solo admin
):
    p = db.query(models.Producto).filter(models.Producto.id==pid).first()
    if not p: raise HTTPException(404, 'Producto no encontrado')
    for k, v in datos.dict().items(): setattr(p, k, v)
    db.commit(); db.refresh(p)
    return p

@router.delete('/{pid}', status_code=204)
def eliminar(pid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_admin)):
    p = db.query(models.Producto).filter(models.Producto.id==pid).first()
    if not p: raise HTTPException(404, 'Producto no encontrado')
    db.delete(p); db.commit()

@router.get('/public/')
def listar_publico(
    skip:  int = 0,
    limit: int = 10,
    db:    Session = Depends(get_db)
):
    total = db.query(models.Producto).count()
    productos = db.query(models.Producto).offset(skip).limit(limit).all()
    return {'total': total, 'datos': productos}

@router.get('/public/{pid}', response_model=schemas.ProductoResponse)
def obtener_publico(pid: int, db: Session=Depends(get_db)):
    p = db.query(models.Producto).filter(models.Producto.id==pid).first()
    if not p: raise HTTPException(404, 'Producto no encontrado')
    return p