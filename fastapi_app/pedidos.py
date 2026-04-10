@router.post('/', response_model=schemas.PedidoResponse, status_code=201)
def crear_pedido(
    datos: schemas.PedidoCreate,
    db: Session = Depends(get_db),
    _:  models.Usuario = Depends(auth.get_current_user)
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id==datos.cliente_id).first()
    if not cliente:
        raise HTTPException(404, 'Cliente no encontrado')

    pedido = models.Pedido(cliente_id=datos.cliente_id, estado=datos.estado)
    db.add(pedido)
    db.flush()  # Obtener ID sin hacer commit

    for det in datos.detalles:
        prod = db.query(models.Producto).filter(models.Producto.id==det.producto_id).first()
        if not prod:
            db.rollback()
            raise HTTPException(404, f'Producto {det.producto_id} no encontrado')
        if prod.stock < det.cantidad:
            db.rollback()
            raise HTTPException(400, f'Stock insuficiente para {prod.nombre}')
        prod.stock -= det.cantidad    # Reducir stock automáticamente
        db.add(models.DetallePedido(
            pedido_id=pedido.id, producto_id=det.producto_id, cantidad=det.cantidad
        ))
    db.commit()
    db.refresh(pedido)
    return pedido
