from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi_app import auth, models_fa as models, schemas
from fastapi_app.database import get_db

router = APIRouter(prefix='/api/clientes', tags=['Clientes'])

@router.get('/')
def listar(
    skip:  int = Query(0,  ge=0),
    limit: int = Query(10, ge=1, le=100),
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_user)
):
    total    = db.query(models.Cliente).count()
    clientes = db.query(models.Cliente).offset(skip).limit(limit).all()
    return {'total': total, 'pagina': skip//limit+1, 'por_pagina': limit, 'datos': clientes}

@router.post('/', response_model=schemas.ClienteResponse, status_code=201)
def crear(
    datos: schemas.ClienteCreate,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_user)
):
    if db.query(models.Cliente).filter(models.Cliente.correo==datos.correo).first():
        raise HTTPException(400, 'Correo ya registrado')
    nuevo = models.Cliente(**datos.dict())
    db.add(nuevo); db.commit(); db.refresh(nuevo)
    return nuevo

@router.get('/{cid}', response_model=schemas.ClienteResponse)
def obtener(cid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_user)):
    c = db.query(models.Cliente).filter(models.Cliente.id==cid).first()
    if not c: raise HTTPException(404, 'Cliente no encontrado')
    return c

@router.put('/{cid}', response_model=schemas.ClienteResponse)
def actualizar(
    cid:   int,
    datos: schemas.ClienteCreate,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_user)
):
    c = db.query(models.Cliente).filter(models.Cliente.id==cid).first()
    if not c: raise HTTPException(404, 'Cliente no encontrado')
    for k, v in datos.dict().items(): setattr(c, k, v)
    db.commit(); db.refresh(c)
    return c

@router.delete('/{cid}', status_code=204)
def eliminar(cid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_user)):
    c = db.query(models.Cliente).filter(models.Cliente.id==cid).first()
    if not c: raise HTTPException(404, 'Cliente no encontrado')
    db.delete(c); db.commit()
