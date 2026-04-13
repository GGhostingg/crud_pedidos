from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app import auth, models_fa as models, schemas
from fastapi_app.database import get_db

router = APIRouter(prefix='/api/pedidos', tags=['Pedidos'])

@router.get('/')
def listar(
    skip:  int = 0,
    limit: int = 10,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_user)
):
    total = db.query(models.Pedido).count()
    pedidos = db.query(models.Pedido).offset(skip).limit(limit).all()
    return {'total': total, 'datos': pedidos}

@router.post('/', response_model=schemas.PedidoResponse, status_code=201)
def crear(
    datos: schemas.PedidoCreate,
    db:    Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_current_user)
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id==datos.cliente_id).first()
    if not cliente:
        raise HTTPException(404, 'Cliente no encontrado')

    pedido = models.Pedido(
        cliente_id=datos.cliente_id,
        usuario_id=usuario.id,
        estado=datos.estado
    )
    db.add(pedido)
    db.flush()

    for det in datos.detalles:
        prod = db.query(models.Producto).filter(models.Producto.id==det.producto_id).first()
        if not prod:
            db.rollback()
            raise HTTPException(404, f'Producto {det.producto_id} no encontrado')
        if prod.stock < det.cantidad:
            db.rollback()
            raise HTTPException(400, f'Stock insuficiente para {prod.nombre}')
        prod.stock -= det.cantidad
        db.add(models.DetallePedido(
            pedido_id=pedido.id, producto_id=det.producto_id, cantidad=det.cantidad
        ))
    db.commit()
    db.refresh(pedido)
    return pedido

@router.get('/{pid}', response_model=schemas.PedidoResponse)
def obtener(pid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_user)):
    p = db.query(models.Pedido).filter(models.Pedido.id==pid).first()
    if not p: raise HTTPException(404, 'Pedido no encontrado')
    return p

@router.put('/{pid}', response_model=schemas.PedidoResponse)
def actualizar(
    pid:   int,
    datos: schemas.PedidoCreate,
    db:    Session = Depends(get_db),
    _:     models.Usuario = Depends(auth.get_current_admin)  # Solo admin puede actualizar
):
    p = db.query(models.Pedido).filter(models.Pedido.id==pid).first()
    if not p: raise HTTPException(404, 'Pedido no encontrado')
    # Lógica para actualizar, simplificada
    p.estado = datos.estado
    db.commit(); db.refresh(p)
    return p

@router.post('/{pid}/anular', response_model=schemas.PedidoResponse)
def anular(
    pid: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(auth.get_current_user)
):
    """Anula un pedido solo si está Pendiente y restaura el stock."""
    p = db.query(models.Pedido).filter(models.Pedido.id==pid).first()
    if not p:
        raise HTTPException(404, 'Pedido no encontrado')
    if p.estado != 'Pendiente':
        raise HTTPException(400, 'Solo se pueden anular pedidos en estado Pendiente')

    # Restaurar stock de cada detalle
    for detalle in p.detalles:
        prod = db.query(models.Producto).filter(models.Producto.id==detalle.producto_id).first()
        if prod:
            prod.stock += detalle.cantidad

    p.estado = 'Anulado'
    db.commit()
    db.refresh(p)
    return p

@router.delete('/{pid}', status_code=204)
def eliminar(pid: int, db: Session=Depends(get_db), _=Depends(auth.get_current_admin)):
    p = db.query(models.Pedido).filter(models.Pedido.id==pid).first()
    if not p: raise HTTPException(404, 'Pedido no encontrado')
    db.delete(p); db.commit()