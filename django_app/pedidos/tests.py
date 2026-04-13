from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError

from pedidos.models import Cliente, Producto, Pedido, DetallePedido
from pedidos.forms import ProductoForm, ClienteForm


class ModelTests(TestCase):
    """Pruebas de modelos: creación, string representation y relaciones."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', email='test@example.com'
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user,
            nombre='Cliente Test',
            correo='cliente@test.com',
        )
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=25.50,
            stock=10,
        )

    def test_cliente_str(self):
        self.assertEqual(str(self.cliente), 'Cliente Test')

    def test_producto_str(self):
        self.assertEqual(str(self.producto), 'Producto Test')

    def test_pedido_str_con_usuario(self):
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            usuario=self.user,
            estado='Pendiente',
        )
        self.assertIn('testuser', str(pedido))
        self.assertIn('Cliente Test', str(pedido))

    def test_pedido_str_sin_usuario(self):
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            usuario=None,
            estado='Pendiente',
        )
        self.assertEqual(str(pedido), f'Pedido #{pedido.id} - Cliente Test')

    def test_detalle_subtotal(self):
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            usuario=self.user,
        )
        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=3,
        )
        self.assertEqual(detalle.subtotal, 76.50)  # 3 * 25.50

    def test_cliente_correo_unique(self):
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                nombre='Otro Cliente',
                correo='cliente@test.com',  # mismo correo
            )

    def test_pedido_estado_default(self):
        pedido = Pedido.objects.create(cliente=self.cliente)
        self.assertEqual(pedido.estado, 'Pendiente')

    def test_pedido_estados_validos(self):
        estados_validos = ['Pendiente', 'Enviado', 'Entregado', 'Anulado']
        for estado in estados_validos:
            pedido = Pedido.objects.create(cliente=self.cliente, estado=estado)
            self.assertEqual(pedido.estado, estado)


class FormTests(TestCase):
    """Pruebas de formularios: validación de campos."""

    def test_producto_form_precio_positiva(self):
        form = ProductoForm(data={
            'nombre': 'Test',
            'precio': -10,
            'stock': 5,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_producto_form_stock_no_negativo(self):
        form = ProductoForm(data={
            'nombre': 'Test',
            'precio': 10.00,
            'stock': -1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('stock', form.errors)

    def test_producto_form_valido(self):
        form = ProductoForm(data={
            'nombre': 'Producto Valido',
            'precio': 15.99,
            'stock': 20,
        })
        self.assertTrue(form.is_valid())

    def test_cliente_form_correo_valido(self):
        form = ClienteForm(data={
            'nombre': 'Cliente Valido',
            'correo': 'correo@example.com',
        })
        self.assertTrue(form.is_valid())

    def test_cliente_form_correo_invalido(self):
        form = ClienteForm(data={
            'nombre': 'Cliente Invalido',
            'correo': 'correo-invalido',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('correo', form.errors)


class ViewAccessTests(TestCase):
    """Pruebas de acceso a vistas: login requerido."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            correo='cliente@test.com',
        )
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=10.00,
            stock=5,
        )

    def test_login_required_producto_list(self):
        response = self.client.get(reverse('producto-list'))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_login_required_pedido_list(self):
        response = self.client.get(reverse('pedido-list'))
        self.assertEqual(response.status_code, 302)

    def test_login_required_cliente_list(self):
        response = self.client.get(reverse('cliente-list'))
        self.assertEqual(response.status_code, 302)

    def test_login_requiere_autenticacion(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
