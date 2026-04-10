from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EstadoPedido(str, Enum):
    pendiente  = 'Pendiente'
    enviado    = 'Enviado'
    entregado  = 'Entregado'

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class ClienteBase(BaseModel):
    nombre: str
    correo: EmailStr
    direccion: Optional[str] = None
    telefono:  Optional[str] = None

class ClienteCreate(ClienteBase): pass

class ClienteResponse(ClienteBase):
    id: int
    class Config: from_attributes = True

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock:  int

    @validator('precio')
    def precio_positivo(cls, v):
        if v <= 0: raise ValueError('El precio debe ser mayor que cero')
        return v

    @validator('stock')
    def stock_no_negativo(cls, v):
        if v < 0: raise ValueError('El stock no puede ser negativo')
        return v

class ProductoCreate(ProductoBase): pass
class ProductoResponse(ProductoBase):
    id: int
    class Config: from_attributes = True

class DetallePedidoIn(BaseModel):
    producto_id: int
    cantidad: int

class DetallePedidoOut(DetallePedidoIn):
    id: int
    subtotal: float
    class Config: from_attributes = True

class PedidoCreate(BaseModel):
    cliente_id: int
    estado: EstadoPedido = EstadoPedido.pendiente
    detalles: List[DetallePedidoIn]

class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime
    estado: str
    detalles: List[DetallePedidoOut] = []
    class Config: from_attributes = True
