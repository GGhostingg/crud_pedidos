from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EstadoPedido(str, Enum):
    pendiente  = 'Pendiente'
    enviado    = 'Enviado'
    entregado  = 'Entregado'
    anulado    = 'Anulado'

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
    is_staff: bool = False

class ClienteBase(BaseModel):
    nombre: str
    correo: EmailStr
    direccion: Optional[str] = None
    telefono:  Optional[str] = None

class ClienteCreate(ClienteBase): pass

class ClienteResponse(ClienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProductoBase(BaseModel):
    nombre: str
    precio: float
    stock:  int

    @field_validator('precio')
    @classmethod
    def precio_positivo(cls, v):
        if v <= 0: raise ValueError('El precio debe ser mayor que cero')
        return v

    @field_validator('stock')
    @classmethod
    def stock_no_negativo(cls, v):
        if v < 0: raise ValueError('El stock no puede ser negativo')
        return v

class ProductoCreate(ProductoBase): pass
class ProductoResponse(ProductoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DetallePedidoIn(BaseModel):
    producto_id: int
    cantidad: int

class DetallePedidoOut(DetallePedidoIn):
    id: int
    subtotal: float
    model_config = ConfigDict(from_attributes=True)

class PedidoCreate(BaseModel):
    cliente_id: int
    estado: EstadoPedido = EstadoPedido.pendiente
    detalles: List[DetallePedidoIn]

class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    usuario_id: Optional[int] = None
    fecha: datetime
    estado: str
    detalles: List[DetallePedidoOut] = []
    model_config = ConfigDict(from_attributes=True)
