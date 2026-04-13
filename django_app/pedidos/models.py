from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Cliente(models.Model):
    usuario   = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='cliente_perfil'
    )
    nombre    = models.CharField(max_length=100)
    correo    = models.EmailField(unique=True)
    direccion = models.CharField(max_length=200, blank=True)
    telefono  = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'clientes'       # Nombre real en MySQL
        verbose_name_plural = 'Clientes'


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock  = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'productos'


class Pedido(models.Model):
    ESTADOS = [
        ('Pendiente',  'Pendiente'),
        ('Enviado',    'Enviado'),
        ('Entregado',  'Entregado'),
        ('Anulado',    'Anulado'),
    ]
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name='pedidos'
    )
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='pedidos_usuario'
    )
    fecha  = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    def __str__(self):
        if self.usuario:
            return f'Pedido #{self.id} - {self.cliente.nombre} ({self.usuario.username})'
        return f'Pedido #{self.id} - {self.cliente.nombre}'

    class Meta:
        db_table = 'pedidos'


class DetallePedido(models.Model):
    pedido   = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

    class Meta:
        db_table = 'detalles_pedido'
