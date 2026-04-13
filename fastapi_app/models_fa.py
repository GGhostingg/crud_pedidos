from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from fastapi_app.database import Base

class Usuario(Base):           # Tabla de usuarios FastAPI (para JWT)
    __tablename__ = 'api_usuarios'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default='user')  # 'admin' or 'user'

class Cliente(Base):           # Mismo nombre de tabla que Django: 'clientes'
    __tablename__ = 'clientes'
    id        = Column(Integer, primary_key=True)
    nombre    = Column(String(100))
    correo    = Column(String(100))
    direccion = Column(String(200))
    telefono  = Column(String(20))
    pedidos   = relationship('Pedido', back_populates='cliente')

class Producto(Base):
    __tablename__ = 'productos'
    id     = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    precio = Column(Float)
    stock  = Column(Integer)

class Pedido(Base):
    __tablename__ = 'pedidos'
    id         = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    usuario_id = Column(Integer, ForeignKey('auth_user.id'), nullable=True)
    fecha      = Column(DateTime, default=datetime.utcnow)
    estado     = Column(Enum('Pendiente','Enviado','Entregado','Anulado'), default='Pendiente')
    cliente    = relationship('Cliente', back_populates='pedidos')
    detalles   = relationship('DetallePedido', back_populates='pedido')

class DetallePedido(Base):
    __tablename__ = 'detalles_pedido'
    id          = Column(Integer, primary_key=True)
    pedido_id   = Column(Integer, ForeignKey('pedidos.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad    = Column(Integer)
    pedido      = relationship('Pedido', back_populates='detalles')
    producto    = relationship('Producto')

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio
