from django.contrib import admin
from .models import Cliente, Producto, Pedido, DetallePedido

# Register your models here.

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'telefono')
    search_fields = ('nombre', 'correo')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'stock')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'usuario', 'fecha', 'estado')
    list_filter  = ('estado', 'usuario')

@admin.register(DetallePedido)
class DetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad')
